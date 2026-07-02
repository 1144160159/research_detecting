from torch_geometric.data import Data, Batch
from torch.utils.data import Dataset, DataLoader
import torch

class GraphFlowDataset(Dataset):
    def __init__(self, data_list,first_bytes):
        """
        spectrograms: 列表，每个元素是一个包含m个频谱图的列表
        graphs: 列表，每个元素是一个torch_geometric.Data对象
        labels: 列表，每个元素是图级标签
        """
        self.intra = [item['spectrograms'][:,:first_bytes] for item in data_list]  # 形状: [num_samples, m, channels, H, W]
        self.graphs = [item['graph'] for item in data_list]  # 形状: [num_samples, Data(x, edge_index, ...)]
        self.labels = [item['label'] for item in data_list]  # 形状: [num_samples]


    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        # 返回一个样本的所有模态数据
        return self.intra[idx], self.graphs[idx], self.labels[idx]  # 标签


    def collate_fn(self, batch):
        # 合并多个图的数据
        intra_list, graph_list,label_list = zip(*batch)

        # 流内特征：展平为 (batch_size*m,1,H,W)
        intra_batch = torch.cat(intra_list, dim=0)
        # 将频谱图数据转换为float32类型
        intra_batch = intra_batch.float()

        # 流间特征：合并为PyG Batch对象
        graph_batch = Batch.from_data_list(graph_list)

        # 标签：合并为一个张量
        label_batch = torch.tensor(label_list)

        return intra_batch, graph_batch, label_batch

