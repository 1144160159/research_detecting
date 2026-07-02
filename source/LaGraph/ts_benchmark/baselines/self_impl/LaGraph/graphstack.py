import torch
import torch.nn as nn
import torch.nn.functional as F


from .attention import OrdAttention
from .graph_layer import GraphLayer
class GraphStack(nn.Module):
    def __init__(self, num_layers, enc_in, d_model, d_ff, win_size, n_heads,d_state, d_conv,expand, topk,dropout):
        super().__init__()
        self.encoder_layers = nn.ModuleList([
            Encoder(d_model=d_model, enc_in=enc_in, d_ff=d_ff, win_size=win_size, n_heads=n_heads,d_state=d_state, d_conv=d_conv,expand=expand,topk=topk,dropout=dropout)
            for _ in range(num_layers)
        ])
        self.num_layers = num_layers
    
    def forward(self, x):
        
        for i in range(self.num_layers):
            
            x, series,prior,attn = self.encoder_layers[i](x)
        return x , series , prior, attn

class Encoder(nn.Module):
    def __init__(self, d_model, enc_in, d_ff, win_size, n_heads, d_state, d_conv,expand,topk,dropout):
        super().__init__()
        
        self.ordinary_attention = OrdAttention(win_size=win_size, model_dim=d_model, atten_dim=32, head_num=n_heads, dropout=dropout, residual=True)
        self.gcn = GraphLayer(d_model,d_model, win_size, topk, 0.0)
        self.liner1 = nn.Linear(d_model, d_model, bias=True)
        self.liner2 = nn.Linear(d_model, d_model, bias=True)
        self.dropout = nn.Dropout(dropout)
        self.activation = F.gelu
        self.d_ff = d_ff
        self.norm = nn.LayerNorm(d_model)
    def forward(self, x):
        x , series , prior =self.gcn(x)
        
        x = self.norm(x)
        x, attn = self.ordinary_attention(x, x, x)
        
        x = self.activation(self.liner1(x))
        x = self.dropout(self.liner2(x))

        return x,series,prior,attn