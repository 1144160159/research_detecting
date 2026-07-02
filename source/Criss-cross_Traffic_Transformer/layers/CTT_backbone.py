__all__ = ['CTT_backbone']

# Cell
from typing import Callable, Optional
import torch
from torch import nn
from torch import Tensor
import torch.nn.functional as F
import numpy as np
from einops import rearrange, repeat
#from collections import OrderedDict
from layers.CTT_layers import *
from layers.RevIN import RevIN



# Cell
class CTT_backbone(nn.Module):
    def __init__(self, c_in:int, context_window:int, target_window:int, patch_len:int, stride:int, max_seq_len:Optional[int]=1024, 
                 n_layers:int=3, d_model=128,mode='analysis',level='packet2flow',use_CNN=True,class_num=7,n_heads=16, d_k:Optional[int]=None, d_v:Optional[int]=None,
                 d_ff:int=256, factor=10,norm:str='BatchNorm', attn_dropout:float=0., dropout:float=0.,cross_attn_dropout=0., cross_dropout=0., act:str="gelu", key_padding_mask:bool='auto',
                 padding_var:Optional[int]=None, attn_mask:Optional[Tensor]=None,  pre_norm:bool=False, store_attn:bool=False,
                 pe:str='zeros', learn_pe:bool=True, fc_dropout:float=0., head_dropout = 0, padding_patch = None,
                 pretrain_head:bool=False, head_type = 'flatten', individual = False, revin = True, affine = True, subtract_last = False,
                 verbose:bool=False, **kwargs):
        
        super().__init__()
        
        # RevIn
        self.revin = revin
        if self.revin: self.revin_layer = RevIN(c_in, affine=affine, subtract_last=subtract_last)
        self.mode = mode
        self.level = level
        self.class_num = class_num
        # Patching
        self.patch_len = patch_len
        self.stride = stride
        self.padding_patch = padding_patch
        patch_num = int((context_window - patch_len)/stride + 1) #(L-P)/S +1
        if padding_patch == 'end': 
            self.padding_patch_layer = nn.ReplicationPad1d((0, stride))
            patch_num += 1 # (L-P)/S +2
        self.seq_len = context_window
        self.use_CNN = use_CNN
        # Backbone 
        self.backbone = TSTiEncoder(c_in, patch_num=patch_num, patch_len=patch_len, max_seq_len=max_seq_len,
                                n_layers=n_layers, d_model=d_model, n_heads=n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff,factor=factor,
                                attn_dropout=attn_dropout, dropout=dropout, cross_attn_dropout=cross_attn_dropout, cross_dropout=cross_dropout,act=act, key_padding_mask=key_padding_mask, padding_var=padding_var,
                                attn_mask=attn_mask, pre_norm=pre_norm, store_attn=store_attn,
                                pe=pe, learn_pe=learn_pe, verbose=verbose, **kwargs)

        # Head
        self.head_nf = d_model * patch_num
        self.n_vars = c_in
        self.pretrain_head = pretrain_head
        self.head_type = head_type
        self.individual = individual

       
        if self.mode == 'pred': 
            self.head = Flatten_Head_Pred(self.individual,self.n_vars,self.head_nf, target_window,self.class_num, head_dropout)
        elif self.mode == 'analysis':
            self.head = CNN_Head(self.class_num,self.n_vars,d_model,patch_num,self.seq_len,self.level)
        
    def forward(self, z):                                                                   # z: [bs x nvars x seq_len]
        # norm
        if self.revin: 
            z = z.permute(0,2,1)
            z = self.revin_layer(z, 'norm')
            z = z.permute(0,2,1)
            
        # do patching
        if self.padding_patch == 'end':
            z = self.padding_patch_layer(z) 
        z = z.unfold(dimension=-1, size=self.patch_len, step=self.stride)                   # z: [bs x nvars x patch_num x patch_len]
        z = z.permute(0,1,3,2)                                                              # z: [bs x nvars x patch_len x patch_num]

        # model
        z = self.backbone(z)                                                           # z: [bs x nvars x d_model x patch_num]
        if self.mode == 'analysis':
            z = z.permute(0,3,1,2) # (batch_size,patch_num,features_num,dmodel)
            z = z.reshape(z.shape[0],z.shape[1],-1) # (batch_size,patch_num,features_num*dmodel)
            if self.use_CNN:
                z = z.unsqueeze(1) # (batch_size,1,patch_num,features_num*dmodel)
        z = self.head(z)                    # pred: z: [bs x nvars x target_window] 
        
        # denorm
        if self.revin: 
            z = z.permute(0,2,1)
            z = self.revin_layer(z, 'denorm')
            z = z.permute(0,2,1)
        return z
    
    def create_pretrain_head(self, head_nf, vars, dropout):
        return nn.Sequential(nn.Dropout(dropout),
                    nn.Conv1d(head_nf, vars, 1)
                    )


