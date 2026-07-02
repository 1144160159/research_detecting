from _typeshed import NoneType
import os
import numpy as np
import pandas as pd
import os
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


class Dataset_Flow(Dataset):
    def __init__(self, mode, use_Label, root_path, flag='train', size=None,
                 features='S', Train_data_path=None, Test_data_path=None, Val_data_path=None,
                 use_upsample=False, upsample_strategy='balanced'):

        self.seq_len = size[0]
        self.label_len = size[1]
        self.pred_len = size[2]
        # init
        assert flag in ['train', 'test', 'val']
        type_map = {'train': 0, 'val': 1, 'test': 2}
        self.set_type = type_map[flag]
        self.mode = mode
        self.features = features
        self.use_Label = use_Label
        self.use_upsample = use_upsample
        self.upsample_strategy = upsample_strategy

        self.root_path = root_path
        self.Train_data_path = Train_data_path
        self.Test_data_path = Test_data_path
        self.Val_data_path = Val_data_path

        self.__read_data__(flag)
        
    
    def __read_data__(self, flag):
        self.scaler = StandardScaler()
        '''
        df_raw.columns: [ features, timestamp, Label]
        '''
        
        # Define data path mapping
        path_mapping = {
            'train': self.Train_data_path,
            'test': self.Test_data_path,
            'val': self.Val_data_path
        }
        
        if flag not in path_mapping:
            raise ValueError('WRONG FLAG!')
            
        # Read data based on flag
        data = pd.read_csv(os.path.join(self.root_path, path_mapping[flag]))
        
        # Extract components
        Label = data['Label']
        df_stamp = data[['timeFirst']]
        data = data.drop(columns=['timeFirst', 'Label'])
        
        # Add Label back if needed
        if self.use_Label:
            data['Label'] = Label
            
        # Set data based on mode (before upsampling)
        self.data_x = data.values
        self.data_y = Label.values
        if self.mode == 'analysis':
            self.data_stamp = df_stamp.values

        # Upsample only on training split and classification setting
        if flag == 'train' and self.use_upsample:
            from utils.upsample import upsample_data
            self.data_x, self.data_y = upsample_data(
                self.data_x,
                self.data_y,
                strategy=self.upsample_strategy,
                random_state=42,
            )

    def __getitem__(self, index):
        if self.mode == 'pred':
            s_begin = index
            s_end = s_begin + self.seq_len
            r_begin = s_end - self.label_len
            r_end = r_begin + self.label_len + self.pred_len
            seq_x = self.data_x[s_begin:s_end]
            seq_y = self.data_y[r_begin:r_end]

        elif self.mode == 'analysis':
            s_begin = index
            s_end = s_begin + self.seq_len
            r_begin = index 
            r_end = r_begin + self.seq_len
            seq_x = self.data_x[s_begin:s_end]
            seq_y = self.data_y[r_begin:r_end]
        else:
            raise ValueError('WRONG MODE!')
        return seq_x, seq_y
    

    def __len__(self):
        return len(self.data_x) - self.seq_len - self.pred_len + 1

    
class Dataset_Packet(Dataset):
    def __init__(self, mode, use_Label, root_path, flag='train', size=None,
                 features='MS', Train_data_path=None, Test_data_path=None, Val_data_path=None,
                 use_upsample=False, upsample_strategy='balanced'):

        self.seq_len = size[0]
        self.label_len = size[1]
        self.pred_len = size[2]
        # init
        assert flag in ['train', 'test', 'val']
        type_map = {'train': 0, 'val': 1, 'test': 2}
        self.set_type = type_map[flag]
        self.features = features
        self.use_upsample = use_upsample
        self.upsample_strategy = upsample_strategy

        self.root_path = root_path
        self.Train_data_path = Train_data_path
        self.Test_data_path = Test_data_path
        self.Val_data_path = Val_data_path
        self.__read_data__(flag)

    def __read_data__(self, flag):
        self.scaler = StandardScaler()
        '''
        df_raw.columns: [ features, timestamp(FirstTime), Label]
        '''
        
        # Define data path mapping
        path_mapping = {
            'train': self.Train_data_path,
            'test': self.Test_data_path,
            'val': self.Val_data_path
        }
        
        if flag not in path_mapping:
            raise ValueError('WRONG FLAG!')
            
        # Read data based on flag
        df_data = pd.read_csv(os.path.join(self.root_path, path_mapping[flag]))
        
        # Handle label encoding if needed
        if df_data.Label.dtype == 'str':
            le = LabelEncoder()
            le.fit_transform(df_data.Label.values)
            df_data['Label'] = le.transform(df_data['Label'])
        
        # Extract components
        Label = df_data['Label']
        df_stamp = df_data['time']
        data = df_data.drop(columns=['Label', 'time'])
        
        self.data_x = data.values
        self.data_y = Label.values
        self.data_stamp = df_stamp.values

        if flag == 'train' and self.use_upsample:
            from utils.upsample import upsample_data
            self.data_x, self.data_y = upsample_data(
                self.data_x,
                self.data_y,
                strategy=self.upsample_strategy,
                random_state=42,
            )
        
    def __getitem__(self, index):
        s_begin = index
        s_end = s_begin + self.seq_len
        r_begin = index 
        r_end = r_begin + self.seq_len
        seq_x = self.data_x[s_begin:s_end]
        seq_y = self.data_y[r_begin:r_end]
        return seq_x, seq_y
    

    def __len__(self):
        return len(self.data_x) - self.seq_len - self.pred_len + 1
    
