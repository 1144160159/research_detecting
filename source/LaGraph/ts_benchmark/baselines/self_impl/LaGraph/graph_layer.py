import torch
import math
import torch.nn as nn
import torch.nn.functional as F


class nconv(nn.Module):
    def __init__(self):
        super(nconv, self).__init__()
        
    def forward(self, x, A):
        x = torch.einsum('bfn,bnv->bfv', (x, A))
        return x.contiguous()


class linear(nn.Module):
    def __init__(self, c_in, c_out):
        super(linear, self).__init__()
        self.mlp = torch.nn.Conv1d(c_in, c_out, kernel_size=1, padding=0, stride=1, bias=True)
        
    def forward(self, x):
        x = self.mlp(x)
        return x

class GCN(nn.Module):
    def __init__(self, c_in, c_out, dropout, support_len=3, order=3):
        super(GCN, self).__init__()
        self.nconv = nconv()
        c_in = (order + 1) * c_in
        self.mlp = linear(c_in, c_out)
        self.dropout = nn.Dropout(dropout)
        self.order = order

    def forward(self, x, support):
        out = [x]
        for a in support:
            x1 = self.nconv(x, a)
            out.append(x1)
            for k in range(2, self.order + 1):
                x2 = self.nconv(x1, a)
                out.append(x2)
                x1 = x2

        h = torch.cat(out, dim=1)
        h = self.mlp(h)
        h = F.relu(h)
        return h



class GraphLayer(nn.Module):
    def __init__(self, enc_in,d_model, win_size, topk, dropout):
        super(GraphLayer, self).__init__()
        self.enc_in = enc_in
        self.d_model = d_model
        self.dropout = dropout
        self.nodedim = topk
        self.win_size = win_size
        self.nodevector_1 = nn.Parameter(torch.randn(self.win_size, self.nodedim))
        self.nodevector_2 = nn.Parameter(torch.randn(self.nodedim, self.win_size))

        self.nodevec_gate1 = nn.Sequential(
                nn.Linear(self.enc_in + self.nodedim, 1),
                nn.Tanh(),
                nn.ReLU())

        self.nodevec_gate2 = nn.Sequential(
            nn.Linear(self.enc_in + self.nodedim, 1),
            nn.Tanh(),
            nn.ReLU())

        self.nodevec_linear1 = nn.Linear(self.enc_in, self.nodedim)
        self.nodevec_linear2 = nn.Linear(self.enc_in, self.nodedim)
        self.proj = nn.Linear(self.enc_in,self.win_size)
        self.gcn = GCN(self.enc_in, self.enc_in, self.dropout)
        self.win_size = win_size
        self.distances = torch.zeros((self.win_size, self.win_size)).cuda()
        for i in range(self.win_size):
            for j in range(self.win_size):
                self.distances[i][j] = abs(i - j)

    def forward(self, x):
        B, _, _ = x.size()
        nodevector_1 = self.nodevector_1.view(1, self.win_size, self.nodedim).repeat(B, 1, 1)
        nodevector_2 = self.nodevector_2.view(1, self.nodedim, self.win_size).repeat(B, 1, 1)
        x_gate_1 = self.nodevec_gate1(torch.cat([x, nodevector_1], dim=-1))
        x_gate_2 = self.nodevec_gate2(torch.cat([x, nodevector_2.permute(0, 2, 1)], dim=-1))

        x_p1 = x_gate_1 * self.nodevec_linear1(x)
        x_p2 = x_gate_2 * self.nodevec_linear2(x)

        nodevector_1 = nodevector_1 + x_p1
        nodevector_2 = nodevector_2 + x_p2.permute(0, 2, 1)
        adp = torch.matmul(nodevector_1, nodevector_2)
        adp = F.softmax(adp, dim=-1)
        adjacency_matrix = adp
        sigma = self.proj(x)
        sigma = torch.sigmoid(sigma * 5) + 1e-5
        sigma = torch.pow(3, sigma) - 1
        prior = self.distances.unsqueeze(0).repeat(sigma.shape[0], 1, 1).cuda()
        prior = 1.0 / (sigma) * torch.exp(-prior / sigma)
        adp = [adp]
        x = x.permute(0, 2, 1)
        x = self.gcn(x, adp) + x 
        x = x.permute(0, 2, 1)
        return x, adjacency_matrix, prior

class GraphStack(nn.Module):
    def __init__(self, num_layers, enc_in, d_model, d_ff, win_size, d_state, d_conv,expand, topk,dropout=0.1):
        super().__init__()
        self.glayers = nn.ModuleList([
            GraphLayer(d_model,d_model, win_size, topk, 0.1)
            for _ in range(num_layers)
        ])
        self.num_layers = num_layers
        self.norm1 = nn.LayerNorm(d_model)
    def forward(self, x):
        
        for i in range(self.num_layers):
            x,_ = self.glayers[i](x)
            x = self.norm1(x)
        return x 
