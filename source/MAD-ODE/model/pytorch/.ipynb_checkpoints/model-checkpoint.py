import torch
import torch.nn as nn
from torch.nn import functional as F
from model.pytorch.cell import DCGRUCell
import numpy as np
from model.pytorch.similarity import batch_cosine_similarity,batch_dot_similarity
import math
import random
import tqdm
import pandas as pd
from sklearn import preprocessing
import torch.optim as optim
import torch.utils as utils
import logging
import os
import argparse
from script import dataloader, utility, earlystopping
from model import models
from modelode import ODEGCN
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def cosine_similarity_torch(x1, x2=None, eps=1e-8):
    x2 = x1 if x2 is None else x2
    w1 = x1.norm(p=2, dim=1, keepdim=True)
    w2 = w1 if x2 is x1 else x2.norm(p=2, dim=1, keepdim=True)
    return torch.mm(x1, x2.t()) / (w1 * w2.t()).clamp(min=eps)

def sample_gumbel(shape, eps=1e-20):
    U = torch.rand(shape).to(device)
    return -torch.autograd.Variable(torch.log(-torch.log(U + eps) + eps))

def gumbel_softmax_sample(logits, temperature, eps=1e-10):
    sample = sample_gumbel(logits.size(), eps=eps)
    y = logits + sample
    return F.softmax(y / temperature, dim=-1)

def gumbel_softmax(logits, temperature, hard=False, eps=1e-10):
  """Sample from the Gumbel-Softmax distribution and optionally discretize.
  Args:
    logits: [batch_size, n_class] unnormalized log-probs
    temperature: non-negative scalar
    hard: if True, take argmax, but differentiate w.r.t. soft sample y
  Returns:
    [batch_size, n_class] sample from the Gumbel-Softmax distribution.
    If hard=True, then the returned sample will be one-hot, otherwise it will
    be a probabilitiy distribution that sums to 1 across classes
  """
  y_soft = gumbel_softmax_sample(logits, temperature=temperature, eps=eps)
  if hard:
      shape = logits.size()
      _, k = y_soft.data.max(-1)
      y_hard = torch.zeros(*shape).to(device)
      y_hard = y_hard.zero_().scatter_(-1, k.view(shape[:-1] + (1,)), 1.0)
      y = torch.autograd.Variable(y_hard - y_soft.data) + y_soft
  else:
      y = y_soft
  return y

class Seq2SeqAttrs:
    def __init__(self, **model_kwargs):
        #self.adj_mx = adj_mx
        self.max_diffusion_step = int(model_kwargs.get('max_diffusion_step', 2))
        self.cl_decay_steps = int(model_kwargs.get('cl_decay_steps', 1000))
        self.filter_type = model_kwargs.get('filter_type', 'laplacian')
        self.num_nodes = int(model_kwargs.get('num_nodes', 1))
        self.num_rnn_layers = int(model_kwargs.get('num_rnn_layers', 1))
        self.rnn_units = int(model_kwargs.get('rnn_units'))
        self.hidden_state_size = self.num_nodes * self.rnn_units
        self.Kt = 3
        self.stblock_num = 2
        self.Ks = 3
        self.graph_conv_type = 'graph_conv'
        self.gso_type = 'sym_norm_lap'
        self.enable_bias = True
        self.droprate = 0.5
        self.weight_decay_rate = 0.0005
        self.step_size = 10
        self.gamma = 0.95
        self.n_his = int(model_kwargs.get('seq_len'))#历史窗口 要改
        self.act_func = 'glu'
        self.horizon = int(model_kwargs.get('horizon', 1))
        
        
class EncoderModel(nn.Module, Seq2SeqAttrs):
    def __init__(self, **model_kwargs):
        nn.Module.__init__(self)
        Seq2SeqAttrs.__init__(self, **model_kwargs)
        self.input_dim = int(model_kwargs.get('input_dim', 1))
        self.seq_len = int(model_kwargs.get('seq_len'))  # for the encoder
        self.dcgru_layers = nn.ModuleList(
            [DCGRUCell(self.rnn_units, self.max_diffusion_step, self.num_nodes,
                       filter_type=self.filter_type) for _ in range(self.num_rnn_layers)])

    def forward(self, inputs, adj, hidden_state=None):
        """
        Encoder forward pass.
        :param inputs: shape (batch_size, self.num_nodes * self.input_dim)
        :param hidden_state: (num_layers, batch_size, self.hidden_state_size)
               optional, zeros if not provided
        :return: output: # shape (batch_size, self.hidden_state_size)
                 hidden_state # shape (num_layers, batch_size, self.hidden_state_size)
                 (lower indices mean lower layers)
        """
        batch_size, _ = inputs.size()  #64,27
        if hidden_state is None:
            hidden_state = torch.zeros((self.num_rnn_layers, 12, self.hidden_state_size),
                                       device=device)  #1,64,1728
        hidden_states = []
        output = inputs
        for layer_num, dcgru_layer in enumerate(self.dcgru_layers):
            next_hidden_state = dcgru_layer(output, hidden_state[layer_num], adj)
            hidden_states.append(next_hidden_state)
            output = next_hidden_state

        return output, torch.stack(hidden_states)  # runs in O(num_layers) so not too slow
        #output64,1728,torch.stack(hidden_states)1,64,1728，内容是一样的

