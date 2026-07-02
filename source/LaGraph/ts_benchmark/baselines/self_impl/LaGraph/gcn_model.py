import torch
import torch.nn as nn
from .graph_layer import GraphStack
from .decomp import MoEDecomposition

from .graphstack import GraphStack

class GCN_model(nn.Module):
    def __init__(self, win_size, enc_in, c_out, dropout,n_heads=2,individual=0, head_dropout=0.1, d_model=256, e_layers=3, patch_size=16, patch_stride=8, channel=55, d_ff=2048, topk=5, lat=10, activation='gelu', output_attention=True):
        super(GCN_model, self).__init__()
        self.output_attention = output_attention
        self.patch_size = patch_size
        self.patch_stride = patch_stride
        self.channel = channel
        self.win_size = win_size
        self.topk = topk
        self.individual = individual
        self.e_layers = e_layers
        self.lat = lat 
        self.encoder = GraphStack(num_layers=e_layers, enc_in=enc_in, d_model=d_model, d_ff=d_ff, win_size=win_size, n_heads=n_heads,d_state=16, d_conv=4,expand=2,topk=topk,dropout=dropout)
        self.proj = nn.Linear(c_out, d_model, bias=True)
        self.conv1 = nn.Conv1d(in_channels=win_size, out_channels=win_size, kernel_size=3, stride=1, padding=1)
        self.projection = nn.Linear(d_model, c_out, bias=True)
        self.conv2 = nn.Conv1d(in_channels=win_size, out_channels=win_size, kernel_size=3, stride=1, padding=1)
        self.projection1 = nn.Linear(c_out, c_out, bias=True)
        self.projection2 = nn.Linear(c_out, c_out, bias=True)
        self.decomp = MoEDecomposition(enc_in)

    def forward(self, x):
       
        B, L, M = x.shape #Batch win_size channel
        x,average = self.decomp(x)
        x = self.proj(x)
        average = self.conv1(average)
        average = self.projection1(average)
        average = self.conv2(average)
        average = self.projection2(average)
        x_rec,series,prior,attn = self.encoder(x)
        x_rec = self.projection(x_rec)
        x_rec = x_rec + average
        if self.output_attention:
            return x_rec,series,prior,attn
        else:
            return None
        

