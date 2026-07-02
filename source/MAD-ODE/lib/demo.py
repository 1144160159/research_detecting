import numpy as np
import os
import pandas as pd

# cat_data = np.load('../data/METR-LA/train.npz')
# print(cat_data.files)
for category in ['train', 'val', 'test']:
    cat_data = np.load('../data/METR-LA/{}.npz'.format(category))
    print(cat_data['x'].shape)