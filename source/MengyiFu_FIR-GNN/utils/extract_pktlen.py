import os
import socket
import dpkt
import pandas as pd
from flowcontainer.extractor import extract

from file_label import file_label


def walkFile(file):
    filepatlist = []
    for root, dirs, files in os.walk(file):
        # root 表示当前访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list
        for f in files:
            filepath = os.path.join(root, f)
            filepatlist.append(filepath)
    return filepatlist


def compute_pkt_len(group, pkt_len_dict, pkt_num=20):
    start_index = 0
    for index, row in group.iterrows():
        key = row['Flow ID']
        # print(key)
        if key in pkt_len_dict.keys():
            l = pkt_len_dict[key][start_index: start_index + row['Tot Pkts']]
            if len(l) > pkt_num:
                l = l[: pkt_num]
            else:
                l = l + [0] * (pkt_num - len(l))
            group.at[index, 'Pkt Len'] = l
            # print(l)
            start_index = start_index + row['Tot Pkts']
        else:
            continue
    return group


def create_flow(row):
    if row["Src Port"] > row["Dst Port"]:
        return f'{row["Src IP"]}-{row["Dst IP"]}-{row["Src Port"]}-{row["Dst Port"]}-{row["Protocol"]}'
    else:
        return f'{row["Dst IP"]}-{row["Src IP"]}-{row["Dst Port"]}-{row["Src Port"]}-{row["Protocol"]}'


