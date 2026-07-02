from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import yaml
from model.pytorch.supervisor import GTSSupervisor
from lib.utils import load_graph_data
import numpy as np
from evaluate import get_best_performance_data, get_val_performance_data, get_full_err_scores
import pandas as pd
from lib import utils
from pathlib import Path
import os
from datetime import datetime
import torch
from datasets.TimeDataset import TimeDataset
from test import *


'''
[67, 64, 44, 30, 41, 21]
[62, 46, 36, 65, 43, 27]
[90, 86, 82, 81, 40, 63, 45, 33, 42, 24]
'''

cluster_res = [67, 64, 44, 30, 41, 21,62, 46, 36, 65, 43, 27,55,58,52,57,51,56,98,49,47,53,50,54,48,105,38,17,15,13,5]
cluster_res.sort()
names = range(0, 124)
df_train = pd.read_csv('./data/wadi/test.csv', index_col=0, header=0,
                       names=names)
df_train = df_train.loc[:,cluster_res]
df_train.to_csv('result_test.csv',index=False)