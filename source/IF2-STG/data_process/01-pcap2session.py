from scapy.all import PcapReader, IP, TCP, UDP
from collections import defaultdict
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import json
import time
import pickle
from multiprocessing import Process, Manager

def byte_to_list(packet):
    ## 匿名化IP地址
    packet[IP].src = "0.0.0.0"
    packet[IP].dst = "0.0.0.0"
    str_bytes = bytes(packet).hex()
    byte_list = [int(str_bytes[i:i + 2], 16) for i in range(0, len(str_bytes), 2)]
    return byte_list

def extract_sessions_from_pcap(pcap_path, label, output_path, first_byte = 500):
    """
    从PCAP文件中提取会话信息（五元组分组），记录字节和包长序列
    :param pcap_path: PCAP文件路径
    :param output_csv: 输出CSV文件路径
    :return: 包含会话信息的DataFrame
    """
    # 读取PCAP文件
    pr = PcapReader(pcap_path)
    pcap_name = pcap_path.split("/")[-1]
    sessions = defaultdict(lambda: {'lengths': [], 'timestamps':[], 'bytes': [],'start_time': None, 'label': label})
    i=0
    # 按五元组分组数据包
    while True:
        try:
            pkt = pr.read_packet()
            i += 1
            if i % 1000 == 0:
                # import pdb;pdb.set_trace()
                print(pcap_name + " packet #", i, ' label:', label)
                # break

            if not pkt.haslayer(IP):
                continue  # 跳过非IP包

            # 提取五元组（源IP、源端口、目的IP、目的端口、协议）
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            proto = pkt[IP].proto
            src_port = 0
            dst_port = 0

            if pkt.haslayer(TCP):
                src_port = pkt[TCP].sport
                dst_port = pkt[TCP].dport
            elif pkt.haslayer(UDP):
                src_port = pkt[UDP].sport
                dst_port = pkt[UDP].dport

            # 构造五元组键
            flow_key_fwd = (src_ip, src_port, dst_ip, dst_port, proto)
            flow_key_bwd = (dst_ip, dst_port, src_ip, src_port, proto)

            flow_key = flow_key_bwd if flow_key_bwd in sessions else flow_key_fwd

            # 记录时间戳
            sessions[flow_key]['timestamps'].append(float(pkt.time))
            # 更新流开始时间（如果是第一条包）
            if sessions[flow_key]['start_time'] is None:
                sessions[flow_key]['start_time'] = float(pkt.time)

            # 根据方向记录包长度（正向为正，反向为负）
            length = -len(pkt) if flow_key == flow_key_bwd else len(pkt)
            sessions[flow_key]['lengths'].append(length)

            if len(sessions[flow_key]['bytes']) < first_byte:
                sessions[flow_key]['bytes'].extend(byte_to_list(pkt))

        except Exception as e:
            # 捕获其他所有异常并打印错误信息，然后退出循环
            print(f"An error occurred while processing packet {i} in {pcap_name}: {e}")
            break
    sessions_dict = dict(sessions)
    with open(output_path, 'wb') as filehandle:
        # store the data as binary data stream
        pickle.dump(sessions_dict, filehandle)
    print(f"Processed {i} packets, saved {len(sessions)} sessions to {output_path}")
    pr.close()
    # return sessions

if __name__ == "__main__":
    data_path = '../../dataset/MQTT/'
    file_name = ["normal.pcap" , "scan_A.pcap","scan_sU.pcap","mqtt_bruteforce.pcap","sparta.pcap"]

    file_path = [data_path + i for i in file_name]
    first_bytes=300
    t0 = time.time()
    process_list = []
    for i,file in enumerate(file_path):
        # import pdb;pdb.set_trace()
        label_id = i
        file_name_fix = file_name[i].split('.')[0]
        output_path = f'../dataset/MQTT/{file_name_fix}_fb{first_bytes}_sessions.data'
        # output_path = f'../dataset/MQTT/raw/{file_name_fix}_length_sessions.data'
        try:
            p = Process(target=extract_sessions_from_pcap, args=(file, label_id, output_path,first_bytes))
            process_list.append(p)
        except Exception as e:
            print(f"创建进程时出错: {str(e)}, 文件: {file}")
            import pdb;pdb.set_trace()
            continue

    for p in process_list:
        p.start()

    for p in process_list:
        p.join()

    t1=time.time()
    print("totally use time：",t1-t0)
