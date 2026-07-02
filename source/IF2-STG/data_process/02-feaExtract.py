import numpy as np
import librosa
from scipy.signal import stft
# from scipy import signal
import torch
from torch_geometric.data import Data
import pickle
from tqdm import tqdm
from collections import defaultdict
from sklearn.model_selection import train_test_split
import os
import glob
from collections import Counter


def bytes_seq(byte_sequence, target_length=500):

    # 补零至500字节
    byte_sequence = byte_sequence[:target_length]
    if len(byte_sequence) < target_length:
        byte_sequence = np.pad(byte_sequence, (0, target_length - len(byte_sequence)), 'constant')
    return torch.tensor(byte_sequence)


def normalize_lists(lenlist, timelist,target_length=20):
    """
    将列表中的每个子列表统一到指定长度：
    """
    duration = (timelist[-1]-timelist[0]) if len(timelist)>1 else 0

    truncated = lenlist[:target_length]
    # 补足长度
    padded = truncated + [0] * (target_length - len(truncated))
    ##计算6个统计特征
    # 转换为numpy数组
    arr = np.array(lenlist)
    # 分离前向和后向数据包
    forward = arr[arr > 0]  # 前向(正值)
    backward = -arr[arr < 0]  # 后向(负值取正)
    all_packets = np.abs(arr)  # 整体(全部取绝对值)

    stati_fea_top6 = [np.mean(all_packets), np.percentile(forward, 40),np.percentile(all_packets, 70),
                      np.percentile(forward, 50),np.percentile(all_packets, 60),  np.percentile(all_packets, 50)]
    ##stc-wf论文原配置
    # mean_backward = np.mean(backward) if len(backward) > 0 else 0  # 默认值设为0
    # stati_fea_top6 = [np.max(forward), len(all_packets), np.percentile(forward, 90),
    #                   len(backward), np.percentile(forward, 80), np.mean(mean_backward)]

    ##加上时间统计特征
    # stati_fea_top6 = [duration, np.percentile(all_packets, 50), np.percentile(all_packets, 70),
    #                   np.mean(all_packets), np.percentile(forward, 60), np.percentile(all_packets, 60)]

    padded.extend(stati_fea_top6)
    # import pdb;pdb.set_trace()

    return padded

def build_graph(flow_group, concurrency_threshold=0.01):
    # 初始化图数据
    node_features = []
    edge_mat = []
    edge_attr = []
    labels = []
    dst_dict = []  # 记录每个节点的目的地
    src_dict = []

    # 为每个流分配节点索引并提取特征
    node_indices = {flow[0]: idx for idx, flow in enumerate(flow_group)}
    for idx,flow in enumerate(flow_group):
        src_ip, src_port, dst_ip, dst_port, proto = flow[0]
        node_features.append(normalize_lists(flow[1]['lengths'],flow[1]['timestamps']))
        labels.append(flow[1]['label'])
        dst_dict.append(dst_ip)
        src_dict.append(src_ip)

    # --- 2. 将流分组成并发组 ---
    groups = []
    current_group = [flow_group[0]]
    for flow in flow_group[1:]:
        # 如果与当前组最后一条流的时间差 < 阈值 且源IP目的IP有交集，加入当前组
        # if (flow[1]['start_time'] - current_group[0][1]['start_time'] < concurrency_threshold) and (flow[0][2] == current_group[0][0][2]):
        if flow[1]['start_time'] - current_group[0][1]['start_time'] < concurrency_threshold:
            # # 检查IP地址集合是否有交集
            a_ips = {flow[0][0],flow[0][2]}
            b_ips = {current_group[0][0][0], current_group[0][0][2]}
            if a_ips.intersection(b_ips):
                current_group.append(flow)

        else:
            groups.append(current_group)
            current_group = [flow]
    groups.append(current_group)  # 添加最后一个组

    # --- 3. 构建组内边（并发流全连接）---
    for group in groups:
        # 将流转换为节点索引
        node_ids = [node_indices[f[0]] for f in group]
        # 组内全连接（无向边）
        for i in range(len(node_ids)):
            for j in range(i + 1, len(node_ids)):
                # 双向边
                edge_mat.extend([[node_ids[i], node_ids[j]], [node_ids[j], node_ids[i]]])
                edge_attr.extend([[1.0, 1.0], [1.0, 1.0]])

    group_nodes = []
    for group in groups:
        if len(group) == 0:
            continue
        node_ids = [node_indices[f[0]] for f in group]
        group_nodes.append(node_ids)

    # 连接相邻组的所有节点
    for i in range(len(group_nodes) - 1):
        prev_group = group_nodes[i]  # 前驱组的所有节点
        next_group = group_nodes[i + 1]  # 后继组的所有节点

        # 计算时间差（使用前驱组最后一个节点和后继组第一个节点的时间差）
        time_gap = np.exp(-(flow_group[next_group[0]][1]['start_time'] -
                            flow_group[prev_group[-1]][1]['start_time']))

        # 为前驱组每个节点连接后继组每个节点
        for src_node in prev_group:
            for dst_node in next_group:
                # # 检查目的是否相同IP对
                # same_dst = 1.0 if (dst_dict[src_node] == dst_dict[dst_node]) else 0.0

                # 检查IP地址集合是否有交集
                src_ips = {src_dict[src_node], dst_dict[src_node]}
                dst_ips = {src_dict[dst_node], dst_dict[dst_node]}
                same_dst = 1.0 if src_ips.intersection(dst_ips) else 0.0

                # 添加单向边
                edge_mat.append([src_node, dst_node])
                edge_attr.append([time_gap, same_dst])
                # edge_attr.append([time_gap])

    # 转换为 numpy 数组（可选）
    edge_mat = torch.tensor(edge_mat, dtype=torch.long).T
    edge_attr = torch.tensor(edge_attr, dtype=torch.float)

    # 创建Data对象
    data = Data(
        x=torch.tensor(node_features, dtype=torch.float),
        edge_index=edge_mat,
        edge_attr=edge_attr,
        y = labels[0]
    )
    # import pdb;pdb.set_trace()
    return data

