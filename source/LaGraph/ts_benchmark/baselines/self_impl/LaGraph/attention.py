import numpy as np
import torch
import math
from torch import nn
import torch.nn.functional as F
from .channel_mask import channel_mask_generator


class OrdAttention(nn.Module):
    def __init__(self, win_size, model_dim, atten_dim, head_num, dropout, residual):
        super(OrdAttention, self).__init__()
        self.atten_dim = atten_dim
        self.head_num = head_num
        self.residual = residual
        self.win_size = win_size
        self.W_Q = nn.Linear(model_dim, self.atten_dim * self.head_num, bias=True)
        self.W_K = nn.Linear(model_dim, self.atten_dim * self.head_num, bias=True)
        self.W_V = nn.Linear(model_dim, self.atten_dim * self.head_num, bias=True)
        self.qkv = nn.Conv1d(self.win_size, self.win_size * 3, kernel_size=1, bias=True)
        self.qkv_dwconv = nn.Conv1d(self.win_size * 3, self.win_size * 3, kernel_size=3, stride=1, padding=1, groups=self.win_size * 3, bias=True)
        self.fc = nn.Linear(self.atten_dim * self.head_num, model_dim, bias=True)

        self.dropout = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(model_dim)
        self.mask = channel_mask_generator(self.atten_dim, self.win_size)

    def forward(self, Q, K, V):
        residual = Q.clone()
        qkv = self.qkv_dwconv(self.qkv(Q))
        Q, K, V = qkv.chunk(3, dim=1)
        Q = self.W_Q(Q).view(Q.size(0), Q.size(1), self.head_num, self.atten_dim)
        K = self.W_K(K).view(K.size(0), K.size(1), self.head_num, self.atten_dim)
        V = self.W_V(V).view(V.size(0), V.size(1), self.head_num, self.atten_dim)

        Q, K, V = Q.transpose(1, 2), K.transpose(1, 2), V.transpose(1, 2)
        scores = torch.matmul(Q, K.transpose(-1, -2)) / np.sqrt(self.atten_dim)
        mask = self.mask(K)
        large_negative = -math.log(1e10)
        attention_mask = torch.where(mask == 0, large_negative, 0)
        scores = scores * mask + attention_mask
        attn = nn.Softmax(dim=-1)(scores)
        context = torch.matmul(attn, V)
        context = context.transpose(1, 2)
        context = context.reshape(residual.size(0), residual.size(1), -1)
        output = self.dropout(self.fc(context))

        if self.residual:
            return self.norm(output + residual), attn
        else:
            return self.norm(output), attn