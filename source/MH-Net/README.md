
# MH-Net

Official implementation of the AAAI'25 Main Technical Track Paper: Revolutionizing Encrypted Traffic Classification with MH-Net: A Multi-View Heterogeneous Graph Model

<p align="center">
    <a href="https://arxiv.org/abs/2501.03279">
        <img alt="Build" src="https://img.shields.io/badge/arXiv-2501.03279-red?logo=arxiv">
    </a>
    <a href="https://github.com/ViktorAxelsen/MH-Net/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/LICENSE-MIT-green">
    </a>
    <br>
    <a href="https://github.com/ViktorAxelsen/MH-Net">
        <img alt="Build" src="https://img.shields.io/github/stars/ViktorAxelsen/MH-Net">
    </a>
    <a href="https://github.com/ViktorAxelsen/MH-Net">
        <img alt="Build" src="https://img.shields.io/github/forks/ViktorAxelsen/MH-Net">
    </a>
    <a href="https://github.com/ViktorAxelsen/MH-Net">
        <img alt="Build" src="https://img.shields.io/github/issues/ViktorAxelsen/MH-Net">
    </a>
</p>


![Method](./figures/MH-Net.png)



## Environment Setup

```bash
# python==3.8
pip install torch==1.10.1+cu113 torchvision==0.11.2+cu113 torchaudio==0.10.1 -f https://download.pytorch.org/whl/cu113/torch_stable.html
pip install dgl==1.0.0+cu113 -f https://data.dgl.ai/wheels/cu113/repo.html
pip install scikit-learn
pip install scapy
```

## Pre-processing

The pre-processing of MH-Net is similar with [TFE-GNN](https://github.com/ViktorAxelsen/TFE-GNN). You can optionally skip the pre-processing section.

### Convert .pcap to .npz Files

To facilitate subsequent processing, we extract the information of the .pcap file into the .npz file.

You may refer to **config.py** and customize your own .pcap path in **DIR_PATH_DICT**. Then, run the following commands to start converting.

```bash
# ISCX-VPN
python pcap2npy.py --dataset iscx-vpn
# ISCX-NonVPN
python pcap2npy.py --dataset iscx-nonvpn
# ISCX-TOR
python pcap2npy.py --dataset iscx-tor
# ISCX-NonTOR
python pcap2npy.py --dataset iscx-nontor
# CIC-Iot
python pcap2npy.py --dataset ciciot
```

### Construct Multi-View Heterogeneous Traffic Graphs

Before running following commands,  you may refer to **config.py** and customize all your own file paths. Then, run the following commands to start constructing.  In addition, we only give the full path of the ciciot dataset as a reference, you can modify others by yourself.

You can specify the "transform_length" to generate Heterogeneous Traffic Graphs with different bit lengths. 

$Note$: We use 8-bit as a baseline and convert 8-bit to other bits for the traffic graph. 

```bash
# ISCX-VPN
python preprocess.py --dataset iscx-vpn --transform_length 4
# ISCX-NonVPN
python preprocess.py --dataset iscx-nonvpn --transform_length 4
# ISCX-TOR
python preprocess.py --dataset iscx-tor --transform_length 4
# ISCX-NonTOR
python preprocess.py --dataset iscx-nontor --transform_length 4
# CIC-IoT
python preprocess.py --dataset ciciot --transform_length 4
```

## Training

You can run following commands to start training.

```bash
# ISCX-VPN
CUDA_VISIBLE_DEVICES="0" python train_new.py --dataset iscx-vpn --prefix exp_train --coe 0.5 --coe_graph 1.0 --seq_aug_ratio 0.6 --drop_edge_ratio 0.05 --drop_node_ratio 0.1 --K 15 --hp_ratio 0.5 --tau 0.07 --gtau 0.07
# ISCX-NonVPN
CUDA_VISIBLE_DEVICES="0" python train_new.py --dataset iscx-nonvpn --prefix exp_train --coe 0.8 --coe_graph 0.4 --seq_aug_ratio 0.6 --drop_edge_ratio 0.05 --drop_node_ratio 0.1 --K 15 --hp_ratio 0.5 --tau 0.07 --gtau 0.07
# ISCX-TOR
CUDA_VISIBLE_DEVICES="0" python train_new.py --dataset iscx-tor --prefix exp_train --coe 1.0 --coe_graph 0.4 --seq_aug_ratio 0.6 --drop_edge_ratio 0.05 --drop_node_ratio 0.1 --K 15 --hp_ratio 0.5 --tau 0.07 --gtau 0.07
# ISCX-NonTOR
CUDA_VISIBLE_DEVICES="0" python train_new.py --dataset iscx-nontor --prefix exp_train --coe 1.0 --coe_graph 0.6 --seq_aug_ratio 0.6 --drop_edge_ratio 0.05 --drop_node_ratio 0.1 --K 15 --hp_ratio 0.5 --tau 0.07 --gtau 0.07
#CIC-IoT
CUDA_VISIBLE_DEVICES="0" python train_new.py --dataset ciciot --prefix exp_train --coe 1.0 --coe_graph 0.6 --seq_aug_ratio 0.6 --drop_edge_ratio 0.05 --drop_node_ratio 0.1 --K 15 --hp_ratio 0.5 --tau 0.07 --gtau 0.07
```

## Evaluation

You can run following commands to start evaluation.

```bash
# ISCX-VPN
CUDA_VISIBLE_DEVICES="0" python test_new.py --dataset iscx-vpn --prefix exp_train
# ISCX-NonVPN
CUDA_VISIBLE_DEVICES="0" python test_new.py --dataset iscx-nonvpn --prefix exp_train
# ISCX-TOR
CUDA_VISIBLE_DEVICES="0" python test_new.py --dataset iscx-tor --prefix exp_train
# ISCX-NonTOR
CUDA_VISIBLE_DEVICES="0" python test_new.py --dataset iscx-nontor --prefix exp_train
# CIC-IoT
CUDA_VISIBLE_DEVICES="0" python test_new.py --dataset ciciot --prefix exp_train
```





## Citation

```bibtex
@article{MH-Net,
  title={Revolutionizing Encrypted Traffic Classification with MH-Net: A Multi-View Heterogeneous Graph Model},
  author={Haozhen Zhang and Haodong Yue and Xi Xiao and Le Yu and Qing Li and Zhen Ling and Ye Zhang},
  journal={arXiv preprint arXiv:2501.03279},
  year={2025}
}
```