class DecoderModel(nn.Module, Seq2SeqAttrs):
    def __init__(self, **model_kwargs):
        # super().__init__(is_training, adj_mx, **model_kwargs)
        nn.Module.__init__(self)
        Seq2SeqAttrs.__init__(self, **model_kwargs)
        self.output_dim = int(model_kwargs.get('output_dim', 1))
        self.horizon = int(model_kwargs.get('horizon', 1))  # for the decoder
        self.projection_layer = nn.Linear(self.rnn_units, self.output_dim)
        self.dcgru_layers = nn.ModuleList(
            [DCGRUCell(self.rnn_units, self.max_diffusion_step, self.num_nodes,
                       filter_type=self.filter_type) for _ in range(self.num_rnn_layers)])

    def forward(self, inputs, adj, hidden_state=None):
        """
        :param inputs: shape (batch_size, self.num_nodes * self.output_dim)
        :param hidden_state: (num_layers, batch_size, self.hidden_state_size)
               optional, zeros if not provided
        :return: output: # shape (batch_size, self.num_nodes * self.output_dim)
                 hidden_state # shape (num_layers, batch_size, self.hidden_state_size)
                 (lower indices mean lower layers)
        """
        hidden_states = []
        output = inputs
        for layer_num, dcgru_layer in enumerate(self.dcgru_layers):
            next_hidden_state = dcgru_layer(output, hidden_state[layer_num], adj)
            hidden_states.append(next_hidden_state)
            output = next_hidden_state

        projected = self.projection_layer(output.view(-1, self.rnn_units))
        output = projected.view(-1, self.num_nodes * self.output_dim)

        return output, torch.stack(hidden_states)


