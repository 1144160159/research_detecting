# CellShift

A utility to transduce Tor cell traces observed in the exit relay position
into traces that represent observation from a different vantage point.

> [!WARNING]
> The state of this code is `experimental` and offered without any promise of
> support. Use at your own risk.

## What is this?

CellShift can be used to transduce exit traces to entry traces, and can improve
our evaluation of real-world website fingerprinting when applied to the GTT23
dataset of cell traces collected from real-world Tor exit relays.

## What is GT23?

The GTT23 dataset contains network metadata of encrypted traffic measured from
exit relays in the Tor network over a 13-week measurement period in 2023. The
metadata is suitable for analyzing and evaluating website fingerprinting attacks
and defenses.

The dataset is available here:
https://doi.org/10.5281/zenodo.10620519
 
## How to install CellShift

You can install manually or use a container.

### Manual installation

Dependencies (tested on `debian:12-slim`)

    # baseline tools (cmake is needed to build some Rust crates)
    apt install -y clang curl cmake git xz-utils zstd
    # hdf5 support
    apt install -y libhdf5-dev hdf5-filter-plugin hdf5-filter-plugin-blosc-serial
    # Rust build tools
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

Easy install

    cargo install --git https://github.com/robgjansen/cellshift.git

### Container-based installation

If you prefer to use [Docker](https://www.docker.com)

    docker build -t cellshift -f Dockerfile .
    docker run -it cellshift

If you prefer to use [Apptainer](https://apptainer.org)

    apptainer build cellshift.sif apptainer.def
    apptainer shell --no-home cellshift.sif

## How to use CellShift

> [!NOTE]  
> These instructions assume you have downloaded the gtt23.hdf5 file linked above.

> [!TIP]
> Cell trace datasets can consume _a lot_ of storage space. If you are low on
> space, use the `--compress` option to reduce storage cost at the expense of
> much greater processing times.

Run `TraceMorph` to produce 10x augmented training traces from GTT23 week 1 exit traces with >= 1000 cells

    cellshift morph --help
    cellshift morph \
        --time-unit week \
        --time-vals 1 \
        --min-length 1000 \
        --seed 654321 \
        gtt23.hdf5 \
        gtt23_week1_entry_augmented10.hdf5 \
        10

Run `TraceMove` to produce testing entry traces from GTT23 weeks 2-6 exit traces with >= 1000 cells

    cellshift move --help
    cellshift move \
        --time-unit week \
        --time-vals 2,3,4,5,6 \
        --min-length 1000 \
        gtt23.hdf5 \
        gtt23_weeks23456_entry.hdf5

Then, you can then train WF classifiers on `gtt23_week1_entry_augmented.hdf5` and test on `gtt23_weeks23456_entry.hdf5`.

## Creating your own cell trace transducers or augmenters

To create your own transduction or augmentation methods using CellShift, add
cellshift as a dependency in your Rust project:

    cargo add --git https://github.com/robgjansen/cellshift.git cellshift

That will give you access to CellShift's core RTT estimation and shifting
functions (in the `src/lib` subdirectory).

## More information

You can learn more about how CellShift works in our academic research paper:

> CellShift: RTT-Aware Trace Transduction for Real-World Website Fingerprinting  
> by Rob Jansen  
> in the Network and Distributed System Security Symposium, 2026.

If you find CellShift useful, please cite our paper:

```bibtex
@inproceedings{cellshift-ndss2026,
  title = {CellShift: RTT-Aware Trace Transduction for Real-World Website Fingerprinting},
  author = {Rob Jansen},
  booktitle = {Network and Distributed System Security Symposium},
  year = {2026},
}
```