if __name__ == '__main__':
    dataset = {'ISCX-VPN': 0, 'ISCX-NonVPN': 1, 'BoT-IoT': 2, 'CICIDS': 3}
    dataset_num = 1
    if dataset_num == 0:
        pcaplist = walkFile('./datasets/ISCX-VPN-NonVPN/VPN-PCAPs-02')
        csv_path = './datasets/ISCX-VPN-NonVPN/VPN-PCAPs-02CSV'
        pkt_len_path = './datasets/ISCX-VPN-NonVPN/VPN-CSV-pktlen'
    elif dataset_num == 1:
        pcaplist = walkFile('./datasets/ISCX-VPN-NonVPN/NonVPN-PCAPs-01')
        csv_path = './datasets/ISCX-VPN-NonVPN/NonVPN-PCAPs-01CSV'
        pkt_len_path = './datasets/ISCX-VPN-NonVPN/NonVPN-CSV-pktlen'
    elif dataset_num == 2:
        pcaplist = walkFile('./datasets/BoT-IoT/BoT-IoT_PCAP')
        csv_path = './datasets/BoT-IoT/BoT-IoT_CSV'
        pkt_len_path = './datasets/BoT-IoT/BoT-IoT_CSV_pktlen'
    else:
        pcaplist = walkFile('./datasets/CICIDS/CICIDS_PCAP')
        csv_path = './datasets/CICIDS/CICIDS_CSV'
        pkt_len_path = './datasets/CICIDS/CICIDS_CSV_pktlen'

    for pcapfile in pcaplist:
        filename = pcapfile.split('/')[-1].split('.')[0]
        label = file_label[filename]
        pkt_len_dict = {}
        print(f'read {filename}')
        result = extract(pcapfile, filter='tcp or udp')
        for key in result:
            value = result[key]
            pkt_len = value.payload_lengths
            src = value.src
            dst = value.dst
            sport = str(value.sport)
            dport = str(value.dport)
            protocol = '6' if value.protocol == 'tcp' else '17'
            key = f'{src}-{dst}-{sport}-{dport}-{protocol}'
            # print(key)
            if key in pkt_len_dict.keys():
                pkt_len_dict[key].extend(pkt_len)
            else:
                pkt_len_dict[key] = pkt_len
        features_df = pd.read_csv(f'{csv_path}/{filename}.pcap_Flow.csv',
                                  encoding='GBK')
        features_df['Tot Pkts'] = features_df['Tot Fwd Pkts'] + features_df['Tot Bwd Pkts']
        features_df['Pkt Len'] = None
        features_df['Flow ID'] = features_df.apply(create_flow, axis=1)
        features_df = features_df.groupby(by='Flow ID').apply(lambda x: compute_pkt_len(x, pkt_len_dict)).reset_index(
            drop=True)
        features_df = features_df.drop(columns=['Tot Pkts'])
        save_path = f'{pkt_len_path}/{label}.csv'
        features_df.to_csv(save_path, mode='a' if os.path.exists(save_path) else 'w', index=False, header=False if os.path.exists(save_path) else True)


    # notISCX = True
    # error_list = set()
    # for pcapfile in pcaplist:
    #     filename = pcapfile.split('/')[-1].split('.')[0]
    #     label = file_label[filename]
    #     pkt_len_dict = {}
    #     with open(pcapfile, 'rb') as f:
    #         try:
    #             pcap = dpkt.pcap.Reader(f)
    #             print(f'read {filename}')
    #             for ts, buf in pcap:
    #                 drop = False
    #                 # IPv4
    #                 try:
    #                     if notISCX:
    #                         eth = dpkt.ethernet.Ethernet(buf)
    #                         ip = eth.data
    #                     else:
    #                         ip = dpkt.ip.IP(buf)
    #                     srcip = socket.inet_ntoa(ip.src)
    #                     dstip = socket.inet_ntoa(ip.dst)
    #                     protocol_index = ip.p
    #                     pkt_len = len(ip.data)
    #                     if isinstance(ip.data, dpkt.tcp.TCP):
    #                         srcport = ip.data.sport
    #                         dstport = ip.data.dport
    #                         if ip.data.flags & (dpkt.tcp.TH_SYN | dpkt.tcp.TH_FIN | dpkt.tcp.TH_RST):
    #                             continue
    #                     elif isinstance(ip.data, dpkt.udp.UDP):
    #                         srcport = ip.data.sport
    #                         dstport = ip.data.dport
    #                     if srcport > dstport:
    #                         flow_id = f'{srcip}-{dstip}-{srcport}-{dstport}-{protocol_index}'
    #                     else:
    #                         flow_id = f'{dstip}-{srcip}-{dstport}-{srcport}-{protocol_index}'
    #                         pkt_len = -pkt_len
    #                     if flow_id in pkt_len_dict.keys():
    #                         pkt_len_dict[flow_id].append(pkt_len)
    #                     else:
    #                         pkt_len_dict[flow_id] = [pkt_len]
    #
    #                 except dpkt.dpkt.UnpackError:
    #                     # print('IPv6')
    #                     try:
    #                         if notISCX:
    #                             eth = dpkt.ethernet.Ethernet(buf)
    #                             ipv6 = eth.data
    #                         else:
    #                             ipv6 = dpkt.ip6.IP6(buf)
    #                         srcip = socket.inet_ntop(socket.AF_INET6, ipv6.src)
    #                         dstip = socket.inet_ntop(socket.AF_INET6, ipv6.dst)
    #                         protocol_index = ipv6.nxt
    #                         pkt_len = len(ipv6.data)
    #                         if isinstance(ipv6.data, dpkt.tcp.TCP):
    #                             if ipv6.data.flags & (dpkt.tcp.TH_SYN | dpkt.tcp.TH_FIN | dpkt.tcp.TH_RST):
    #                                 continue
    #                             srcport = ipv6.data.sport
    #                             dstport = ipv6.data.dport
    #                         elif isinstance(ipv6.data, dpkt.udp.UDP):
    #                             srcport = ipv6.data.sport
    #                             dstport = ipv6.data.dport
    #
    #                         if srcport > dstport:
    #                             flow_id = f'{srcip}-{dstip}-{srcport}-{dstport}-{protocol_index}'
    #                         else:
    #                             flow_id = f'{dstip}-{srcip}-{dstport}-{srcport}-{protocol_index}'
    #                             pkt_len = -pkt_len
    #                         if flow_id in pkt_len_dict.keys():
    #                             pkt_len_dict[flow_id].append(pkt_len)
    #                         else:
    #                             pkt_len_dict[flow_id] = [pkt_len]
    #                     except dpkt.dpkt.NeedData:
    #                         print('IPv6解析失败')
    #         except ValueError:
    #             print('Malformed Packet')
    #             error_list.update([filename])
    # print('Malformed Pcap:', error_list)