class     GTSModel(nn.Module, Seq2SeqAttrs):
    def __init__(self, temperature, logger,knnadj, **model_kwargs):
        super().__init__()
        self.knnadj = knnadj
        Seq2SeqAttrs.__init__(self, **model_kwargs)
        self.encoder_model = EncoderModel(**model_kwargs)
        self.decoder_model = DecoderModel(**model_kwargs)
        self.cl_decay_steps = int(model_kwargs.get('cl_decay_steps', 1000))
        self.use_curriculum_learning = bool(model_kwargs.get('use_curriculum_learning', False))
        self._logger = logger
        self.temperature = temperature
        self.dim_fc = int(model_kwargs.get('dim_fc', False))    #dim_fc: 383552
        self.embedding_dim = 100
        self.conv1 = torch.nn.Conv1d(1, 8, 10, stride=1)  # .to(device)
        self.conv2 = torch.nn.Conv1d(8, 16, 10, stride=1)  # .to(device)
        self.hidden_drop = torch.nn.Dropout(0.2)
        self.fc = torch.nn.Linear(self.dim_fc, self.embedding_dim)     #dim_fc: 7919712/143712
        self.bn1 = torch.nn.BatchNorm1d(8)
        self.bn2 = torch.nn.BatchNorm1d(16)
        self.bn3 = torch.nn.BatchNorm1d(self.embedding_dim)
        self.fc_out = nn.Linear(self.embedding_dim * 2, self.embedding_dim)
        self.fc_cat = nn.Linear(self.embedding_dim, 2)
        self.Ko = self.n_his - (self.Kt - 1) * 2 * self.stblock_num
        self.wind = self.horizon
        blocks = []
        blocks.append([1])
        for l in range(self.stblock_num):
            blocks.append([64, 16, 64])
        if self.Ko == 0:
            blocks.append([128])
        elif self.Ko > 0:
            blocks.append([128, 128])
        blocks.append([self.horizon])
        # blocks.append([12])
        self.blocks = blocks
        def encode_onehot(labels):
            classes = set(labels)
            classes_dict = {c: np.identity(len(classes))[i, :] for i, c in
                            enumerate(classes)}
            labels_onehot = np.array(list(map(classes_dict.get, labels)),
                                     dtype=np.int32)
            return labels_onehot
        # Generate off-diagonal interaction graph
        off_diag = np.ones([self.num_nodes, self.num_nodes])
        rel_rec = np.array(encode_onehot(np.where(off_diag)[0]), dtype=np.float32)
        rel_send = np.array(encode_onehot(np.where(off_diag)[1]), dtype=np.float32)
        self. rel_rec = torch.FloatTensor(rel_rec).to(device)
        self.rel_send = torch.FloatTensor(rel_send).to(device)
        
        self.logits = .8 * torch.ones(self.num_nodes ** 2, 2).to(device)
        self.x = self.logits
        self.logits[:, 1] = 0
        self.adj = torch.nn.functional.gumbel_softmax(self.logits, hard=True)

        self.adj = self.adj[:, 0].clone().reshape(self.num_nodes, -1)
        self.mask = torch.eye(self.num_nodes, self.num_nodes).bool().to(device)
        self.adj.masked_fill_(self.mask, 0)  #对角线填充0
        if self.graph_conv_type == 'cheb_graph_conv':
            self.model1 = models.STGCNChebGraphConv(self.Kt, self.Ks, self.act_func, self.graph_conv_type, self.adj, self.enable_bias, self.droprate, self.n_his, self.blocks, self.num_nodes)
        else:
            self.model1 = models.STGCNGraphConv(self.Kt, self.Ks, self.act_func, self.graph_conv_type, self.adj, self.enable_bias, self.droprate, self.n_his, self.blocks, self.num_nodes)
        self.model1.to(device)
        self.nodevec1 = nn.Parameter(torch.randn(self.num_nodes, 10).to(device),requires_grad=True).to(device)
        self.nodevec2 = nn.Parameter(torch.randn(10, self.num_nodes).to(device), requires_grad=True).to(device)
        self.adp = F.softmax(F.relu(torch.mm(self.nodevec1, self.nodevec2)), dim=1).detach().to(device)
        self.net = ODEGCN(num_nodes=self.num_nodes, 
                num_features=1, 
                num_timesteps_input=12, 
                num_timesteps_output=self.horizon, 
                A_sp_hat=self.knnadj, 
                A_se_hat=self.adj)
        self.net.to(device)
        

    def _compute_sampling_threshold(self, batches_seen):
        return self.cl_decay_steps / (
                self.cl_decay_steps + np.exp(batches_seen / self.cl_decay_steps))

    def encoder(self, inputs, adj):
        """
        Encoder forward pass
        :param inputs: shape (seq_len, batch_size, num_sensor * input_dim)
        :return: encoder_hidden_state: (num_layers, batch_size, self.hidden_state_size)
        """
        encoder_hidden_state = None
        for t in range(self.encoder_model.seq_len):
            _, encoder_hidden_state = self.encoder_model(inputs[t], adj, encoder_hidden_state)

        return encoder_hidden_state  #1,64,1728

    def decoder(self, encoder_hidden_state, adj, labels=None, batches_seen=None):
        """
        Decoder forward pass
        :param encoder_hidden_state: (num_layers, batch_size, self.hidden_state_size)
        :param labels: (self.horizon, batch_size, self.num_nodes * self.output_dim) [optional, not exist for inference]
        :param batches_seen: global step [optional, not exist for inference]
        :return: output: (self.horizon, batch_size, self.num_nodes * self.output_dim)
        """
        batch_size = encoder_hidden_state.size(1)
        go_symbol = torch.zeros((batch_size, self.num_nodes * self.decoder_model.output_dim),
                                device=device)
        decoder_hidden_state = encoder_hidden_state
        decoder_input = go_symbol

        outputs = []

        for t in range(self.decoder_model.horizon):
            decoder_output, decoder_hidden_state = self.decoder_model(decoder_input, adj,
                                                                      decoder_hidden_state)
            decoder_input = decoder_output
            outputs.append(decoder_output)
            if self.training and self.use_curriculum_learning:
                c = np.random.uniform(0, 1)
                if c < self._compute_sampling_threshold(batches_seen):
                    decoder_input = labels[t]
        outputs = torch.stack(outputs)
        return outputs


    def forward(self, label, inputs, node_feas, temp, gumbel_soft, labels=None, batches_seen=None,k=None):
        """
        :param inputs: shape (seq_len, batch_size, num_sensor * input_dim)
        :param labels: shape (horizon, batch_size, num_sensor * output)
        :param batches_seen: batches seen till now
        :return: output: (self.horizon, batch_size, self.num_nodes * self.output_dim)
        """
        self.adp = F.softmax(F.relu(torch.mm(self.nodevec1, self.nodevec2)), dim=1).to(device)
        # '''特征提取器'''
        # x = inputs.transpose(1, 0)
        # x = x.view(self.num_nodes, 1, -1)
        # # x = node_feas.transpose(1, 0).view(self.num_nodes, 1, -1)   #x(207,1,23990)，node_feas(23990,207)
        # x = self.conv1(x)   #x(207,8,23981)
        # x = F.relu(x)
        # x = self.bn1(x)   #归一化
        # # x = self.hidden_drop(x)
        # x = self.conv2(x)    #x([207, 16, 23972])
        # x = F.relu(x)
        # x = self.bn2(x)
        # x = x.view(self.num_nodes, -1)  #torch.Size([207, 383552])
        # x = self.fc(x)
        # x = F.relu(x)   #torch.Size([207, 100])
        # x = self.bn3(x)
        #
        # knn_metric = 'cosine'
        # from sklearn.neighbors import kneighbors_graph
        # g = kneighbors_graph(x.cpu().detach().numpy(), k, metric=knn_metric)
        # g = np.array(g.todense(), dtype=np.float32) #55,55
        # adj_knn = torch.Tensor(g).to(device)      #adj_mx是knn图的邻接矩阵
        #
        # '''链路预测器'''
        # receivers = torch.matmul(self.rel_rec, x)
        # senders = torch.matmul(self.rel_send, x)
        # x = torch.cat([senders, receivers], dim=1)   #torch.cat拼接函数（concatenate）
        # x = torch.relu(self.fc_out(x))
        # x = self.fc_cat(x)    #torch.Size([42849, 2])
        # cd = x.softmax(-1)[:, 0]
        # adj = gumbel_softmax(x, temperature=temp, hard=True)

        
        
        n_vertex = self.num_nodes
        
        
