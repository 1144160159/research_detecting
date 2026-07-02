__all__ = ['CTT']

# Cell
from typing import Callable, Optional
import torch
from torch import nn
from torch import Tensor
import torch.nn.functional as F
import numpy as np

from layers.CTT_backbone import CTT_backbone

class Model(nn.Module):
    def __init__(self, configs, max_seq_len:Optional[int]=1024, d_k:Optional[int]=None, d_v:Optional[int]=None, norm:str='BatchNorm', attn_dropout:float=0., 
                 act:str="gelu", key_padding_mask:bool='auto',padding_var:Optional[int]=None, attn_mask:Optional[Tensor]=None, 
                 pre_norm:bool=False, store_attn:bool=False, pe:str='zeros', learn_pe:bool=True, pretrain_head:bool=False, head_type = 'flatten', verbose:bool=False, **kwargs):
        
        super().__init__()
        
        # load parameters
        c_in = configs.enc_in
        context_window = configs.seq_len #lookback windows length
        target_window = configs.pred_len #prediction windows length
        
        n_layers = configs.e_layers # number of encoding layers
        n_heads = configs.n_heads
        d_model = configs.d_model 
        d_ff = configs.d_ff
        factor = configs.factor
        dropout = configs.dropout
        cross_attn_dropout = configs.cross_attn_dropout
        cross_dropout= configs.cross_dropout
        fc_dropout = configs.fc_dropout
        head_dropout = configs.head_dropout
       
        patch_len = configs.patch_len
        stride = configs.stride
        padding_patch = configs.padding_patch #'end' means padding in the end 
        seq_len = configs.seq_len
        revin = configs.revin #
        affine = configs.affine #
        subtract_last = configs.subtract_last #
        individual = configs.individual 
        self.mode = configs.mode
        self.level = configs.level
        class_num = configs.c_out
        use_CNN = configs.use_CNN
        self.model = CTT_backbone(c_in=c_in, context_window = context_window, target_window=target_window, patch_len=patch_len, stride=stride, 
                                max_seq_len=max_seq_len, n_layers=n_layers, d_model=d_model,mode=self.mode,level=self.level,use_CNN=use_CNN, class_num=class_num,seq_len=seq_len,
                                n_heads=n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff, factor=factor,norm=norm, attn_dropout=attn_dropout,
                                dropout=dropout, cross_attn_dropout=cross_attn_dropout, cross_dropout=cross_dropout, act=act, key_padding_mask=key_padding_mask, padding_var=padding_var, 
                                attn_mask=attn_mask, pre_norm=pre_norm, store_attn=store_attn,
                                pe=pe, learn_pe=learn_pe, fc_dropout=fc_dropout, head_dropout=head_dropout, padding_patch = padding_patch,
                                pretrain_head=pretrain_head, head_type=head_type, individual=individual, revin=revin, affine=affine,
                                subtract_last=subtract_last, verbose=verbose, **kwargs)
    
    
    def forward(self, x):           # x: [Batch, Input length, Channel]
        x = x.permute(0,2,1)        # x: [Batch, Channel, Input length]
        x = self.model(x)
        if self.mode =='pred':
            x = x.permute(0,2,1)    # x: [Batch, Input length, Channel]
        return x