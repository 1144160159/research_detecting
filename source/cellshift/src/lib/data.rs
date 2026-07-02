use std::collections::HashSet;
use std::marker::PhantomData;
use std::num::NonZeroUsize;
use std::ops::Range;
use std::{iter::StepBy, path::PathBuf};

use gtt23::{CircuitIndex, IndexArrayEntry};
use hdf5::{Dataset, File, H5Type};
use ndarray::{self, Array1, ArrayView};

pub struct DatasetReader<T: H5Type> {
    phantom: PhantomData<T>,
    file: File,
    dataset: Dataset,
}

impl<T: H5Type> DatasetReader<T> {
    pub fn new(file_path: &PathBuf) -> anyhow::Result<Self> {
        let file = hdf5::File::open(file_path)?;
        Ok(Self {
            phantom: PhantomData,
            dataset: file.dataset("circuits")?,
            file,
        })
    }

    pub fn close(self) -> anyhow::Result<()> {
        Ok(self.file.close()?)
    }

    pub fn iter(
        &self,
        slice_len: NonZeroUsize,
        filter_min_len: Option<u16>,
        filter_days: Option<Vec<u8>>,
    ) -> anyhow::Result<DatasetSliceIterator<T>> {
        Ok(DatasetSliceIterator::new(
            &self.dataset,
            slice_len,
            self.select_filtered_indices(filter_min_len, filter_days)?,
        ))
    }

    fn select_filtered_indices(
        &self,
        min_len_filter: Option<u16>,
        days_filter: Option<Vec<u8>>,
    ) -> anyhow::Result<Option<Vec<usize>>> {
        log::info!(
            "Selecting filtered circuit indices from {:?}",
            self.file.filename()
        );

        let mut indices: Vec<usize> =
            if let (Some(min_len), Some(days)) = (min_len_filter, &days_filter) {
                let len_indices = self.select_indices_with_len_filter(min_len)?;
                let days_indices = self.select_indices_with_days_filter(days)?;
                len_indices
                    .intersection(&days_indices)
                    .map(|i| *i as usize)
                    .collect()
            } else if let Some(min_len) = min_len_filter {
                self.select_indices_with_len_filter(min_len)?
                    .iter()
                    .map(|i| *i as usize)
                    .collect()
            } else if let Some(days) = &days_filter {
                self.select_indices_with_days_filter(days)?
                    .iter()
                    .map(|i| *i as usize)
                    .collect()
            } else {
                // There is no filter.
                log::info!("Selected {} circuit indices", self.dataset.size());
                return Ok(None);
            };

        indices.sort();
        log::info!("Selected {} circuit indices", indices.len());
        Ok(Some(indices))
    }

    fn select_indices_with_len_filter(
        &self,
        min_len: u16,
    ) -> anyhow::Result<HashSet<CircuitIndex>> {
        let in_ds = self.file.dataset("/index/len")?;
        log::info!("Scanning {} entries in /index/len", in_ds.size());

        let entries: Array1<IndexArrayEntry<u16>> = in_ds.read_1d()?;
        let mut buffer = HashSet::<CircuitIndex>::new();

        for entry in entries {
            let trace_len = entry.value;
            if trace_len >= min_len {
                buffer.extend(entry.indexarr.iter());
            }
        }

        log::info!(
            "Found {} total indices of circuits with length >= {}",
            buffer.len(),
            min_len
        );
        Ok(buffer)
    }

    fn select_indices_with_days_filter(
        &self,
        days: &Vec<u8>,
    ) -> anyhow::Result<HashSet<CircuitIndex>> {
        let in_ds = self.file.dataset("/index/day")?;
        log::info!("Scanning {} entries in /index/day", in_ds.size());

        let entries: Array1<IndexArrayEntry<u8>> = in_ds.read_1d()?;
        let mut buffer = HashSet::<CircuitIndex>::new();

        for entry in entries {
            let day = entry.value;
            if days.is_empty() || days.contains(&day) {
                buffer.extend(entry.indexarr.iter());
            }
        }

        log::info!(
            "Found {} total indices of circuits from selected days {:?}",
            buffer.len(),
            days
        );
        Ok(buffer)
    }
}

pub struct DatasetSliceIterator<'a, T: H5Type> {
    phantom: PhantomData<T>,
    dataset: &'a Dataset,
    indices_filter: Option<Vec<usize>>,
    slice_len: NonZeroUsize,
    slice_begin_iter: StepBy<Range<usize>>,
}

impl<'a, T: H5Type> DatasetSliceIterator<'a, T> {
    fn new(
        dataset: &'a Dataset,
        slice_len: NonZeroUsize,
        indices_filter: Option<Vec<usize>>,
    ) -> Self {
        let end = indices_filter.as_ref().map_or(dataset.size(), |x| x.len());
        DatasetSliceIterator {
            phantom: PhantomData,
            dataset,
            slice_begin_iter: (0..end).step_by(slice_len.into()),
            slice_len,
            indices_filter,
        }
    }

