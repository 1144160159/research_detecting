# Argus

## Project Structure
- `CICIDD/` - Code for CICIDD dataset
- `MalReal/` - Code for MalReal dataset  
- `myutil.py` - Utility functions
- `dataconfig_ctu.py` - Configuration for MalReal dataset
- `dataconfig_ids2018.py` - Configuration for CICIDD dataset
- `dataset_address` - Dataset storage address

## Usage
For each dataset folder, execute the modules in numerical order:
1. Model training
2. Classification and drift detection  
3. Drift identification
4. Model adaptation

## Notes
- Update dataset paths in configuration files before running
- Execute modules sequentially as each step depends on previous outputs
