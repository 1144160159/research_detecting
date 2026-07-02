use std::{collections::HashMap, num::NonZeroUsize};

use hdf5::{
    H5Type,
    types::{FixedAscii, VarLenArray},
};
use ndarray::{self, Array1};

use gtt23::{AugmentedCircuit, CircuitIndex, IndexArrayEntry, IndexEntry};

use crate::{cli::IndexArgs, util};
use cellshift::data::{DatasetReader, write_index};

pub fn run_index(args: &IndexArgs) -> anyhow::Result<()> {
    log::info!("Writing database index");

    let mut ci_uuid = HashMap::<FixedAscii<32>, Vec<CircuitIndex>>::new();
    let mut ci_uuid_gtt23 = HashMap::<FixedAscii<32>, Vec<CircuitIndex>>::new();
    let mut ci_aug_index = HashMap::<u16, Vec<CircuitIndex>>::new();
    let mut ci_len = HashMap::<u16, Vec<CircuitIndex>>::new();

    // Read the entire dataset to compute the index.
    {
        let db: DatasetReader<AugmentedCircuit> = DatasetReader::new(&args.input)?;

        let step = 1_000; // multiple of chunk size
        let slice_iter = db.iter(NonZeroUsize::new(step).unwrap(), None, None)?;
        let n_circuits = slice_iter.total_size();

        let pb = util::pb_new(n_circuits, "Computing index".to_string());
        pb.tick();

        // Read from dataset in batches for better performance.
        let mut index: CircuitIndex = 0;
        for slice in slice_iter {
            for circuit in slice.iter() {
                ci_uuid.entry(circuit.uuid).or_default().push(index);
                ci_uuid_gtt23
                    .entry(circuit.uuid_gtt23)
                    .or_default()
                    .push(index);
                ci_aug_index
                    .entry(circuit.aug_index)
                    .or_default()
                    .push(index);
                ci_len.entry(circuit.len).or_default().push(index);
                index = index.checked_add(1).unwrap();
            }

            pb.inc(slice.len() as u64);
        }

        pb.finish();
        db.close()?;
    }

    // Write each index into the hdf5 database.

    let mut index = create_index_entries(ci_uuid, "uuid")?;
    index.sort_by_key(|v| v.value.to_string());
    write_index(&args.input, "/index/uuid", &Array1::from_vec(index))?;

    let mut index = create_index_arr_entries(ci_uuid_gtt23, "uuid_gtt23")?;
    index.sort_by_key(|v| v.value.to_string());
    write_index(&args.input, "/index/uuid_gtt23", &Array1::from_vec(index))?;

    let mut index = create_index_arr_entries(ci_aug_index, "aug_index")?;
    index.sort_by_key(|v| v.value);
    write_index(&args.input, "/index/aug_index", &Array1::from_vec(index))?;

    let mut index = create_index_arr_entries(ci_len, "len")?;
    index.sort_by_key(|v| v.value);
    write_index(&args.input, "/index/len", &Array1::from_vec(index))?;

    Ok(())
}

fn create_index_entries<T>(
    index_map: HashMap<T, Vec<CircuitIndex>>,
    name: &str,
) -> anyhow::Result<Vec<IndexEntry<T>>>
where
    T: H5Type,
{
    Ok(create_index_arr_entries(index_map, name)?
        .into_iter()
        .map(|ent| IndexEntry {
            value: ent.value,
            index: *ent.indexarr.first().unwrap(),
        })
        .collect())
}

fn create_index_arr_entries<T>(
    index_map: HashMap<T, Vec<CircuitIndex>>,
    name: &str,
) -> anyhow::Result<Vec<IndexArrayEntry<T>>>
where
    T: H5Type,
{
    let mut index = Vec::new();
    let pb = util::pb_new(index_map.len(), format!("Preparing {name} index"));

    for (value, mut indices) in index_map.into_iter() {
        indices.sort();
        let indexarr = VarLenArray::from_slice(&indices);
        index.push(IndexArrayEntry { value, indexarr });
        pb.inc(1);
    }

    pb.finish();
    Ok(index)
}
