# python3.9
# time:2025/11/8
# data from：https://huggingface.co/datasets/EgilKarlsen/Thunderbird_BERT_Baseline

from datasets import load_dataset
import numpy as np
import pandas as pd
import torch
from torch import nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
import torch.utils.data as Data
import matplotlib.pyplot as plt
from torch.nn.utils import weight_norm
from torch.autograd import Variable
import math
import time
from torchsummary import summary


# Login using e.g. `huggingface-cli login` to access this dataset
# ds = load_dataset("logfit-project/Thunderbird")

splits = {'train': 'data/train-00000-of-00001-ec21cad20410e828.parquet', 'test': 'data/test-00000-of-00001-4275684e731adef1.parquet'}
df_train = pd.read_parquet("hf://datasets/EgilKarlsen/Thunderbird_BERT_Baseline/" + splits["train"])
df_test = pd.read_parquet("hf://datasets/EgilKarlsen/Thunderbird_BERT_Baseline/" + splits["test"])
# ds = load_dataset("EgilKarlsen/Thunderbird_BERT_Baseline")
train = df_train.values
test = df_test.values
# print(train)

# ont-hot,1 is abnormal
for i in range(train.shape[0]):  # abnormal:568，all:7500
    if train[i, -1] == "Normal":
        train[i, -1] = 0
    else:
        train[i, -1] = 1
for i in range(test.shape[0]):  # abnormal:201，all:12500
    if test[i, -1] == "Normal":
        test[i, -1] = 0
    else:
        test[i, -1] = 1
# print(np.sum(test[:, -1]))
# print(test.shape[0])

df = pd.DataFrame(train)
df.to_excel(r'train.xlsx')
df1 = pd.DataFrame(test)
df1.to_excel(r'test.xlsx')