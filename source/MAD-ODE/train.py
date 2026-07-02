from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from mai import mai
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
import os
from fastdtw import fastdtw
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Main():
    def __init__(self,config) -> None:
        self.config = config
        self.config_filename = self.config['config_filename']
        self.use_cpu_only = self.config['use_cpu_only']
        self.temperature = self.config['temperature']
        with open(self.config_filename) as f:
            # self.supervisor_config = yaml.load(f)
            self.supervisor_config = yaml.safe_load(f)
        self._data_kwargs = self.supervisor_config.get('data')     #_data_kwargs数据的一些参数
        self._model_kwargs = self.supervisor_config.get('model')       #模型的一些参数
        self._train_kwargs = self.supervisor_config.get('train')        #训练的一些参数
        self.report = self.config['report']
        
        ### Feas
        if self._data_kwargs['dataset_dir'] == 'data/METR-LA':
            dataset = 'ori'
            df = pd.read_hdf('./data/metr-la.h5')
        elif self._data_kwargs['dataset_dir'] == 'data/PEMS-BAY':
            dataset = 'ori'
            df = pd.read_hdf('./data/pems-bay.h5')
        else:
            dataset = 'other'
            names = range(0,self._model_kwargs['num_nodes']+1)
            df_train = pd.read_csv('./data/{}/train.csv'.format(self._data_kwargs['dataset_name']), index_col=0)
            if 'attack' in df_train.columns:
                df_train = df_train.drop(columns=['attack'])
            if 'timestamp' in df_train.columns:
                df_train = df_train.drop(columns=['timestamp'])

                

        if dataset == 'ori':
            num_samples = df.shape[0]
            num_train = round(num_samples * 0.7)
            df = df[:num_train].values
            scaler = utils.StandardScaler(mean=df.mean(), std=df.std())
            train_feas = scaler.transform(df)         #训练集归一化后作为训练集特征生成knn图
            self.train_feas = train_feas
            self._train_feas = torch.Tensor(train_feas).to(device)

            # data set
            self.dataloader = utils.load_dataset(**self._data_kwargs)    #dataloader
            self.standard_scaler = self.dataloader['scaler']     #一个StandardScaler类的对象，存储了均值标准差

        else:
            df = df_train.values[...,range(0,self._model_kwargs['num_nodes'])]
            
            
            n = np.zeros((df.shape[1], df.shape[1]))
            data = df.reshape((df.shape[0],df.shape[1],1))
            num_node = data.shape[1]
            mean_value = np.mean(data, axis=(0, 1)).reshape(1, 1, -1)
            std_value = np.std(data, axis=(0, 1)).reshape(1, 1, -1)
            data = (data - mean_value) / std_value
            mean_value = mean_value.reshape(-1)[0]
            std_value = std_value.reshape(-1)[0]
            filename = self._data_kwargs['dataset_name']
            if not os.path.exists(f'data/{filename}_dtw_distance.npy'):
                data_mean = np.mean([data[:, :, 0][24 * 12 * i: 24 * 12 * (i + 1)] for i in range(data.shape[0] // (24 * 12))],axis=0)
                data_mean = data_mean.squeeze().T
                dtw_distance = np.zeros((num_node, num_node))
                for i in range(num_node):
                    for j in range(i, num_node):
                        dtw_distance[i][j] = fastdtw(data_mean[i], data_mean[j], radius=6)[0]
                for i in range(num_node):
                    for j in range(i):
                        dtw_distance[i][j] = dtw_distance[j][i]
                print(dtw_distance.shape)
                np.save(f'data/{filename}_dtw_distance.npy', dtw_distance)
            
            
            
            
            scaler = utils.StandardScaler(mean=df.mean(), std=df.std())
            train_feas = scaler.transform(df)
            self.train_feas = train_feas
            self._train_feas = torch.Tensor(train_feas).to(device)
            # data set
            self.dataloader = utils.load_dataset_other(**self._data_kwargs)    #dataloader
            self.standard_scaler = self.dataloader['scaler']     #一个StandardScaler类的对象，存储了均值标准差



    def run(self):
        dic = {}
        save_adj_name = self.config_filename[11:-5]
        model_save_path = self.get_save_path()[0]
        supervisor = GTSSupervisor(self.train_feas, self.dataloader, self.standard_scaler, save_adj_name, temperature=self.temperature, load_model_path = model_save_path,**self.supervisor_config)
        GTS_model,load_model_path = supervisor.train()

        GTS_model.load_state_dict(torch.load(load_model_path))
        best_model = GTS_model.to(device)

        dic['seq_len'] = int(self.supervisor_config.get('model').get('seq_len'))
        dic['num_nodes']=int(self.supervisor_config.get('model').get('num_nodes', 1))
        dic['input_dim']=int(self.supervisor_config.get('model').get('input_dim', 1))
        dic['output_dim'] =int(self.supervisor_config.get('model').get('output_dim', 1))
        dic['horizon']=int(self.supervisor_config.get('model').get('horizon', 1))
        dic['k'] = int(self.supervisor_config.get('train').get('knn_k', 1))

        self.train_result = test(best_model, self.dataloader['train_loader'].get_iterator(),self.temperature,self._train_feas,dic)
        self.test_result = test(best_model, self.dataloader['test_loader'].get_iterator(),self.temperature,self._train_feas,dic)    #(1999,27)(1999,27)(1999,27)
        self.val_result = test(best_model, self.dataloader['val_loader'].get_iterator(),self.temperature,self._train_feas,dic)

        train_preds = np.array(self.train_result[0])
        train_trues = np.array(self.train_result[1])

        test_preds = np.array(self.test_result[0])
        test_trues = np.array(self.test_result[1])
        test_labels = np.array(self.test_result[2])[:,0]
        teststgcn = np.array(self.test_result[4])
        testdcrnn = np.array(self.test_result[5])
        folder_path = './results/' + self._data_kwargs['dataset_name'] + '/'

        np.save(folder_path + 'test_preds.npy', test_preds)        #(44928, 1, 51)
        np.save(folder_path + 'test_trues.npy', test_trues )
        np.save(folder_path + 'test_labels.npy', test_labels)      #(44928, 1)
        np.save(folder_path + 'train_preds.npy', train_preds)        #(44928, 1, 51)
        np.save(folder_path + 'train_trues.npy', train_trues )
        np.save(folder_path + 'test_stgcn.npy', teststgcn)
        np.save(folder_path + 'test_dcrnn.npy', testdcrnn)
        # self.get_score(self.test_result, self.val_result)

        mai(self._data_kwargs['dataset_name'])

    def get_save_path(self, feature_name=''):
  
        dir_path = self._data_kwargs['dataset_name']
        

        now = datetime.now()
        datestr = now.strftime('%m-%d-%H-%M-%S')

        paths = [
            f'./pretrained/{dir_path}/best_{datestr}.pt',
            f'./results/{dir_path}/{datestr}.csv',
        ]

        for path in paths:
            dirname = os.path.dirname(path)
            Path(dirname).mkdir(parents=True, exist_ok=True)

        return paths

    def get_score(self, test_result, val_result):

        feature_num = len(test_result[0][0])    #时序数量
        np_test_result = np.array(test_result)
        np_val_result = np.array(val_result)

        test_labels = np_test_result[2, :, 0].tolist()
    
        test_scores, normal_scores = get_full_err_scores(test_result, val_result)

        top1_best_info = get_best_performance_data(test_scores, test_labels, topk=1) 
        top1_val_info = get_val_performance_data(test_scores, normal_scores, test_labels, topk=1)


        print('=========================** Result **============================\n')

        info = None
        if self.report == 'best':
            info = top1_best_info
        elif self.report == 'val':
            info = top1_val_info

        print(f'F1 score: {info[0]}')
        print(f'precision: {info[1]}')
        print(f'recall: {info[2]}\n')
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_filename', default='data/model/smap.yaml', type=str,
                        help='Configuration filename for restoring the model.')
    parser.add_argument('--use_cpu_only', default=False, type=bool, help='Set to true to only use cpu.')
    parser.add_argument('--temperature', default=0.5, type=float, help='temperature value for gumbel-softmax.')
    parser.add_argument('-slide_win', help='slide_win', type = int, default=12)
    parser.add_argument('-slide_stride', help='slide_stride', type = int, default=1)
    parser.add_argument('-report', help='best / val', type=str, default='best')
    args = parser.parse_args()

    config = {
        'config_filename': args.config_filename,
        'use_cpu_only': args.use_cpu_only,
        'temperature': args.temperature,
        'slide_win':args.slide_win,
        'slide_stride':args.slide_stride,
        'report': args.report
    }

    main = Main(config)
    main.run()