#         logits1 = .8 * torch.ones(num_nodes ** 2, 2).to(device)
#         x1 = logits1
#         logits1[:, 1] = 0
#         adj1 = torch.nn.functional.gumbel_softmax(logits1, hard=True)

#         adj1 = adj1[:, 0].clone().reshape(self.num_nodes, -1)
#         mask1 = torch.eye(self.num_nodes, self.num_nodes).bool().to(device)
#         adj1.masked_fill_(mask1, 0)  #对角线填充0
        
        
        
        
        
        inputs1 = inputs.unsqueeze(0)#1 12 64 127
        inputs1 = inputs1.permute(2, 3, 1, 0)#batch * N * his_length * features
        # inputs1 = [inputs1,self.adp]
        # outputs1 = self.model1(inputs1).view(len(inputs1), self.wind, -1)
        # # outputs1 = torch.squeeze(model1(inputs1))
        # outputs1 = outputs1.permute(1, 0, 2)
        # # outputs1 = outputs1[0:self.wind, ...]
        encoder_hidden_state = self.encoder(inputs, self.adp)
        # self._logger.debug("Encoder complete, starting decoder")
        outputs2 = self.decoder(encoder_hidden_state, self.adp, labels, batches_seen=batches_seen)
        # self._logger.debug("Decoder complete")#12 64 127
        # # temp = [outputs1, outputs2]
        # # temp1 = torch.cat(temp, dim=0)
        # # re = temp1.permute(1, 0, 2)
        # # convfc = nn.Conv1d(in_channels=4, out_channels=2, kernel_size=1).to(device)
        # # outputs = convfc(re)#64 12 127
        # # outputs = outputs.permute(1, 0, 2)
        
        
        outputs = self.net(inputs1).view(len(inputs1), self.num_nodes, -1)
        outputs1 = outputs.permute(2,0,1)
        
        if batches_seen == 0:
            self._logger.info(
                "Total trainable parameters {}".format(count_parameters(self))
            )
        # array = adj.cpu().numpy()
        array = self.adj.cpu().detach().numpy()
        return self.adp,outputs,outputs1, self.x.softmax(-1)[:, 0].clone().reshape(self.num_nodes, -1),array#,adj_knn     #out为预测时序值
