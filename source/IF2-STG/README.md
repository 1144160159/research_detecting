# IF2-STG

## Code Structure
This repository contains the code for the paper “Enhancing Intrusion Detection via Interpretable Inter-Flow Spatio-Temporal Graphs and Intra-Flow Features”. The implementation is divided into two main stages: Data Preprocessing and Model Training.


## Usage

### 1. Data Preprocessing
Run the scripts in `data_process` in order:
- `01-pcap2session.py`: Processes raw PCAP files to split network traffic into individual sessions/flows.
- `02-feaExtract.py`: Extracts intra-flow raw bytes from the split flows, and constructs the Inter-flow Spatio-Temporal relationship Graph (ISTG).


### 2. Model Training
Execute the training script directly:
- Run `train.py` to start the model training process.