def process_flow_groups(flow_dict, m=8,target_length=500,concur_threshold=0.01):
    """
    处理原始数据流字典，生成:
    - spectrograms: (N, m, 1, H, W)
    - graphs: List[PyG Data]
    - labels: (N,)
    """
    samples = []
    # spectrograms, graphs, labels = [], [], []
    # import pdb;pdb.set_trace()

    # 按开始时间排序
    flows_sorted = sorted(flow_dict.items(), key=lambda item: item[1]['start_time'])
    flow_items = list(flows_sorted)
    # import pdb;pdb.set_trace()

    for i in tqdm(range(0, len(flow_items), m)):
        group = flow_items[i:i + m]
        if len(group) < m:
            continue  # 跳过不足m条的组

        # 生成字节序列组
        group_specs = torch.stack([bytes_seq(f[1]['bytes'], target_length=target_length) for f in group])
        # import pdb;pdb.set_trace()

        # 构建图数据
        graph = build_graph(group,concur_threshold)  # 使用前文的build_graph函数

        # 确定标签（多数投票）
        group_labels = [f[1]['label'] for f in group]
        majority_label = max(set(group_labels), key=group_labels.count)

        # 添加到样本列表
        samples.append({
            'spectrograms': group_specs,  # (flows_per_graph, 1, H, W)
            'graph': graph,
            'label': majority_label
        })
        # import pdb;pdb.set_trace()

    return samples


def split_train_test(samples, test_size=0.2, random_state=42):

    train_samples, test_samples = train_test_split(
        samples, test_size=test_size, random_state=random_state,
        stratify=[sample['label'] for sample in samples]  # 保持类别平衡
    )

    return train_samples, test_samples


def save_processed_data(train_samples, test_samples, save_dir='./processed_data',suffix=""):
    """保存处理后的数据"""
    os.makedirs(save_dir, exist_ok=True)

    # 保存训练集和测试集
    torch.save(train_samples, os.path.join(save_dir, f'train_samples{suffix}.pt'))
    torch.save(test_samples, os.path.join(save_dir, f'test_samples{suffix}.pt'))

    print(f"Data saved to {save_dir}")
    print(f"Training samples: {len(train_samples)}")
    print(f"Test samples: {len(test_samples)}")

all_samples = []
filelist = glob.glob("../dataset/MQTT/*_sessions.data")
filename = []
graph_num = []
m=12
first_bytes=300

import time
t0=time.time()
for file in filelist:
    class_name = os.path.basename(file).split("_sessions")[0]
    # 1. 加载原始数据
    with open(file, 'rb') as filehandle:
        # read the data as binary data stream
        flow_dict = pickle.load(filehandle)
    # 2. 创建样本和图
    samples = process_flow_groups(flow_dict,m=m,target_length=first_bytes,concur_threshold=threshold)
    print(f"{class_name} generated {len(samples)} samples.")
    # import pdb;pdb.set_trace()
    all_samples.extend(samples)

# 3. 划分训练集和测试集
train_samples, test_samples = split_train_test(all_samples, test_size=0.2,random_state=42)
t1=time.time()
print('use time:',t1-t0)
train_label = Counter(sample['label'] for sample in train_samples)
test_label = Counter(sample['label'] for sample in test_samples)
print('train label count:',train_label)
print('test label count:',test_label)
# 4. 保存处理后的数据
save_processed_data(train_samples, test_samples,'../dataset/MQTT/processed_data',f'_m{m}_{first_bytes}bytes_threshold-{int(threshold*1000)}ms')