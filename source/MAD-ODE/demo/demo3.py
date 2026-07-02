import os
import pandas as pd
import numpy as np


class DataLoader(object):
    def __init__(self, xs, ys,batch_size,labels, pad_with_last_sample=True, shuffle=False):
        """

        :param xs:
        :param ys:
        :param batch_size:
        :param pad_with_last_sample: pad with the last sample to make number of samples divisible to batch_size.
        """
        self.batch_size = batch_size
        self.current_ind = 0
            # if pad_with_last_sample:
            #     num_padding = (batch_size - (len(xs) % batch_size)) % batch_size
            #     x_padding = np.repeat(xs[-1:], num_padding, axis=0)
            #     y_padding = np.repeat(ys[-1:], num_padding, axis=0)
            #     xs = np.concatenate([xs, x_padding], axis=0)
            #     ys = np.concatenate([ys, y_padding], axis=0)
            # self.size = len(xs)    #数据量
            # self.num_batch = int(self.size // self.batch_size)   #这个数据集中分几个batch
            # if shuffle:
            #     permutation = np.random.permutation(self.size)
            #     xs, ys = xs[permutation], ys[permutation]
            # self.xs = xs
            # self.ys = ys

        if pad_with_last_sample:
            num_padding = (batch_size - (len(xs) % batch_size)) % batch_size
            x_padding = np.repeat(xs[-1:], num_padding, axis=0)
            y_padding = np.repeat(ys[-1:], num_padding, axis=0)
            labels_padding = np.repeat(labels[-1:], num_padding, axis=0)
            xs = np.concatenate([xs, x_padding], axis=0)
            ys = np.concatenate([ys, y_padding], axis=0)
            labels = np.concatenate([labels, labels_padding], axis=0)
        self.size = len(xs)    #数据量
        self.num_batch = int(self.size // self.batch_size)   #这个数据集中分几个batch
        if shuffle:
            permutation = np.random.permutation(self.size)
            xs, ys ,labels= xs[permutation], ys[permutation],labels[permutation]
        self.xs = xs
        self.ys = ys
        self.labels = labels

    def get_iterator(self):
        self.current_ind = 0

        def _wrapper():
            while self.current_ind < self.num_batch:
                start_ind = self.batch_size * self.current_ind
                end_ind = min(self.size, self.batch_size * (self.current_ind + 1))
                x_i = self.xs[start_ind: end_ind, ...]
                y_i = self.ys[start_ind: end_ind, ...]
                labels = self.labels[start_ind: end_ind, ...]
                yield (x_i, y_i,labels)        #yieled相当于return
                self.current_ind += 1

        return _wrapper()

class StandardScaler:
    """
    Standard the input
    """

    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def transform(self, data):  #归一化
        return (data - self.mean) / self.std

    def inverse_transform(self, data):
        return (data * self.std) + self.mean

data = {}
for category in ['train', 'val', 'test']:
    cat_data = np.load('../data/swat/{}.npz'.format(category))
    data['x_' + category] = cat_data['x']
    data['y_' + category] = cat_data['y']
    data['labels_' + category] = cat_data['labels']

scaler = StandardScaler(mean=data['x_train'][..., 0].mean(), std=data['x_train'][..., 0].std())  #mean均值，std标准差5
# Data format
for category in ['train', 'val', 'test']:
    data['x_' + category][..., 0] = scaler.transform(data['x_' + category][..., 0])     #归一化
    data['y_' + category][..., 0] = scaler.transform(data['y_' + category][..., 0])
data['train_loader'] = DataLoader(data['x_train'], data['y_train'],64, shuffle=True,labels=data['labels_train'] )
data['val_loader'] = DataLoader(data['x_val'], data['y_val'],64, shuffle=False,labels=data['labels_val'] )
data['test_loader'] = DataLoader(data['x_test'], data['y_test'] ,64, shuffle=False,labels=data['labels_test'])
data['scaler'] = scaler

i = 0

for batch_idx, (x, y, labels) in enumerate(data['train_loader'].get_iterator()):
    print('x:',x.shape,'y:',y.shape,'labels:',labels.shape)
    ++i
print(batch_idx)