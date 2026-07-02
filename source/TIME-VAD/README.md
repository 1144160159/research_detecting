# TIME-VAD: Text-Informed Magnitude Enhancement Feature Learning for Vehicle Accident Detection and Anticipation

[![Paper](https://img.shields.io/badge/Paper-IEEE%20TITS-blue)](R2_Time_VAD.pdf)
[![Video Demo](https://img.shields.io/badge/Demo-Video-red)](TIME-VAD_demo.mp4)

> Official PyTorch implementation of TIME-VAD for vehicle accident detection and anticipation.
<p align="center">
  <img src="TIME-VAD.png" alt="TIME-VAD Architecture" width="800"/>
</p>
## 🎥 Video Demonstration

https://github.com/user-attachments/assets/bad9c20d-2b3a-4fbb-9ac1-457499fab9a9

*Demonstration of TIME-VAD model performance on vehicle accident detection and anticipation*

## 📄 Paper

**[Download Paper (PDF)](R2_Time_VAD.pdf)**

Published in *IEEE Transactions on Intelligent Transportation Systems*, 2025

## 🎯 Features

- 🚗 Support for multiple datasets: **CCD**, **DAD**, **DOTA**
- ⚡ Multiple temporal modeling options: **DTCA**, **TCN**, **Transformer**, **LSTM**, **ConvLSTM**
- 📊 Comprehensive evaluation metrics
- 🔧 Easy-to-use training and evaluation pipeline

## 📁 Project Structure
```
TIME-VAD/
├── main.py              # Main training script
├── option.py            # Command line arguments and configuration
├── config.py            # Configuration class
├── model.py             # Model architectures with temporal modeling options
├── dataset.py           # Dataset loading and preprocessing
├── train.py             # Training functions and loss computation
├── test_10crop.py       # Testing and evaluation
├── eval_tools.py        # Evaluation metrics (AP, mTTA, TTA@R80)
├── utils.py             # Utility functions
├── evaluation_model.py  # Evaluation script for fixed-frame datasets
├── evaluate_dota.py     # Evaluation script for variable-frame datasets
├── data/                # Dataset directory
│   ├── CCD/
│   ├── DAD/
│   └── DOTA/
├── checkpoints/         # Model checkpoints
├── results/             # Evaluation results
├── R2_Time_VAD.pdf      # Research paper
├── TIME-VAD_demo.mp4    # Video demonstration
└── LICENSE              # License file
```

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/TIME-VAD.git
cd TIME-VAD
```

2. **Install dependencies:**
```bash
pip install torch torchvision numpy scikit-learn matplotlib visdom tqdm
```

## 📂 Dataset Setup

Create the following directory structure in the `data/` folder:
```
data/
├── CCD/
│   ├── train_ccd.list
│   ├── test_ccd.list
│   └── ground_truth.npy
├── DAD/
│   ├── train.list
│   ├── test.list
│   └── ground_truth.npy
├── DOTA/
│   ├── train_dota.list
│   ├── DOTA_val.list
│   └── test_labels.npy
├── clip_features1.npy   # Negative anchor features
└── clip_features2.npy   # Positive anchor features
```

**Note:** 
- The `.list` files should contain paths to video feature files (one per line)
- The `.npy` files should contain frame-level binary labels
- Extract CLIP features [vit-large-patch14-336] for each dataset and save them accordingly
- Update feature paths in list files

## 💻 Usage

### Training

**Train on CCD dataset with default DTCA temporal model:**
```bash
python main.py --dataset ccd --batch-size 32
```

**Train on DAD dataset:**
```bash
python main.py --dataset dad --batch-size 32
```

**Train on DOTA dataset:**
```bash
python main.py --dataset dota --batch-size 32
```

**Train with different temporal models:**
```bash
# Using Transformer
python main.py --dataset ccd --temporal-model transformer --batch-size 16

# Using TCN
python main.py --dataset ccd --temporal-model tcn --batch-size 32

# Using LSTM
python main.py --dataset ccd --temporal-model lstm --batch-size 32
```

**Change hyperparameters in `option.py` or via command line arguments**

### Evaluation

**For fixed-frame datasets (CCD, DAD):**
```bash
python evaluation_model.py --dataset ccd --model-path checkpoints/time_vad_best.pkl --output-dir ./
```

**For variable-frame datasets (DOTA):**
```bash
python evaluate_dota.py --dataset dota --model-path checkpoints/time_vad_best.pkl --output-dir ./
```

## ⚙️ Configuration Options

### Model Architecture
- `--temporal-model`: Temporal modeling approach (`dtca`, `tcn`, `transformer`, `lstm`, `convlstm`)
- `--feature-size`: Input feature dimension (default: 768)

### Training Parameters
- `--batch-size`: Training batch size (default: 32)
- `--max-epoch`: Maximum training epochs
- `--lr`: Learning rate schedule as string
- `--weight-decay`: Optimizer weight decay
- `--num-segments`: Number of segments (use 50 for DAD if reducing size)

### Hardware
- `--gpu-id`: GPU device ID (-1 for CPU)

### Evaluation
- `--eval-freq`: Evaluation frequency in epochs
- `--eval-start`: Epoch to start evaluation
- `--eval-initial`: Perform initial evaluation

**See `option.py` for complete list of arguments**

## 🔬 Temporal Models

TIME-VAD supports multiple temporal modeling approaches:

| Model | Description |
|-------|-------------|
| **DTCA** (Default) | Dilated Temporal Conv-Attention with Non-Local blocks |
| **TCN** | Temporal Convolutional Network with residual connections |
| **Transformer** | Multi-head attention with positional encoding |
| **LSTM** | Bidirectional LSTM layers |
| **ConvLSTM** | Combination of convolutional and LSTM layers |

Select using `--temporal-model` argument.

## 📊 Evaluation Metrics

### For CCD and DAD:
- **AUC**: Area under ROC curve (frame-level)
- **AP_video**: Average Precision (video-level detection)
- **AP**: Average Precision (accident prediction)
- **mTTA**: Mean Time-to-Accident
- **TTA@R80**: Time-to-Accident at 80% Recall
- **P@R80**: Precision at 80% Recall

### For DOTA:
- **AUC**: Area under ROC curve (frame-level)

*Note: DOTA evaluation uses sliding window approach due to variable frame lengths*

## 💡 Training Tips

1. **Learning Rate**: Start with `[0.0005]*epochs` and adjust based on convergence
2. **Batch Size**: Use 32 for most datasets, reduce to 16 for Transformer models
3. **DAD Dataset**: If reducing frames to 50, pass `--num-segments 50`. For full 100 frames, update positional encoding in model
4. **DOTA Dataset**: Testing uses sliding window approach for variable-length videos
5. **Convergence**: Monitor validation metrics and adjust learning rate if training plateaus

## 📖 Citation

If you use this code in your research, please cite:
```bibtex
@ARTICLE{11295937,
  author={Mishra, Sumit and Mishra, Medhavi and Shyam, Pranjay and Har, Dongsoo},
  journal={IEEE Transactions on Intelligent Transportation Systems}, 
  title={TIME-VAD: Text-Informed Magnitude Enhancement Feature Learning for Vehicle Accident Detection and Anticipation}, 
  year={2025},
  volume={},
  number={},
  pages={1-16},
  doi={10.1109/TITS.2025.3637912}
}
```

## 📜 License
```
TIME-VAD: Text-Informed Magnitude Enhancement Feature Learning 
for Vehicle Accident Detection and Anticipation
Copyright (c) 2025

This software is provided for research and academic use only.
Commercial use, redistribution, or modification for commercial purposes 
is strictly prohibited without explicit written permission from the authors.

This project is associated with a Korean Patent Application (under review).
All rights reserved.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
```

---

**⭐ If you find this work helpful, please star this repository and cite our paper!**





