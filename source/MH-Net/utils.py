import random
import math
import datetime

import torch
import dgl
import numpy as np
from scapy.all import *
from config import *

config = Config()

def get_device(index= 3):
    return torch.device("cuda:" + str(index) if torch.cuda.is_available() else "cpu")

def get_all_device():
    return ["cuda:0","cuda:1","cuda:2","cuda:3"]

def show_time():
    time_stamp = '\033[1;31;40m[' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ']\033[0m'

    return time_stamp

def set_seed(seed=config.SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    dgl.seed(seed)
    dgl.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def mix_collate_cl_fn(batch):
    hetro_data,bit_hetro_data,target,hetro_mask,bit_hetro_mask= list(zip(*batch))
    hetro_data = np.array(hetro_data).flatten()
    hetro_data = dgl.batch(hetro_data)
    bit_hetro_data = np.array(bit_hetro_data).flatten()
    bit_hetro_data = dgl.batch(bit_hetro_data)
    target = torch.LongTensor(target)
    hetro_mask = np.array(hetro_mask).flatten()
    bit_hetro_mask = np.array(bit_hetro_mask).flatten()

    return hetro_data,bit_hetro_data,target,hetro_mask,bit_hetro_mask

def get_bytes_from_raw(s):
    rows = s.split('\n')
    for i, row in enumerate(rows):
        rows[i] = row[6: 53].strip()

    bytes_list = []
    for row in rows:
        bytes_list.extend(row.replace(' ',''))

    bytes_list_dec = [int(hex, 16) for hex in bytes_list]

    return bytes_list, bytes_list_dec


def pad_truncate(flow, type, config):
    flow_pad_trunc_length = config.FLOW_PAD_TRUNC_LENGTH
    if type == 'payload':
        byte_pad_trunc_length = config.BYTE_PAD_TRUNC_LENGTH
    elif type == 'header':
        byte_pad_trunc_length = config.HEADER_BYTE_PAD_TRUNC_LENGTH

    if len(flow) > flow_pad_trunc_length:
        flow = flow[:flow_pad_trunc_length]

    for ind, p in enumerate(flow):
        if len(p) > byte_pad_trunc_length:
            flow[ind] = p[:byte_pad_trunc_length]
        elif len(p) < byte_pad_trunc_length:
            p.extend([config.PAD_TRUNC_DIGIT] * (byte_pad_trunc_length - len(p)))
            flow[ind] = p

    if len(flow) < flow_pad_trunc_length:
        flow.extend([[config.PAD_TRUNC_DIGIT] * byte_pad_trunc_length] * (flow_pad_trunc_length - len(flow)))

    return flow

def filter_packets(file_path , config):
    file = np.load(file_path,allow_pickle=True)
    header_flow = file['header']
    payload_flow = file['payload']
    index_none = set()
    header_flow = [list(flow) for ind,flow in enumerate(header_flow)]
    payload_flow = [list(flow) for ind,flow in enumerate(payload_flow)]
    for ind,flow in enumerate(header_flow):
        if len(flow) == 0:
            index_none.add(ind)
    for ind,flow in enumerate(payload_flow):
        if len(flow) == 0:
            index_none.add(ind)
    for ind, p in enumerate(payload_flow):
        if ind in index_none:
            p.extend([config.PAD_TRUNC_DIGIT] * (config.BYTE_PAD_TRUNC_LENGTH - len(p)))
            payload_flow[ind] = p
    return index_none,header_flow,payload_flow

def get_bytes_from_raw_new(pkt):
    layers = pkt.layers()
    ip_layer = None
    tcp_layer = None
    for i, layer in enumerate(layers):
        layer = str(layer)
        if 'IP' in layer:
            ip_layer = i
        elif 'TCP' in layer:
            tcp_layer = i

    ip_data = hexdump(pkt[layers[ip_layer]],dump = True).split('\n')
    if len(layers) <= 3 or tcp_layer == None:
        tcp_after_data = ''
    else:
        tcp_after_data = hexdump(pkt[layers[tcp_layer+1]],dump = True).split('\n')
    for i,row in enumerate(ip_data):
        ip_data[i] = row[6:53].strip()
    for i,row in enumerate(tcp_after_data):
        tcp_after_data[i] = row[6:53].strip()
    bytes_list_ip = []
    bytes_list_tcp = []
    for row in ip_data:
        bytes_list_ip.extend(row.replace(' ',''))
    for row in tcp_after_data:
        bytes_list_tcp.extend(row.replace(' ',''))
    
    bytes_list_ip_dec = [int(hex,16) for hex in bytes_list_ip]
    bytes_list_tcp_dec = [int(hex,16) for hex in bytes_list_tcp]    
    final_data = bytes_list_ip_dec[:len(bytes_list_ip_dec)-len(bytes_list_tcp_dec)]
    
    return final_data

def split_flow_ISCX_new(file_path, cate, allow_empty, pad_trunc, config, type='payload'):
    file = np.load(file_path, allow_pickle=True)
    index_none_headerAndpayload,header_flow,payload_flow = filter_packets(file_path,config)
    if type == 'header':
        packets = header_flow
    if type == 'payload':
        packets = payload_flow
    if type == 'header':
        baseline = payload_flow
    data_list = []

    seg_pcap = packets
    if type == 'header':
        seg_baseline = baseline
    if allow_empty:
        seg_pcap = [list(p) for ind, p in enumerate(seg_pcap)]
        if type == 'header':
            seg_baseline = [list(p) for ind, p in enumerate(seg_baseline)]
    else:
        seg_pcap = [list(p) for ind, p in enumerate(seg_pcap) if len(p) != 0]
        if type == 'header':
            seg_baseline =[list(p) for ind, p in enumerate(seg_baseline) if len(p) != 0]
    if type == 'header':
        if len(seg_baseline) == 0:
            print("Empty Flow Detected")
            return data_list
    else:
        if len(seg_pcap) == 0:
            print("Empty Flow Detected")
            return data_list
    if pad_trunc:
        if type == 'header':
            if len(seg_baseline) > config.ANOMALOUS_FLOW_THRESHOLD:
                print("Anomalous Flow Detected")
                return data_list
        else:
            if len(seg_pcap) > config.ANOMALOUS_FLOW_THRESHOLD:
                print("Anomalous Flow Detected")
                return data_list
        seg_pcap = pad_truncate(flow=seg_pcap, type=type, config=config)
    data_list.append(seg_pcap)

    return data_list


def split_flow_ISCX(file_path, cate, allow_empty, pad_trunc, config, type='payload'):
    file = np.load(file_path, allow_pickle=True)
    packets = file[type]
    if type == 'header':
        baseline = file['payload']
    data_list = []

    seg_pcap = packets
    if type == 'header':
        seg_baseline = baseline
    if allow_empty:
        seg_pcap = [list(p) for ind, p in enumerate(seg_pcap)]
        if type == 'header':
            seg_baseline = [list(p) for ind, p in enumerate(seg_baseline)]
    else:
        seg_pcap = [list(p) for ind, p in enumerate(seg_pcap) if len(p) != 0]
        if type == 'header':
            seg_baseline =[list(p) for ind, p in enumerate(seg_baseline) if len(p) != 0]
    if type == 'header':
        if len(seg_baseline) == 0:
            print("Empty Flow Detected")
            return data_list
    else:
        if len(seg_pcap) == 0:
            print("Empty Flow Detected")
            return data_list
    if pad_trunc:
        if type == 'header':
            if len(seg_baseline) > config.ANOMALOUS_FLOW_THRESHOLD:
                print("Anomalous Flow Detected")
                return data_list
        else:
            if len(seg_pcap) > config.ANOMALOUS_FLOW_THRESHOLD:
                print("Anomalous Flow Detected")
                return data_list
        seg_pcap = pad_truncate(flow=seg_pcap, type=type, config=config)
    data_list.append(seg_pcap)

    return data_list

def split_flow_Tor_nonoverlapping(file_path, cate, allow_empty, pad_trunc, config, type='payload'):
    file = np.load(file_path, allow_pickle=True)
    index_none_headerAndpayload,header_flow,payload_flow = filter_packets(file_path,config)
    if type == 'header':
        packets = header_flow
    if type == 'payload':
        packets = payload_flow
    if type == 'header':
        baseline = payload_flow
    data_list = []
    time_stamp = np.array(file['time']).astype(np.float64)
    time_stamp = time_stamp - time_stamp[0]
    sliding_window = int((time_stamp[-1] - 60) / 60) + 1
    if time_stamp[-1] <= 60:
        sliding_window = 1
    begin = [60 * i for i in range(sliding_window)]
    end = [60 + 60 * i for i in range(sliding_window)]
    all_seg_stamp = list(set(begin + end))
    all_seg_stamp.sort()
    stamp_ind_map = dict()
    prev_j = 0
    for i, seg_stamp in enumerate(all_seg_stamp):
        for j in range(prev_j, len(time_stamp)):
            if seg_stamp <= time_stamp[j]:
                stamp_ind_map[seg_stamp] = j
                prev_j = j
                break
    if time_stamp[-1] <= 60:
        stamp_ind_map[60] = len(time_stamp)
    begin = [stamp_ind_map[i] for i in begin]
    end = [stamp_ind_map[i] for i in end]
    for s_ind, e_ind in zip(begin, end):
        if s_ind == e_ind:
            continue
        seg_pcap = packets[s_ind: e_ind]
        if type == 'header':
            seg_baseline = baseline[s_ind: e_ind]
        if allow_empty:
            seg_pcap = [list(p) for ind, p in enumerate(seg_pcap)]
            if type == 'header':
                seg_baseline = [list(p) for ind, p in enumerate(seg_baseline)]
        else:
            seg_pcap = [list(p) for ind, p in enumerate(seg_pcap) if len(p) != 0]
            if type == 'header':
                seg_baseline =[list(p) for ind, p in enumerate(seg_baseline) if len(p) != 0]
        if type == 'header':
            if len(seg_baseline) == 0:
                print("Empty Flow Detected")
                continue
        else:
            if len(seg_pcap) == 0:
                print("Empty Flow Detected")
                continue
        if pad_trunc:
            if type == 'header':
                if len(seg_baseline) > config.ANOMALOUS_FLOW_THRESHOLD:
                    print("Anomalous Flow Detected")
                    continue
            else:
                if len(seg_pcap) > config.ANOMALOUS_FLOW_THRESHOLD:
                    print("Anomalous Flow Detected")
                    continue
            seg_pcap = pad_truncate(flow=seg_pcap, type=type, config=config)
        data_list.append(seg_pcap)

    return data_list

def construct_graph(bytes, header, w_size, k=1):
    # word co-occurence with context windows
    h_payload = np.concatenate((header, bytes))
    
    src_header,dst_header,feat_header = construce_graph_init(header,w_size,'header',k)
    src_payload,dst_payload,feat_payload = construce_graph_init(bytes,w_size,'payload',k)
    src_h_header,dst_h_payload,feat_h_payload = construce_graph_init(h_payload,w_size,'h_payload',k)
    
    g = dgl.heterograph({
        ('header', 'h', 'header') : (src_header,dst_header),
        ('payload', 'p', 'payload') : (src_payload,dst_payload),
        ('header_p', 'h_p', 'header_p')  : (src_h_header,dst_h_payload)})
    
    g.nodes['header'].data['feat'] = feat_header
    g.nodes['payload'].data['feat'] = feat_payload
    g.nodes['header_p'].data['feat'] = feat_h_payload
    return g

def construce_graph_init(bytes,w_size,type,k=1):
    window_size = w_size
    windows = [] # [[], [], [], ..., []]

    words = bytes # ['A', 'B', 'C']
    length = len(words)
    if length <= window_size:
        windows.append(words)
    else:
        # print(length, length - window_size + 1)
        for j in range(length - window_size + 1):
            window = words[j: j + window_size]
            windows.append(window)

    word_window_freq = {}
    for window in windows:
        appeared = set()
        for i in range(len(window)):
            if window[i] in appeared:
                continue
            if window[i] in word_window_freq:
                word_window_freq[window[i]] += 1
            else:
                word_window_freq[window[i]] = 1
            appeared.add(window[i])
    
    word_pair_count = {}
    for window in windows:
        for i in range(1, len(window)):
            for j in range(0, i):
                word_i = window[i]
                word_i_id = word_i
                word_j = window[j]
                word_j_id = word_j
                if word_i_id == word_j_id:
                    continue
                word_pair_str = str(word_i_id) + ',' + str(word_j_id)
                if word_pair_str in word_pair_count:
                    word_pair_count[word_pair_str] += 1
                else:
                    word_pair_count[word_pair_str] = 1
                # two orders
                word_pair_str = str(word_j_id) + ',' + str(word_i_id)
                if word_pair_str in word_pair_count:
                    word_pair_count[word_pair_str] += 1
                else:
                    word_pair_count[word_pair_str] = 1

    src = []
    dst = []
    weight = []

    # pmi as weights

    num_window = len(windows)

    for key in word_pair_count:
        temp = key.split(',')
        i = int(temp[0])
        j = int(temp[1])
        count = word_pair_count[key]
        word_freq_i = word_window_freq[i]
        word_freq_j = word_window_freq[j]
        pmi = math.log((1.0 * count / num_window) ** k /
                  (1.0 * word_freq_i * word_freq_j / (num_window * num_window)))
        if pmi <= 0:
            continue
        src.append(i)
        dst.append(j)
        weight.append(pmi)

    bytes2id = {}
    feat = []
    id_count = 0
    for byte in src:
        if byte in bytes2id:
            continue
        bytes2id[byte] = id_count
        id_count += 1
        feat.append([byte])

    src = [bytes2id[i] for i in src]
    dst = [bytes2id[i] for i in dst]
    feat = torch.tensor(feat, dtype=torch.float32)
    return src,dst,feat


if __name__ == '__main__':
    pass