#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   1_identify_drift.py
@Contact :   hanxueying@iie.ac.cn
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2024/7/8 16:25   xueying      1.0        和1_certainuncertain_process.py一样，主要是对内容进一步细化，把一些数据作为参数，更适合脚本运行
'''

import sys
import os
import importlib
import logging
from datetime import datetime
import argparse

sys.path.append('/home/hxy/driftDetect/newcode0625')
sys.path.append('/newcode0625')
ctu_dataset_config = importlib.import_module('dataconfig_ctu')
generate_co_certain_file = importlib.import_module('myutil').generate_co_certain_file
concat_ori_files = importlib.import_module('myutil').concat_ori_files
generate_uncertain_data = importlib.import_module('myutil').generate_uncertain_data
split_latent = importlib.import_module('myutil').split_latent
cluster_pair_data_all = importlib.import_module('myutil').cluster_pair_data_all
get_all_eval_res = importlib.import_module('myutil').get_all_eval_res
fine_split_certain = importlib.import_module('myutil').fine_split_certain
fine_split_uncertain = importlib.import_module('myutil').fine_split_uncertain
split_get_uncertain_data = importlib.import_module('myutil').split_get_uncertain_data
save_certain_uncertain_with_class_for_train = importlib.import_module(
    'myutil').save_certain_uncertain_with_class_for_train

# kmeans0711_config1_k1_dm0.05_qm10.0tm10.0_l50_weighted_alq1.0_0.01_alt1.0_0   # model
# kmeans0711_config1_k1_dm0.05_qm10.0tm10.0_l50_weighted_alq1.0_0.01_alt1.0_0.01_mq266t266   # result

parser = argparse.ArgumentParser(description='step 2&3 drift detection and identification',
                                 formatter_class=argparse.RawTextHelpFormatter)
# parser.add_argument('--model_folder', type=str, default='')  # 包含了使用的参数  # 这里都是对已有的数据直接进行分割，不涉及重新加载模型
parser.add_argument('--config_folder', type=str, default='kmeans0708_config1_k1_dm0.05_qm10tm10_l50_weighted')  # 包含了使用的参数和使用的模型
parser.add_argument('--data_folder', type=str, default='kmeans0708_config1_k1_dm0.05_weighted')
parser.add_argument('--used_config', type=str, default='config1')
parser.add_argument('--train_part_name', type=str, default='part1')
parser.add_argument('--test_part_name', type=str, default='p2')
parser.add_argument('--test_part_name_prefix', type=str, default='')
parser.add_argument('--idcl_eps', type=float, default=0.5)
parser.add_argument('--idcl_minpts', type=int, default=10)
parser.add_argument('--edge_div_node_threshold', type=float, default=5)
parser.add_argument('--edge_div_com_threshold', type=float, default=10)
parser.add_argument('--save_detail_data', type=bool, default=True)  # 是否保存有标签的数据
parser.add_argument('--execute_folder_name', type=str, default='6_ctu_script_new')

args = parser.parse_args()


class IdentifyConfig:
    def __init__(self, config_folder, data_folder, used_config='config1', train_part_name='part1', test_part_name='p2',
                 test_part_name_prefix='', idcl_eps=0.5, idcl_minpts=10, edge_div_node_threshold=5,
                 edge_div_com_threshold=10, execute_folder_name='none'):
        """
        :param config_folder: 类似 'kmeans0711_config1_k1_dm0.05_qm10.0tm10.0_l50_weighted_alq1.0_0.01_alt1.0_0.01_mq266t266'，可以由多个参数推导得到，包含训练时的参数以及使用的模型
        :param data_folder: 类似 'kmeans0625_config1_k2_dm0.05_weighted'
        :param used_config:
        :param train_part_name:  是由什么数据训练得到的模型生成的结果，如果是第一次训练就是part1，如果是后面更新的就是 p1p2_certain，或者p1p2_uncertain
        :param idcl_eps, idcl_minpts, edge_div_node_threshold, edge_div_com_threshold: 聚类参数
        """
        self.dataset = 'ctu'
        self.dataset_config_name = used_config
        self.all95 = 'all'
        self.train_part_name = train_part_name
        self.test_part_name = test_part_name
        self.test_part_name_prefix = test_part_name_prefix

        if self.dataset == 'ctu':
            if self.dataset_config_name == 'config1':
                self.dataset_config = ctu_dataset_config.DatasetConfig1()
            elif self.dataset_config_name == 'config2':
                self.dataset_config = ctu_dataset_config.DatasetConfig2()
            elif self.dataset_config_name == 'config3':
                self.dataset_config = ctu_dataset_config.DatasetConfig3()
            elif self.dataset_config_name == 'config4':
                self.dataset_config = ctu_dataset_config.DatasetConfig4()

        if self.test_part_name == 'p2':
            self.test_normal_files = self.dataset_config.part2_normal_files
            self.test_attack_files = self.dataset_config.part2_attack_files
        elif self.test_part_name == 'p1val':
            self.test_normal_files = self.dataset_config.part1_normal_files_val
            self.test_attack_files = self.dataset_config.part1_attack_files_val
        elif self.test_part_name == 'p2val':
            self.test_normal_files = self.dataset_config.part2_normal_files_val
            self.test_attack_files = self.dataset_config.part2_attack_files_val
        elif self.test_part_name == 'p3':
            self.test_normal_files = self.dataset_config.part3_normal_files
            self.test_attack_files = self.dataset_config.part3_attack_files
        elif self.test_part_name == 'p4':
            self.test_normal_files = self.dataset_config.part4_normal_files
            self.test_attack_files = self.dataset_config.part4_attack_files
        elif self.test_part_name == 'p4val':
            self.test_normal_files = self.dataset_config.part4_normal_files_val
            self.test_attack_files = self.dataset_config.part4_attack_files_val

        # 确定certain的列
        self.cocertain_row = 'dist_co_certain'  # 看seq和sta的结果是否一致
        self.consider_unmatch = True  # 是否考虑seq和sta结果不一致的情况，true就是把不匹配的也视为uncertain
        self.used_uncertain_row = 'cla_md_recon_uncertain_3'
        self.regenerate_cocertain = False

        # 在identify的时候聚类的参数
        self.idcl_eps = idcl_eps
        self.idcl_minpts = idcl_minpts

        # 在判断聚类得到的簇是否为恶意时的参数
        self.edge_div_node_threshold = edge_div_node_threshold
        self.edge_div_com_threshold = edge_div_com_threshold

        # ===============
        # ctu路径
        # ===============
        # self.config_folder = 'kmeans0625_config1_k2_dm0.05_qm10tm10_l50_weighted'
        # self.data_folder = 'kmeans0625_config1_k2_dm0.05_weighted'
        self.config_folder = config_folder
        self.data_folder = data_folder

        self.ori_file_root = f'/home/hxy/driftDetect/0_data/2_captured_traffic/ctu_all_run_data/{self.data_folder}'
        self.train_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/{self.train_part_name}/{self.config_folder}'

        if len(self.test_part_name_prefix) == 0:
            self.result_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/{self.train_part_name}/{self.config_folder}/{self.test_part_name}'
            self.test_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/{self.train_part_name}/{self.config_folder}/{self.test_part_name}'
        else:
            self.result_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/{self.train_part_name}/{self.config_folder}/{self.test_part_name_prefix}/{self.test_part_name}'
            self.test_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/{self.train_part_name}/{self.config_folder}/{self.test_part_name_prefix}/{self.test_part_name}'

        if self.all95 == '95':
            self.attack_seq_path = os.path.join(self.result_root, 'attack_test_result_ksigma_95deep_new_seq.csv')
            self.attack_sta_path = os.path.join(self.result_root, 'attack_test_result_ksigma_95deep_new_sta.csv')
            self.attack_dist_seq_path = os.path.join(self.result_root, 'attack_test_result_ksigma_95_seq.csv')
            self.attack_dist_sta_path = os.path.join(self.result_root, 'attack_test_result_ksigma_95_sta.csv')
            self.attack_cocertain_path = os.path.join(self.result_root, 'attack_cocertain.csv')

            self.normal_seq_path = os.path.join(self.result_root, 'normal_test_result_ksigma_95deep_new_seq.csv')
            self.normal_sta_path = os.path.join(self.result_root, 'normal_test_result_ksigma_95deep_new_sta.csv')
            self.normal_dist_seq_path = os.path.join(self.result_root, 'normal_test_result_ksigma_95_seq.csv')
            self.normal_dist_sta_path = os.path.join(self.result_root, 'normal_test_result_ksigma_95_sta.csv')
            self.normal_cocertain_path = os.path.join(self.result_root, 'normal_cocertain.csv')
        elif self.all95 == 'all':
            self.attack_seq_path = os.path.join(self.result_root, 'attack_test_result_ksigma_deep_new_seq.csv')
            self.attack_sta_path = os.path.join(self.result_root, 'attack_test_result_ksigma_deep_new_sta.csv')
            self.attack_dist_seq_path = os.path.join(self.result_root, 'attack_test_result_ksigma_seq.csv')
            self.attack_dist_sta_path = os.path.join(self.result_root, 'attack_test_result_ksigma_sta.csv')
            self.attack_cocertain_path = os.path.join(self.result_root, 'attack_cocertain.csv')

            self.normal_seq_path = os.path.join(self.result_root, 'normal_test_result_ksigma_deep_new_seq.csv')
            self.normal_sta_path = os.path.join(self.result_root, 'normal_test_result_ksigma_deep_new_sta.csv')
            self.normal_dist_seq_path = os.path.join(self.result_root, 'normal_test_result_ksigma_seq.csv')
            self.normal_dist_sta_path = os.path.join(self.result_root, 'normal_test_result_ksigma_sta.csv')
            self.normal_cocertain_path = os.path.join(self.result_root, 'normal_cocertain.csv')

        # 隐含特征是在一起的
        self.seq_latent_path = os.path.join(self.test_save_data_root, 'test_seqmid_info.pickle')
        self.sta_latent_path = os.path.join(self.test_save_data_root, 'test_stamid_info.pickle')
        self.attack_seq_latent_path = os.path.join(self.test_save_data_root, 'attack_test_seqmid_info.pickle')
        self.attack_sta_latent_path = os.path.join(self.test_save_data_root, 'attack_test_stamid_info.pickle')
        self.normal_seq_latent_path = os.path.join(self.test_save_data_root, 'normal_test_seqmid_info.pickle')
        self.normal_sta_latent_path = os.path.join(self.test_save_data_root, 'normal_test_stamid_info.pickle')

        if self.consider_unmatch:
            self.certain_normal_path = os.path.join(self.result_root,
                                                    f'normal_certain-{self.cocertain_row}-{self.used_uncertain_row}_counmatch.csv')
            self.uncertain_normal_path = os.path.join(self.result_root,
                                                      f'normal_uncertain-{self.cocertain_row}-{self.used_uncertain_row}_counmatch.csv')
            self.certain_attack_path = os.path.join(self.result_root,
                                                    f'attack_certain-{self.cocertain_row}-{self.used_uncertain_row}_counmatch.csv')
            self.uncertain_attack_path = os.path.join(self.result_root,
                                                      f'attack_uncertain-{self.cocertain_row}-{self.used_uncertain_row}_counmatch.csv')
        else:
            self.certain_normal_path = os.path.join(self.result_root,
                                                    f'normal_certain-{self.cocertain_row}-{self.used_uncertain_row}_nocounmatch.csv')
            self.uncertain_normal_path = os.path.join(self.result_root,
                                                      f'normal_uncertain-{self.cocertain_row}-{self.used_uncertain_row}_nocounmatch.csv')
            self.certain_attack_path = os.path.join(self.result_root,
                                                    f'attack_certain-{self.cocertain_row}-{self.used_uncertain_row}_nocounmatch.csv')
            self.uncertain_attack_path = os.path.join(self.result_root,
                                                      f'attack_uncertain-{self.cocertain_row}-{self.used_uncertain_row}_nocounmatch.csv')
        # 保存聚类后的簇的统计特征
        self.cluster_mid_file_root = os.path.join(self.result_root,
                                                  f'cluster_mid_file_eps{self.idcl_eps}_mp{self.idcl_minpts}')

        # 更新数据重新保存，用于下一次训练
        self.new_certain_data_root = os.path.join(self.ori_file_root,
                                                  f'{self.test_part_name}_certain/{self.cocertain_row}-'
                                                  f'{self.used_uncertain_row}-eps{self.idcl_eps}minpts'
                                                  f'{self.idcl_minpts}-thre{self.edge_div_node_threshold}_{self.edge_div_com_threshold}')
        self.new_uncertain_data_root = os.path.join(self.ori_file_root,
                                                    f'{self.test_part_name}_uncertain/{self.cocertain_row}-'
                                                    f'{self.used_uncertain_row}-eps{self.idcl_eps}minpts'
                                                    f'{self.idcl_minpts}-thre{self.edge_div_node_threshold}_{self.edge_div_com_threshold}')
        if not os.path.exists(self.new_certain_data_root):
            os.makedirs(self.new_certain_data_root)
        if not os.path.exists(self.new_uncertain_data_root):
            os.makedirs(self.new_uncertain_data_root)

        # =======
        # 设置log信息
        # =======

        logging.basicConfig(level=logging.DEBUG,
                            filename=f'log/stage2_{self.dataset}-{self.config_folder}.log',
                            format='%(message)s')
        logging.info('\n\n===================================================')
        logging.info('====== ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ======')
        logging.info('=====================================================')
        logging.info(f'- data: {self.dataset}, {self.test_part_name}')
        logging.info(f'- train part name: {self.train_part_name}, test part name: {self.test_part_name}')
        logging.info(f'- config folder: {self.config_folder}')
        logging.info(
            f'- certain: cocertain_row: {self.cocertain_row}, used_uncertain_row: {self.used_uncertain_row}, consider unmatch: {self.consider_unmatch}')
        logging.info(
            f'- identify cluster: eps: {self.idcl_eps}, minpts: {self.idcl_minpts}, edge_div_node_thre: {self.edge_div_node_threshold}, edge_div_com_thre: {self.edge_div_com_threshold}')
        logging.info('--------')


if __name__ == '__main__':
    config = IdentifyConfig(config_folder=args.config_folder, data_folder=args.data_folder,
                            used_config=args.used_config,
                            train_part_name=args.train_part_name, test_part_name=args.test_part_name, test_part_name_prefix=args.test_part_name_prefix,
                            idcl_eps=args.idcl_eps, idcl_minpts=args.idcl_minpts,
                            edge_div_node_threshold=args.edge_div_node_threshold,
                            edge_div_com_threshold=args.edge_div_com_threshold,
                            execute_folder_name=args.execute_folder_name)
    # 将被判定为certain和uncertain的原始特征分别存储起来
    print('[INFO] Split get uncertain data')
    logging.info('[INFO] Split get uncertain data')
    split_get_uncertain_data(config.seq_latent_path, config.attack_seq_latent_path, config.normal_seq_latent_path,
                             config.sta_latent_path, config.attack_sta_latent_path, config.normal_sta_latent_path,
                             config.regenerate_cocertain, config.consider_unmatch, config.cocertain_row,
                             config.used_uncertain_row,
                             config.ori_file_root, config.result_root,
                             config.normal_seq_path, config.normal_sta_path, config.normal_cocertain_path,
                             config.test_normal_files,
                             config.normal_dist_seq_path, config.normal_dist_sta_path, config.certain_normal_path,
                             config.uncertain_normal_path,
                             config.attack_seq_path, config.attack_sta_path, config.attack_cocertain_path,
                             config.test_attack_files,
                             config.attack_dist_seq_path, config.attack_dist_sta_path, config.certain_attack_path,
                             config.uncertain_attack_path
                             )
    # 对uncertain的数据进行聚类，判定是攻击还是异常，并生成对整体的评价
    print('[INFO] Identify drift type')
    logging.info('[INFO] Identify drift type')
    cluster_pair_data_all(config.result_root, config.result_root,
                          os.path.basename(config.uncertain_normal_path),
                          os.path.basename(config.uncertain_attack_path), config.cluster_mid_file_root,
                          config.idcl_eps, config.idcl_minpts, config.edge_div_node_threshold,
                          config.edge_div_com_threshold)

    get_all_eval_res(config.certain_normal_path, config.certain_attack_path, config.uncertain_normal_path,
                     config.uncertain_attack_path)

    # 将不确定样本具体的类别保存下来，用于后续训练
    if args.save_detail_data:
        print('[INFO] Save certain and uncertain test data with detail class label')
        logging.info('[INFO] Save certain and uncertain test data with detail class label')
        save_certain_uncertain_with_class_for_train(config.certain_normal_path, config.certain_attack_path,
                                                    config.new_certain_data_root,
                                                    config.uncertain_normal_path, config.uncertain_attack_path,
                                                    config.new_uncertain_data_root)
