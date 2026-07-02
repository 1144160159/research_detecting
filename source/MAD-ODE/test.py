import numpy as np
import torch
import torch.nn as nn
import time
from util.time import *
from util.env import *

import argparse
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import torch.nn.functional as F

from util.data import *
from util.preprocess import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _prepare_data(x, y, dic):
    x, y = _get_x_y(x, y)
    x, y = _get_x_y_in_correct_dims(x, y, dic)
    return x.to(device), y.to(device)


def _get_x_y(x, y):
    """
    :param x: shape (batch_size, seq_len, num_sensor, input_dim)
    :param y: shape (batch_size, horizon, num_sensor, input_dim)
    :returns x shape (seq_len, batch_size, num_sensor, input_dim)
             y shape (horizon, batch_size, num_sensor, input_dim)
    """
    x = torch.from_numpy(x).float()  # torch.from_numpy，从np数组创建张量
    y = torch.from_numpy(y).float()
    x = x.permute(1, 0, 2, 3)
    y = y.permute(1, 0, 2, 3)
    return x, y


def _get_x_y_in_correct_dims(x, y, dic):
    """
    :param x: shape (seq_len, batch_size, num_sensor, input_dim)
    :param y: shape (horizon, batch_size, num_sensor, input_dim)
    :return: x: shape (seq_len, batch_size, num_sensor * input_dim)
             y: shape (horizon, batch_size, num_sensor * output_dim)
    """
    batch_size = x.size(1)
    x = x.view(dic['seq_len'], batch_size, dic['num_nodes'] * dic['input_dim'])  # （12,64,207*2）
    y = y[..., :dic['output_dim']].view(dic['horizon'], batch_size,
                                        dic['num_nodes'] * dic['output_dim'])  # (12,64,207*1)
    return x, y


def test(model, dataloader, temperature, _train_feas, dic):
    # test
    device = get_device()

    now = time.time()
    
    test_predicted_list = []
    test_ground_list = []
    test_labels_list = []
    stgcndic = []
    dcrnndic = []
    t_test_predicted_list = []
    t_test_ground_list = []
    t_test_labels_list = []

    gumbel_soft = True
    label = 'without_regularization'

    model.eval()

    i = 0

    for batch_idx, (x, y, labels) in enumerate(dataloader):

        y = y[:, 0:dic['horizon'], :, :]  # (batch_size, seq_len, num_sensor, input_dim)
        x, y = _prepare_data(x, y, dic)
        labels = torch.tensor(labels).double()
        y = y[0]

        with torch.no_grad():
            # predicted, _ = model(inputs = x,  node_feas = _train_feas, temp = temperature)
            stgcn, dcrnn, predicted, _,array = model(label, x, _train_feas, temperature, gumbel_soft, k = dic['k'])
            predicted = predicted[0]
            stgcn = stgcn[0]
            dcrnn = dcrnn[0]
            labels = labels[:, 0]
            labels = labels.unsqueeze(1)
            labels = labels.repeat(1, predicted.shape[1])

            if len(t_test_predicted_list) <= 0:
                t_test_predicted_list = predicted
                stgcndic = stgcn
                dcrnndic = dcrnn
                t_test_ground_list = y
                t_test_labels_list = labels
            else:
                t_test_predicted_list = torch.cat((t_test_predicted_list, predicted), dim=0)
                stgcndic = torch.cat((stgcndic, stgcn), dim=0)
                dcrnndic = torch.cat((dcrnndic, dcrnn), dim=0)
                t_test_ground_list = torch.cat((t_test_ground_list, y), dim=0)
                t_test_labels_list = torch.cat((t_test_labels_list, labels), dim=0)

        i += 1

    test_predicted_list = t_test_predicted_list.tolist()
    stgcndic = stgcndic.tolist()
    dcrnndic = dcrnndic.tolist()# 使用msl数据集，训练的时候test_predicted_list形状为30*27，测试的时候test_predicted_list形状为1999*27
    test_ground_list = t_test_ground_list.tolist()
    test_labels_list = t_test_labels_list.tolist()

    return [test_predicted_list, test_ground_list, test_labels_list,array,stgcndic,dcrnndic]