    /// Returns the sum of the lengths of the slices that remain to be iterated.
    pub fn size(&self) -> usize {
        let n_iter_completed = self.total_len().checked_sub(self.len()).unwrap();
        let n_size_completed = n_iter_completed.checked_mul(self.slice_len.into()).unwrap();
        // Saturating sub ensures that we never return more than the total_size.
        // This handles the case where the last slice is not a full slice.
        self.total_size().saturating_sub(n_size_completed)
    }

    /// Returns the sum of the lengths of all slices in the selected dataset.
    pub fn total_size(&self) -> usize {
        if let Some(indices) = &self.indices_filter {
            indices.len()
        } else {
            self.dataset.size()
        }
    }

    /// Returns the total number of all slices in the selected dataset.
    pub fn total_len(&self) -> usize {
        self.total_size().div_ceil(self.slice_len.into())
    }
}

impl<'a, T: H5Type> ExactSizeIterator for DatasetSliceIterator<'a, T> {
    /// Returns the remaining number of slices to be iterated.
    fn len(&self) -> usize {
        self.slice_begin_iter.len()
    }
}

impl<'a, T: H5Type> Iterator for DatasetSliceIterator<'a, T> {
    type Item = Array1<T>;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(begin) = self.slice_begin_iter.next() {
            // If there is no filter then we're iterating the entire dataset.
            let end = begin.checked_add(self.slice_len.into()).unwrap();
            let end = std::cmp::min(end, self.total_size());

            // Read the slice, use the filter if we have one.
            let result = if let Some(indices) = &self.indices_filter {
                self.dataset.read_slice(&indices[begin..end])
            } else {
                self.dataset.read_slice(ndarray::s![begin..end])
            };

            // Unfortunate that we have to crash here.
            Some(result.expect("Error reading dataset slice from database"))
        } else {
            None
        }
    }
}

pub struct DatasetWriter<T: H5Type> {
    phantom: PhantomData<T>,
    file: File,
    dataset: Dataset,
    write_cursor: usize,
}

impl<T: H5Type> DatasetWriter<T> {
    pub fn new(file_path: &PathBuf, size: usize, compress: bool) -> anyhow::Result<Self> {
        // Make a dataset with the known size.
        let file = hdf5::File::create(file_path)?;

        let mut builder = file.new_dataset_builder().chunk(25);
        if compress {
            log::info!("Zstd compression enabled in dataset writer");
            builder = builder.blosc_zstd(9, false); // level 9, no shuffle
        } else {
            log::info!("Compression is disabled in dataset writer");
        }
        let dataset = builder.empty::<T>().shape(size).create("circuits")?;

        assert_eq!(dataset.size(), size);

        Ok(Self {
            phantom: PhantomData,
            dataset,
            file,
            write_cursor: 0,
        })
    }

    /// Converts the vector to an array, and then calls `write_arr()`
    pub fn write_vec(&mut self, slice: Vec<T>) -> anyhow::Result<(usize, usize)> {
        self.write_arr(Array1::from_vec(slice))
    }

    /// Returns the number of elements of `T` that were written, and the
    /// remaining space for writing additional elements of `T`.
    pub fn write_arr(&mut self, arr: Array1<T>) -> anyhow::Result<(usize, usize)> {
        let begin = self.write_cursor;
        let end = std::cmp::min(begin + arr.len(), self.dataset.size());
        assert!(begin <= end);

        // Write the full slice for performance.
        self.dataset.write_slice(&arr, ndarray::s![begin..end])?;
        let write_len = end.checked_sub(begin).unwrap();

        self.write_cursor = end;
        let space = self.dataset.size().saturating_sub(end);

        Ok((write_len, space))
    }

    pub fn truncate_and_close(self) -> anyhow::Result<usize> {
        if self.write_cursor < self.dataset.size() {
            self.dataset.resize(self.write_cursor)?;
        }
        let size = self.dataset.size();
        self.file.close()?;
        Ok(size)
    }
}

pub fn write_index<'d, A, T, D>(file_path: &PathBuf, name: &str, data: A) -> anyhow::Result<()>
where
    A: Into<ArrayView<'d, T, D>>,
    T: H5Type,
    D: ndarray::Dimension,
{
    let file = File::open_rw(file_path)?;

    if file.dataset(name).is_ok() {
        // Note this unlinks but does not reclaim its storage space.
        file.unlink(name)?;
    }

    file.new_dataset_builder().with_data(data).create(name)?;

    file.close()?;
    Ok(())
}
