# import torch
import torch.nn as nn
import torch
from torch_geometric.nn import GCNConv,GATConv,GATv2Conv,TransformerConv
from torch_geometric.nn import GraphConv, TopKPooling
from torch_geometric.nn import global_mean_pool as gap, global_max_pool as gmp
import torch.nn.functional as F
from layers import SAGPool

class InterNet(torch.nn.Module):
    def __init__(self,num_classes,num_features=20,nhid=128):
        super(InterNet, self).__init__()
        self.num_features = num_features
        self.nhid = nhid
        self.num_classes = num_classes
        self.pooling_ratio = 0.5
        self.dropout_ratio = 0.1

        self.lin=torch.nn.Linear(self.num_features, self.nhid//2)

        self.conv1 = GATConv(self.nhid//2, self.nhid, heads=3,edge_dim=2)
        self.conv2 = GATConv(nhid * 3, nhid, heads=1)  # 合并多头特征

        self.pool = SAGPool(self.nhid*3, ratio=self.pooling_ratio)

        self.lin1 = torch.nn.Linear(self.nhid*3*2, self.nhid)
        self.lin2 = torch.nn.Linear(self.nhid, self.nhid//2)
        self.lin3 = torch.nn.Linear(self.nhid//2, self. num_classes)

    def forward(self, data,m):
        x, edge_index, edge_attr, batch = data.x, data.edge_index, data.edge_attr,data.batch
        # import pdb;pdb.set_trace()

        x=F.elu(self.lin(x))
        x1 = F.relu(self.conv1(x, edge_index, edge_attr))
        # node_representations = x1
        node_representations = F.relu(self.conv2(x1, edge_index))
        # x =x1
        x, edge_index, _, batch, _ = self.pool(x1, edge_index, edge_attr, batch)
        x = torch.cat([gmp(x, batch), gap(x, batch)], dim=1)
        x = F.relu(self.lin1(x))
        x = F.dropout(x, p=self.dropout_ratio, training=self.training)
        x = F.relu(self.lin2(x))
        # x = F.log_softmax(self.lin3(x), dim=-1)
        x = self.lin3(x)
        x_logits = torch.repeat_interleave(x, repeats=m, dim=0)
        return x_logits, node_representations

class ByteCNN(nn.Module):
    def __init__(self,num_classes,input_channels=1,hidden_dim = 128,first_bytes=500):
        super(ByteCNN, self).__init__()
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=(1, 25), padding=(0, 12))
        self.pool1 = nn.MaxPool2d(kernel_size=(1, 3), stride=(1, 3), padding=(0, 1))
        self.conv2 = nn.Conv2d(32, 64, kernel_size=(1, 25), padding=(0, 12))
        self.pool2 = nn.MaxPool2d(kernel_size=(1, 3), stride=(1, 3), padding=(0, 1))
        # self.fc1 = nn.Linear(1 * 88 * 64, 1024)
        self.seq_length=first_bytes
        l1 = (first_bytes + 2 * 1 - 3) // 3 + 1  # 整除
        l2 = (l1 + 2 * 1 - 3) // 3 + 1  # 整除
        self.l2=l2
        self.fc1 = nn.Linear(1 * l2 * 64, hidden_dim)
        self.mlp =nn.Sequential(
            nn.Linear(hidden_dim, 512),  # 先降到512过渡
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )
        self.fc2 = nn.Linear(hidden_dim, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = x.view(-1, 1, 1, self.seq_length)
        x = torch.relu(self.conv1(x))
        x = self.pool1(x)
        x = torch.relu(self.conv2(x))
        x = self.pool2(x)
        x = x.view(-1, 1 * self.l2 * 64)
        x = self.fc1(x)
        x_represent=x

        x = torch.relu(x)
        x = self.dropout(x)
        x_logits = self.mlp(x)
        # x_logits = self.fc2(x)
        return x_logits,x_represent


class MultiModalClassifier(nn.Module):
    def __init__(self, num_classes=10, len_seq=20,intra_hid=128,inter_hid=128,first_bytes=500):
        super().__init__()
        # 流内特征分支
        self.intra_model = ByteCNN(num_classes=num_classes,input_channels=1,hidden_dim = intra_hid,first_bytes=first_bytes)
        # 流间特征分支
        self.inter_model = InterNet(num_classes=num_classes,num_features=len_seq,nhid=inter_hid)

        self.fusion_classifier = nn.Sequential(
            nn.Linear(intra_hid + inter_hid, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, spectrogram, graph_image,m):
        intra_logits,intra_fea = self.intra_model(spectrogram)
        inter_logits,inter_fea = self.inter_model(graph_image,m)
        # import pdb;pdb.set_trace()

        # 特征融合与分类
        combined = torch.cat([intra_fea, inter_fea], dim=1)
        fusion_logits = self.fusion_classifier(combined)
        # fusion_probs = F.softmax(fusion_logits, dim=1)

        return (fusion_logits, intra_logits, inter_logits)