class Flatten_Head_Pred(nn.Module):
    def __init__(self, individual, n_vars, nf, target_window, class_num,head_dropout=0):
        super().__init__()
        
        self.individual = individual
        self.n_vars = n_vars
        self.class_num = class_num
        if self.individual:
            self.linears = nn.ModuleList()
            self.dropouts = nn.ModuleList()
            self.flattens = nn.ModuleList()
            for i in range(self.n_vars):
                self.flattens.append(nn.Flatten(start_dim=-2))
                self.linears.append(nn.Linear(nf, target_window))
                self.dropouts.append(nn.Dropout(head_dropout))
        else:
            self.flatten = nn.Flatten(start_dim=-2) 
            self.linear = nn.Linear(nf, target_window)
            self.dropout = nn.Dropout(head_dropout)
            self.class_head = nn.Sequential(nn.Linear(n_vars,128), nn.ReLU(),nn.Dropout(head_dropout),nn.Linear(128,64),nn.ReLU(),nn.Dropout(head_dropout),nn.Linear(64,32),nn.ReLU(),nn.Dropout(head_dropout),nn.Linear(32,self.class_num))
            
    def forward(self, x):                                 # x: [bs x nvars x d_model x patch_num]
        if self.individual:
            x_out = []
            for i in range(self.n_vars):
                z = self.flattens[i](x[:,i,:,:])          # z: [bs x d_model * patch_num]
                z = self.linears[i](z)                    # z: [bs x target_window]
                z = self.dropouts[i](z)
                x_out.append(z)
            x = torch.stack(x_out, dim=1)                 # x: [bs x nvars x target_window]
        else:
            x = self.flatten(x) # x: [bs x nvars x d_model * patch_num]
            x = self.linear(x)  # x: [bs x nvars x target_window]
            x = self.dropout(x)
            x = x.permute(0,2,1)
            x = self.class_head(x)
            x = x.permute(0,2,1)
        return x
    

