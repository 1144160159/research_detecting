## Hardware support
All experiments were conducted using Python 3.8, PyTorch 1.10, and CUDA version 11.3, and were trained on a server 
equipped with an Intel(R) Xeon(R) Platinum 8255C CPU and NVIDIA RTX 3090 GPU.


## Installation

Install the dependency using the following command:

```bash
pip install -r requirements.txt
```

* torch
* scipy>=0.19.0
* numpy>=1.12.1
* pandas>=0.19.2
* pyyaml
* statsmodels
* tensorflow>=1.3.0
* tables
* future


## Data Preparation

Run the following commands to generate train/test/val dataset at  `data/{swat,wadi,smap,msl}/{train,val,test}.npz`.

```bash

# Create data directories
mkdir -p data/{swat,wadi,smap,msl}

# msl
python -m scripts.generate_msl_dataset 

# swat
python -m scripts.generate_swat_dataset 

# wadi
python -m scripts.generate_wadi_dataset 

# smap
python -m scripts.generate_smap_dataset 
```

## Train Model

When you train the model, you can run:

```bash
python train.py 
```

Hyperparameters can be modified in the `swat.yaml` 、 `wadi.yaml` files、`smap.yaml` filesand `msl.yaml` files.

## Design your own model

You can directly modify the model in the "model/pytorch/model.py" file.

## Citation

If you use this repository, e.g., the code and the datasets, in your research, please cite the following paper:
```
@article{shang2021discrete,
  title={Discrete Graph Structure Learning for Forecasting Multiple Time Series},
  author={Shang, Chao and Chen, Jie and Bi, Jinbo},
  journal={arXiv preprint arXiv:2101.06861},
  year={2021}
}
```

## Acknowledgments

[DCRNN-PyTorch](https://github.com/chnsh/DCRNN_PyTorch), [GCN](https://github.com/tkipf/gcn), [NRI](https://github.com/ethanfetaya/NRI) and [LDS-GNN](https://github.com/lucfra/LDS-GNN).