class Dataset_Packet2Flow(Dataset):
    def __init__(self, mode, use_Label, root_path, flag='train', size=None,
                 features='S', Train_data_path=None, Test_data_path=None, Val_data_path=None, scale=False, timeenc=0,
                 use_upsample=False, upsample_strategy='balanced'):
        

        self.seq_len = size[0]
        self.label_len = size[1]
        self.pred_len = size[2]
        # init
        assert flag in ['train', 'test', 'val']
        type_map = {'train': 0, 'val': 1, 'test': 2}
        self.set_type = type_map[flag]
        self.mode = mode
        self.features = features
        self.scale = scale
        self.use_upsample = use_upsample
        self.upsample_strategy = upsample_strategy

        self.root_path = root_path
        self.Train_data_path = Train_data_path
        self.Test_data_path = Test_data_path
        self.Val_data_path = Val_data_path
        self.__read_data__(flag)

    def __read_data__(self, flag):
        self.scaler = StandardScaler()
        '''
        df_raw.columns: [ features, time, Label]
        '''
        
        # Define data path mapping
        path_mapping = {
            'train': self.Train_data_path,
            'test': self.Test_data_path,
            'val': self.Val_data_path
        }
        
        if flag not in path_mapping:
            raise ValueError('WRONG FLAG!')
            
        # Read data based on flag
        df_data = pd.read_csv(os.path.join(self.root_path, path_mapping[flag]))
        
        # Handle scaling if needed
        if self.scale:
            time_col = 'time' 
            cols_to_norm = [col for col in df_data.columns if col not in [time_col, 'Label']]
            df_data[cols_to_norm] = self.scaler.fit_transform(df_data[cols_to_norm])
        
        # Extract components
        Label = df_data['Label']
        data = df_data.drop(columns=['Label'])
        data = data.drop(columns=['time'])
    
        # Create chunks of size 32
        chunk_size = 32
        chunks = [data.iloc[i:i + chunk_size].values for i in range(0, len(data), chunk_size)]
        l_chunks = [Label.iloc[i:i + chunk_size] for i in range(0, len(Label), chunk_size)]
        
        # Validate that each chunk has the same label value
        validation_result = all(chunk.nunique() == 1 for chunk in l_chunks)
        if validation_result:
            chunks_Label = [chunk.iloc[0] for chunk in l_chunks]
        else:
            raise ValueError('Wrong data! Labels in chunks are not consistent.')
        
        self.data_x = np.array(chunks) 
        self.data_y = np.array(chunks_Label)

        if flag == 'train' and self.use_upsample:
            from utils.upsample import upsample_data
            self.data_x, self.data_y = upsample_data(
                self.data_x,
                self.data_y,
                strategy=self.upsample_strategy,
                random_state=42,
            )
        
    def __getitem__(self, index):
        # At this time, data_y is the label sequence of data_x
        seq_x = self.data_x[index]
        seq_y = self.data_y[index]

        return seq_x, seq_y
    
    def __len__(self):
        return self.data_x.shape[0]
        
    def inverse_transform(self, data):
        return self.scaler.inverse_transform(data)