class CNN_Head(nn.Module):
    def __init__(self, class_num,n_vars,d_model,patch_num,seq_len,level,pooling_size=4):
        super(CNN_Head, self).__init__()
        self.level = level
       
        assert seq_len % patch_num ==0
        dim = seq_len//patch_num
        print("The dim is:")
        print(dim)
        self.conv1 = nn.Conv2d(1, dim//2, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=(1,pooling_size), stride=(1,pooling_size)) 
        
        self.conv2 = nn.Conv2d(dim//2, dim, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=(1,pooling_size), stride=(1,pooling_size))
        self.flatten = nn.Flatten(start_dim=1)
        

        if self.level == 'packet' or self.level == 'flow':
            self.flatten_size =int(n_vars*d_model/(pooling_size*pooling_size))   # 
        else :
            self.flatten_size = int(dim*patch_num*n_vars*d_model/(pooling_size*pooling_size)) 
        self.fc1 = nn.Linear(self.flatten_size, 64)
        self.relu3 = nn.ReLU()
        
        self.fc2 = nn.Linear(64, class_num)  
        
        
    def forward(self, x):
        x = self.conv1(x) #shape=(batch_size,4,64,2176)
        x = self.relu1(x)
        x = self.pool1(x) #shape=(batch_size,4,64,544)
        
        x = self.conv2(x) #shape=(batch_size,16,64,544)
        x = self.relu2(x)
        x = self.pool2(x) #shape=(batch_size,16,32,136)
        
        if self.level == 'packet' or self.level == 'flow':
            x = x.view(x.shape[0],x.shape[1]*x.shape[2],x.shape[3]) #shape=(batch_size,512,136)
            x = self.fc1(x)
            x = self.relu3(x)
            x = self.fc2(x)
            x = x.reshape(x.shape[0]*x.shape[1],x.shape[2]) 
        else:
            x = self.flatten(x)
            x = self.fc1(x)
            x = self.relu3(x)
            x = self.fc2(x)
        return x    
        
    
    
class TSTiEncoder(nn.Module):  
    def __init__(self, c_in, patch_num, patch_len, max_seq_len=1024,
                 n_layers=3, d_model=128, n_heads=16, d_k=None, d_v=None,
                 d_ff=256,factor=10, norm='BatchNorm', attn_dropout=0., dropout=0.,cross_attn_dropout=0., cross_dropout=0., act="gelu", store_attn=False,
                 key_padding_mask='auto', padding_var=None, attn_mask=None, pre_norm=False,
                 pe='zeros', learn_pe=True, verbose=False, **kwargs):
        
        super().__init__()
        
        self.patch_num = patch_num
        self.patch_len = patch_len
        
        # Input encoding
        q_len = patch_num
        self.W_P = nn.Linear(patch_len, d_model)       
        self.seq_len = q_len

        # Positional encoding
        self.W_pos = positional_encoding(pe, learn_pe, q_len, d_model)

        # Residual dropout
        self.dropout = nn.Dropout(dropout) 

        # Encoder
        self.encoder = TSTEncoder(q_len, d_model, n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff,factor=factor, norm=norm, attn_dropout=attn_dropout, dropout=dropout,cross_attn_dropout=cross_attn_dropout, cross_dropout=cross_dropout,
                                   pre_norm=pre_norm, activation=act,  n_layers=n_layers, store_attn=store_attn)

        
    def forward(self, x) -> Tensor:                                              # x: [bs x nvars x patch_len x patch_num]
        
        n_vars = x.shape[1]
        # Input encoding
        x = x.permute(0,1,3,2)                                                   # x: [bs x nvars x patch_num x patch_len]
        x = self.W_P(x)                                                          # x: [bs x nvars x patch_num x d_model]

        u = torch.reshape(x, (x.shape[0]*x.shape[1],x.shape[2],x.shape[3]))      # u: [bs * nvars x patch_num x d_model]
        u = self.dropout(u + self.W_pos)                                         # u: [bs * nvars x patch_num x d_model]

        # Encoder
        z= self.encoder(u,n_vars)                                                # z: [bs * nvars x patch_num x d_model]
        z = torch.reshape(z, (-1,n_vars,z.shape[-2],z.shape[-1]))                # z: [bs x nvars x patch_num x d_model]
        z = z.permute(0,1,3,2)                                                   # z: [bs x nvars x d_model x patch_num]
        
        return z
            
            
    
# Cell
class TSTEncoder(nn.Module):
    def __init__(self, q_len, d_model, n_heads, d_k=None, d_v=None, d_ff=None, factor=10,
                        norm='BatchNorm', attn_dropout=0., dropout=0., cross_attn_dropout=0., cross_dropout=0., activation='gelu',
                        n_layers=1, pre_norm=False, store_attn=False):
        super().__init__()

        self.layers = nn.ModuleList([CrossTSTEncoderLayer(q_len, d_model, n_heads=n_heads, d_k=d_k, d_v=d_v, d_ff=d_ff,factor=factor, norm=norm,
                                                      attn_dropout=attn_dropout, dropout=dropout, cross_attn_dropout=cross_attn_dropout, cross_dropout=cross_dropout,
                                                      activation=activation,
                                                      pre_norm=pre_norm, store_attn=store_attn) for i in range(n_layers)])


    def forward(self, src:Tensor,n_vars, key_padding_mask:Optional[Tensor]=None, attn_mask:Optional[Tensor]=None):
        output = src
        # scores = None
        for mod in self.layers:  #output.shape = (batch_size*n_vars,patch_num,d_model)
            output,att_weight1,att_weight2,att_weight3 = mod(output, n_vars=n_vars, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
        return output,att_weight1,att_weight2,att_weight3



class CrossTSTEncoderLayer(nn.Module):

    def __init__(self, q_len, d_model, n_heads, d_k=None, d_v=None, d_ff=256,factor=10, store_attn=False,
                 norm='BatchNorm', attn_dropout=0, dropout=0., cross_attn_dropout=0, cross_dropout=0., bias=True, activation="gelu", pre_norm=False):
        super().__init__()
        assert not d_model%n_heads, f"d_model ({d_model}) must be divisible by n_heads ({n_heads})"
        d_k = d_model // n_heads if d_k is None else d_k 
        d_v = d_model // n_heads if d_v is None else d_v

        # Multi-Head attention

        self.self_attn = _MultiheadAttention(d_model, n_heads, d_k, d_v, attn_dropout=attn_dropout, proj_dropout=dropout)
        # Add & Norm
        self.dropout_attn = nn.Dropout(dropout)
        if "batch" in norm.lower(): #BatchNorm
            self.norm_attn1 = nn.Sequential(Transpose(1,2), nn.BatchNorm1d(d_model), Transpose(1,2))
        else: #LayerNorm
            self.norm_attn1 = nn.LayerNorm(d_model)
        
        # Position-wise Feed-Forward
        self.ff = nn.Sequential(nn.Linear(d_model, d_ff, bias=bias),
                                get_activation_fn(activation),
                                nn.Dropout(dropout),
                                nn.Linear(d_ff, d_model, bias=bias))

        # Add & Norm
        self.dropout_ffn = nn.Dropout(dropout)
        if "batch" in norm.lower():
            self.norm_ffn = nn.Sequential(Transpose(1,2), nn.BatchNorm1d(d_model), Transpose(1,2))
        else:
            self.norm_ffn = nn.LayerNorm(d_model)
        # Cross Dimension Attention
        self.dim_sender = _MultiheadAttention(d_model, n_heads, d_k, d_v, attn_dropout=cross_attn_dropout, proj_dropout=cross_dropout)
        self.dim_receiver = _MultiheadAttention(d_model, n_heads, d_k, d_v, attn_dropout=cross_attn_dropout, proj_dropout=cross_dropout)
        self.router = nn.Parameter(torch.randn(q_len, factor, d_model))
        self.cross_dropout_attn = nn.Dropout(cross_dropout)
        self.cross_attn_norm1 = nn.LayerNorm(d_model)
        self.cross_attn_norm2 = nn.LayerNorm(d_model)
        self.cross_MLP = nn.Sequential(nn.Linear(d_model,d_ff),
                                        nn.GELU(),
                                        nn.Linear(d_ff,d_model))
        self.pre_norm = pre_norm
        self.store_attn = store_attn


    def forward(self, src:Tensor, n_vars, prev:Optional[Tensor]=None, key_padding_mask:Optional[Tensor]=None, attn_mask:Optional[Tensor]=None) -> Tensor:

        # Multi-Head attention sublayer
        if self.pre_norm:
            src = self.norm_attn1(src)
        ## Multi-Head attention

        src2,att_weight1 = self.self_attn(src, src, src, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
        
        ## Add & Norm
        src= src + self.dropout_attn(src2) # Add: residual connection with residual dropout
        if not self.pre_norm:
            src = self.norm_attn1(src)

        # Feed-forward sublayer
        if self.pre_norm:
            src = self.norm_ffn(src)
        ## Position-wise Feed-Forward
        src2 = self.ff(src)
        ## Add & Norm
        src = src + self.dropout_ffn(src2) # Add: residual connection with residual dropout
        if not self.pre_norm:
            src = self.norm_ffn(src)

    
        batch = src.shape[0]//n_vars
        dim_send = rearrange(src,'(b ts_d) patch_num d_model ->(b patch_num) ts_d  d_model',b=batch)
        batch_router = repeat(self.router,'patch_num factor d_model ->(repeat patch_num) factor d_model',repeat=batch)
        dim_buffer,att_weight2 = self.dim_sender(batch_router,dim_send,dim_send)
        dim_receive,att_weight3 = self.dim_receiver(dim_send,dim_buffer,dim_buffer)
        dim_enc = dim_send + self.cross_dropout_attn(dim_receive)
        dim_enc = self.cross_attn_norm1(dim_enc)
        dim_enc = dim_enc + self.cross_dropout_attn(self.cross_MLP(dim_enc))
        dim_enc = self.cross_attn_norm2(dim_enc)
        final_out = rearrange(dim_enc,'(b patch_num) ts_d d_model -> (b ts_d) patch_num d_model',b=batch) #shape=(batch_size,data_dim,patch_num,d_model)
        return final_out


class _MultiheadAttention(nn.Module):
    def __init__(self, d_model, n_heads, d_k=None, d_v=None, attn_dropout=0., proj_dropout=0., qkv_bias=True, lsa=False):
        """Multi Head Attention Layer
        Input shape:
            Q:       [batch_size (bs) x max_q_len x d_model]
            K, V:    [batch_size (bs) x q_len x d_model]
            mask:    [q_len x q_len]
        """
        super().__init__()
        d_k = d_model // n_heads if d_k is None else d_k
        d_v = d_model // n_heads if d_v is None else d_v

        self.n_heads, self.d_k, self.d_v = n_heads, d_k, d_v

        self.W_Q = nn.Linear(d_model, d_k * n_heads, bias=qkv_bias)
        self.W_K = nn.Linear(d_model, d_k * n_heads, bias=qkv_bias)
        self.W_V = nn.Linear(d_model, d_v * n_heads, bias=qkv_bias)

        # Scaled Dot-Product Attention (multiple heads)

        self.sdp_attn = _ScaledDotProductAttention(d_model, n_heads, attn_dropout=attn_dropout,lsa=lsa)

        # Poject output
        self.to_out = nn.Sequential(nn.Linear(n_heads * d_v, d_model), nn.Dropout(proj_dropout))


    def forward(self, Q:Tensor, K:Optional[Tensor]=None, V:Optional[Tensor]=None, prev:Optional[Tensor]=None,
                key_padding_mask:Optional[Tensor]=None, attn_mask:Optional[Tensor]=None):

        bs = Q.size(0)
        if K is None: K = Q
        if V is None: V = Q

        # Linear (+ split in multiple heads)
        q_s = self.W_Q(Q).view(bs, -1, self.n_heads, self.d_k).transpose(1,2)       # q_s    : [bs x n_heads x max_q_len x d_k]
        k_s = self.W_K(K).view(bs, -1, self.n_heads, self.d_k).permute(0,2,3,1)     # k_s    : [bs x n_heads x d_k x q_len] - transpose(1,2) + transpose(2,3)
        v_s = self.W_V(V).view(bs, -1, self.n_heads, self.d_v).transpose(1,2)       # v_s    : [bs x n_heads x q_len x d_v]

        # Apply Scaled Dot-Product Attention (multiple heads)
        output, attn_weights = self.sdp_attn(q_s, k_s, v_s, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
        # output: [bs x n_heads x q_len x d_v], attn: [bs x n_heads x q_len x q_len], scores: [bs x n_heads x max_q_len x q_len]

        # back to the original inputs dimensions
        output = output.transpose(1, 2).contiguous().view(bs, -1, self.n_heads * self.d_v) # output: [bs*f_dim x patch_num x d_model] contiguous() returns a tensor that is contiguous in memory;
        output = self.to_out(output)
        return output, attn_weights


class _ScaledDotProductAttention(nn.Module):
    r"""Scaled Dot-Product Attention module (Attention is all you need by Vaswani et al., 2017) with optional residual attention from previous layer
    (Realformer: Transformer likes residual attention by He et al, 2020) and locality self sttention (Vision Transformer for Small-Size Datasets
    by Lee et al, 2021)"""

    def __init__(self, d_model, n_heads, attn_dropout=0., lsa=False):
        super().__init__()
        self.attn_dropout = nn.Dropout(attn_dropout)
        
        head_dim = d_model // n_heads
        self.scale = nn.Parameter(torch.tensor(head_dim ** -0.5), requires_grad=lsa)
        self.lsa = lsa

    def forward(self, q:Tensor, k:Tensor, v:Tensor, prev:Optional[Tensor]=None, key_padding_mask:Optional[Tensor]=None, attn_mask:Optional[Tensor]=None):
        '''
        Input shape:
            q               : [bs x n_heads x max_q_len x d_k]
            k               : [bs x n_heads x d_k x seq_len]
            v               : [bs x n_heads x seq_len x d_v]
            prev            : [bs x n_heads x q_len x seq_len]
            key_padding_mask: [bs x seq_len]
            attn_mask       : [1 x seq_len x seq_len]
        Output shape:
            output:  [bs x n_heads x q_len x d_v]
            attn   : [bs x n_heads x q_len x seq_len]
            scores : [bs x n_heads x q_len x seq_len]
        '''

        # Scaled MatMul (q, k) - similarity scores for all pairs of positions in an input sequence
        attn_scores = torch.matmul(q, k) * self.scale      # attn_scores : [bs x n_heads x max_q_len x q_len]

        # Add pre-softmax attention scores from the previous layer (optional)
        if prev is not None: attn_scores = attn_scores + prev

        # Attention mask (optional)
        if attn_mask is not None:                                     # attn_mask with shape [q_len x seq_len] - only used when q_len == seq_len
            if attn_mask.dtype == torch.bool:
                attn_scores.masked_fill_(attn_mask, -np.inf)
            else:
                attn_scores += attn_mask

        # Key padding mask (optional)
        if key_padding_mask is not None:                              # mask with shape [bs x q_len] (only when max_w_len == q_len)
            attn_scores.masked_fill_(key_padding_mask.unsqueeze(1).unsqueeze(2), -np.inf)

        # normalize the attention weights
        attn_weights = F.softmax(attn_scores, dim=-1)                 # attn_weights   : [bs*f_dim x n_heads x max_q_len x q_len]
        attn_weights = self.attn_dropout(attn_weights)

        # compute the new values given the attention weights
        output = torch.matmul(attn_weights, v)                        # output: [bs x n_heads x max_q_len x d_v]

        # output = softmax(QK^T/sqrt(d_k))V ; attn_weights = softmax(QK^T/sqrt(d_k)) attn_scores = QK^T/sqrt(d_k)
        return output, attn_weights

