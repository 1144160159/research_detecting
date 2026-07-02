#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   5_uncertain_update.py
@Contact :   hanxueying@iie.ac.cn
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2024/7/25 9:51   xueying      1.0       
'''

import os
import sys, importlib
import torch
import logging
from datetime import datetime
import argparse
from torch.utils.data import DataLoader, WeightedRandomSampler, RandomSampler
import pickle
import itertools

sys.path.append('/home/hxy/driftDetect/newcode0625')
sys.path.append('D:\PycharmProject\DriftDetection/newcode0625')

DatasetConfig1 = importlib.import_module('dataconfig_ctu').DatasetConfig1
StaSeqTrafficNormalizedDatasetUpdateUncertain = importlib.import_module(
    'myutil').StaSeqTrafficNormalizedDatasetUpdateUncertain
get_sample_weights = importlib.import_module('myutil').get_sample_weights
ContraLossEucNewM2 = importlib.import_module('myutil').ContraLossEucNewM2
StaSeqTrafficNormalizedDataset = importlib.import_module('myutil').StaSeqTrafficNormalizedDataset

uncertain_train_update_model = importlib.import_module('myutil').uncertain_train_update_model
get_uncertain_related = importlib.import_module('myutil').get_uncertain_related
combine_two_distribution_uncertain = importlib.import_module('myutil').combine_two_distribution_uncertain
validate_drift = importlib.import_module('myutil').validate_drift
eval_model_stage2 = importlib.import_module('myutil').eval_model_stage2
StaSeqTrafficNormalizedDatasetUpdateOri = importlib.import_module('myutil').StaSeqTrafficNormalizedDatasetUpdateOri

parser = argparse.ArgumentParser(description='step 4 uncertain update',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--used_config', type=str, default='config1')
parser.add_argument('--config_folder', type=str)
parser.add_argument('--data_folder', type=str)
parser.add_argument('--new_normal_file', type=str)
parser.add_argument('--new_attack_file', type=str)
parser.add_argument('--old_test_part_name', type=str)
parser.add_argument('--used_seq_model_ori_num', type=int, default=266)
parser.add_argument('--used_sta_model_ori_num', type=int, default=266)
parser.add_argument('--used_seq_model_certain_num', type=int, default=10)
parser.add_argument('--used_sta_model_certain_num', type=int, default=10)
parser.add_argument('--used_seq_model_uncertain_num', type=int)
parser.add_argument('--used_sta_model_uncertain_num', type=int)
parser.add_argument('--min_sample_each_file_uncertain', type=int, default=100)
parser.add_argument('--execute_folder_name', type=str, default='6_ctu_script_new')
parser.add_argument('--alpha_margin', type=float, default=1.1)
parser.add_argument('--un_seq_margin', type=float, default=10)
parser.add_argument('--un_sta_margin', type=float, default=10)
parser.add_argument('--seq_contra_lamda', type=float, default=1)
parser.add_argument('--seq_recon_lamda', type=float, default=0.05)
parser.add_argument('--seq_tocenter_lamda', type=float, default=1)
parser.add_argument('--seq_dist_lamda', type=float, default=0.001)
parser.add_argument('--sta_contra_lamda', type=float, default=1)
parser.add_argument('--sta_recon_lamda', type=float, default=0.05)
parser.add_argument('--sta_tocenter_lamda', type=float, default=1)
parser.add_argument('--sta_dist_lamda', type=float, default=0.001)
parser.add_argument('--used_self_labeled_data', type=str, default='yes')
parser.add_argument('--train_epoch', type=int, default=100)

args = parser.parse_args()


def check_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


class UpdateUncertainConfig:
    def __init__(self, used_config, config_folder, data_folder, new_normal_file, new_attack_file, old_test_part_name,
                 used_seq_model_ori_num, used_sta_model_ori_num,
                 used_seq_model_certain_num, used_sta_model_certain_num, used_seq_model_uncertain_num,
                 used_sta_model_uncertain_num,
                 min_sample_each_file_uncertain, execute_folder_name,
                 alpha_margin=1.1, un_seq_margin=10, un_sta_margin=10,
                 seq_contra_lamda=1, seq_recon_lamda=0.05, seq_tocenter_lamda=1, seq_dist_lamda=0.001,
                 sta_contra_lamda=1, sta_recon_lamda=0.05, sta_tocenter_lamda=1, sta_dist_lamda=0.001,
                 used_self_labeled_data='yes', train_epoch=100):

        self.used_config = used_config  # 'config1'

        self.config_folder = config_folder  # 'kmeans0625_config1_k2_dm0.05_qm10tm10_l50_weighted'
        self.data_folder = data_folder  # 'kmeans0625_config1_k2_dm0.05_weighted'
        self.ori_file_root = f'/home/hxy/driftDetect/0_data/2_captured_traffic/ctu_all_run_data/{self.data_folder}'

        self.new_normal_file = new_normal_file  # 'normal_kmeans_k2_dm0.05.pickle'
        self.new_attack_file = new_attack_file
        self.old_test_part_name = old_test_part_name

        if self.used_config == 'config1':
            if (new_normal_file is not None) and (new_attack_file is not None):
                self.dataconfig = DatasetConfig1(new_normal_file=self.new_normal_file,
                                                 new_attack_file=self.new_attack_file)
            elif (new_normal_file is not None) and (new_attack_file is None):
                self.dataconfig = DatasetConfig1(new_normal_file=self.new_normal_file)
            else:
                print('[ERROR] Dataconfig error occurs, both empty')
            # self.dataconfig = DatasetConfig1(self.new_normal_file)

        self.min_sample_each_file_uncertain = min_sample_each_file_uncertain  # 100  # 如果一个文件中的样本数少于这些，就不使用这个文件

        # 来自step2的参数
        # 确定certain的列
        self.cocertain_row = 'dist_co_certain'  # 看seq和sta的结果是否一致
        self.consider_unmatch = True  # 是否考虑seq和sta结果不一致的情况，true就是把不匹配的也视为uncertain
        self.used_uncertain_row = 'cla_md_recon_uncertain_3'
        self.regenerate_cocertain = False
        # 在identify的时候聚类的参数
        self.idcl_eps = 0.5
        self.idcl_minpts = 10
        # 在判断聚类得到的簇是否为恶意时的参数
        self.edge_div_node_threshold = 5.0
        self.edge_div_com_threshold = 10.0

        # 使用了更新后的模型的临时的一个路径文件夹，因为后面很多用这个的（主要是result，save data相关的，model的存储路径不是这样
        certain_update_tmp_folder_name = f'certain_usesl_{used_self_labeled_data}_om{used_seq_model_ori_num}_{used_sta_model_ori_num}_cm{used_seq_model_certain_num}_{used_sta_model_certain_num}'
        uncertain_update_tmp_folder_name = f'uncertain_usesl_{used_self_labeled_data}_om{used_seq_model_ori_num}_{used_sta_model_ori_num}_cm{used_seq_model_certain_num}_{used_sta_model_certain_num}_un{used_seq_model_uncertain_num}_{used_sta_model_uncertain_num}'

        # uncertain和certain的folder是一样的
        # 用于更新模型的数据所在的路径（如果使用的是identify drift生成的数据）
        self.certain_name_folder = f'{self.cocertain_row}-{self.used_uncertain_row}-eps{self.idcl_eps}minpts{self.idcl_minpts}-thre{self.edge_div_node_threshold}_{self.edge_div_com_threshold}'
        self.uncertain_data_root = os.path.join(self.ori_file_root,
                                                f'{self.old_test_part_name}_uncertain/{self.certain_name_folder}')

        # 根据原始数据生成的真实的数据标签所在的路径（如果不使用identify drift生成的数据）[这个只和原始的聚类的划分有关，和config folder没有关系]
        self.ori_label_root = os.path.join(self.ori_file_root, f'ori_label_{self.old_test_part_name}')  # 只有标签，没有数据

        # 基于certain数据更新的模型继续更新
        self.certain_model_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/model/p1{self.old_test_part_name}_certain/{self.config_folder}/certain_usesl_{used_self_labeled_data}_om{used_seq_model_ori_num}_{used_sta_model_ori_num}'  # 不涉及cm，所以这里单独写
        self.certain_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain/{self.config_folder}/{certain_update_tmp_folder_name}/{self.old_test_part_name}_updated'

        # 使用用certain更新好的哪个模型
        self.used_certain_seq_model = f'seq_model_{used_seq_model_certain_num}.pth'
        self.used_certain_sta_model = f'sta_model_{used_sta_model_certain_num}.pth'

        # 使用uncertain更新后的模型、中间数据和结果存储在哪里
        self.uncertain_model_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/model/p1{self.old_test_part_name}_uncertain' \
                                    f'/{self.config_folder}/uncertain_usesl_{used_self_labeled_data}_om{used_seq_model_ori_num}_{used_sta_model_ori_num}_cm{used_seq_model_certain_num}_{used_sta_model_certain_num}'
        self.uncertain_new_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{uncertain_update_tmp_folder_name}/{self.old_test_part_name}_new'
        self.uncertain_updated_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{uncertain_update_tmp_folder_name}/{self.old_test_part_name}_updated'
        # 验证在使用uncertain更新的模型上，数据偏移了多少，存储中间结果，主要是用过去的数据处理
        self.uncertain_driftvalidate_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain_driftvalidate/{self.config_folder}/{uncertain_update_tmp_folder_name}'

        check_paths(
            [self.uncertain_model_root, self.uncertain_new_save_data_root, self.uncertain_updated_save_data_root,
             self.uncertain_driftvalidate_save_data_root])

        # 使用更新后的模型进行验证，结果和中间结果保存在哪里
        self.uncertain_updated_test_result_root_p1val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p1val'
        self.uncertain_update_test_save_data_root_p1val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p1val'
        self.uncertain_updated_test_result_root_p2val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p2val'
        self.uncertain_update_test_save_data_root_p2val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p2val'
        self.uncertain_updated_test_result_root_p3 = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p3'
        self.uncertain_update_test_save_data_root_p3 = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p3'
        self.uncertain_updated_test_result_root_p4val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p4val'
        self.uncertain_update_test_save_data_root_p4val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_uncertain/{self.config_folder}/{self.old_test_part_name}_updated/{uncertain_update_tmp_folder_name}/p4val'
        check_paths([self.uncertain_updated_test_result_root_p1val, self.uncertain_update_test_save_data_root_p1val,
                     self.uncertain_updated_test_result_root_p2val, self.uncertain_update_test_save_data_root_p2val,
                     self.uncertain_updated_test_result_root_p3, self.uncertain_update_test_save_data_root_p3,
                     self.uncertain_updated_test_result_root_p4val, self.uncertain_update_test_save_data_root_p4val])

        # 测试的路径，相关数据
        self.class_dict = self.dataconfig.class_dict
        self.detail_class_dict = self.dataconfig.detail_class_dict
        self.test_files_p3 = self.dataconfig.part3_normal_files + self.dataconfig.part3_attack_files
        self.test_files_p1val = self.dataconfig.part1_normal_files_val + self.dataconfig.part1_attack_files_val
        self.test_files_p2val = self.dataconfig.part2_normal_files_val + self.dataconfig.part2_attack_files_val
        self.test_files_p4val = self.dataconfig.part4_normal_files_val + self.dataconfig.part4_attack_files_val
        self.test_files_p1 = self.dataconfig.part1_normal_files + self.dataconfig.part1_attack_files

        # 如果使用原有的标签，所需的信息
        if self.old_test_part_name == 'p2':
            self.normal_certain_files = self.dataconfig.part2_normal_certain_files
            self.normal_uncertain_files = self.dataconfig.part2_normal_uncertain_files
            self.attack_certain_files = self.dataconfig.part2_attack_certain_files
            self.attack_uncertain_files = self.dataconfig.part2_attack_uncertain_files
        elif self.old_test_part_name == 'p4':
            self.normal_certain_files = self.dataconfig.part4_normal_certain_files
            self.normal_uncertain_files = self.dataconfig.part4_normal_uncertain_files
            self.attack_certain_files = self.dataconfig.part4_attack_certain_files
            self.attack_uncertain_files = self.dataconfig.part4_attack_uncertain_files
        else:
            self.normal_certain_files = None
            self.normal_uncertain_files = None
            self.attack_certain_files = None
            self.attack_uncertain_files = None

        # 使用uncertain更新后的模型用哪个
        self.used_seq_model_uncertain_update = f'seq_model_{used_seq_model_uncertain_num}.pth'
        self.used_sta_model_uncertain_update = f'sta_model_{used_sta_model_uncertain_num}.pth'

        # 原来的簇心
        self.old_p2cer_sta_centers_path = os.path.join(self.certain_save_data_root, 'train_sta_info_stadata.pickle')
        self.old_p2cer_seq_centers_path = os.path.join(self.certain_save_data_root, 'train_sta_info.pickle')

        # 原来的scaler的路径
        self.old_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/part1/{self.config_folder}'
        self.ori_scaler_path = os.path.join(self.old_save_data_root, 'scaler.pickle')

        # 旧 seq model 的参数
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.feature_size = 2
        self.d_model = 16
        self.nhead = 2
        self.num_encoder_layers = 3
        self.num_decoder_layers = 3
        self.dim_feedforward = 32
        self.dropout = 0.1
        self.sequence_length = 50

        # =======
        # 更新训练模型的参数
        self.batch_size = 1024
        self.train_epoch = train_epoch
        self.seq_lr = 0.001
        self.sta_lr = 0.001
        self.seq_eta_min = 1e-05
        self.sta_eta_min = 1e-05

        # 更新时margin是原来的多少倍
        self.alpha_margin = alpha_margin  # 1.1
        self.seq_margin = un_seq_margin  # 10
        self.sta_margin = un_sta_margin  # 10
        self.temperature = 1

        # 在计算损失时各项的权重
        self.seq_contra_lamda = seq_contra_lamda  # 1
        self.seq_recon_lamda = seq_recon_lamda  # 0.05  # /20
        self.seq_tocenter_lamda = seq_tocenter_lamda  # 1  # 距离原来的簇心的距离对应的损失
        self.seq_dist_lamda = seq_dist_lamda  # 0.001  # 和原来的样本的距离的约束
        self.sta_contra_lamda = sta_contra_lamda  # 1
        self.sta_recon_lamda = sta_recon_lamda  # 0.05  # /20
        self.sta_tocenter_lamda = sta_tocenter_lamda  # 1
        self.sta_dist_lamda = sta_dist_lamda  # 0.001

        logging.basicConfig(level=logging.DEBUG,
                            filename=f'log/updata-uncertain-{self.config_folder}-uncertain_usesl_{used_self_labeled_data}.log',
                            format='%(message)s')
        logging.info('\n\n ====== ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ======\n\n')
        logging.info('\n******** update uncertain ********\n')
        logging.info(f'** uncertain: {self.certain_name_folder} **')  # certain folder和uncertain folder是一样的
        logging.info(f'** used model: {self.used_seq_model_uncertain_update}, {self.used_sta_model_uncertain_update}')


if __name__ == '__main__':
    config = UpdateUncertainConfig(args.used_config, args.config_folder, args.data_folder, args.new_normal_file,
                                   args.new_attack_file, args.old_test_part_name,
                                   args.used_seq_model_ori_num, args.used_sta_model_ori_num,
                                   args.used_seq_model_certain_num, args.used_sta_model_certain_num,
                                   args.used_seq_model_uncertain_num, args.used_sta_model_uncertain_num,
                                   args.min_sample_each_file_uncertain, args.execute_folder_name,
                                   args.alpha_margin, args.un_seq_margin, args.un_sta_margin,
                                   args.seq_contra_lamda, args.seq_recon_lamda, args.seq_tocenter_lamda,
                                   args.seq_dist_lamda,
                                   args.sta_contra_lamda, args.sta_recon_lamda, args.sta_tocenter_lamda,
                                   args.sta_dist_lamda,
                                   args.used_self_labeled_data, args.train_epoch)

    if args.used_self_labeled_data == 'yes':
        print('[INFO] Load old latent center')
        logging.info('[INFO] Load old latent center')
        sta_old_center_path = os.path.join(config.certain_save_data_root, 'train_distri_para_info_stadata.pickle')
        with open(sta_old_center_path, 'rb') as f:
            sta_old_centers = pickle.load(f)
        seq_old_center_path = os.path.join(config.certain_save_data_root, 'train_sta_info.pickle')
        with open(seq_old_center_path, 'rb') as f:
            seq_old_centers = pickle.load(f)

        print('[INFO] Load train dataset')
        logging.info('[INFO] Load train dataset')
        train_dataset = StaSeqTrafficNormalizedDatasetUpdateUncertain(
            [os.path.join(config.uncertain_data_root, i) for i in os.listdir(config.uncertain_data_root)],
            config.ori_scaler_path, False, config)
        sample_weights = get_sample_weights(train_dataset)
        sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
        train_loader_weighted = DataLoader(train_dataset, batch_size=config.batch_size, sampler=sampler)
        train_loader_noweight = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=False)

        # 适用训练初始模型的数据，约束新的特征空间和之前不是特别偏移
        print('[INFO] Load old p1 dataset')
        logging.info('[INFO] Load old p1 dataset')
        val_dataset_p1 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1], config.class_dict,
            config.detail_class_dict, config, False, config.ori_scaler_path
        )
        val_p1_part_sampler = RandomSampler(val_dataset_p1, num_samples=3000,
                                            generator=torch.Generator().manual_seed(42))
        val_p1_part_loader = DataLoader(val_dataset_p1, batch_size=config.batch_size, sampler=val_p1_part_sampler)
        val_p1_part_loader_cycle = itertools.cycle(val_p1_part_loader)

        # 用于验证差异
        val_p1_part_sampler_2 = RandomSampler(val_dataset_p1, num_samples=3000,
                                              generator=torch.Generator().manual_seed(50))
        val_p1_part_loader_2 = DataLoader(val_dataset_p1, batch_size=config.batch_size, sampler=val_p1_part_sampler)

        print('[INFO] Begin update model with uncertain')
        logging.info('[INFO] Begin update model with uncertain')
        uncertain_train_update_model(config, train_loader_weighted, val_p1_part_loader_cycle,
                                     os.path.join(config.certain_model_root, config.used_certain_seq_model),
                                     os.path.join(config.certain_model_root, config.used_certain_sta_model),
                                     config.uncertain_model_root,
                                     config.old_p2cer_seq_centers_path, config.old_p2cer_sta_centers_path)
        get_uncertain_related(config, train_loader_noweight,
                              os.path.join(config.uncertain_model_root, config.used_seq_model_uncertain_update),
                              os.path.join(config.uncertain_model_root, config.used_sta_model_uncertain_update),
                              config.uncertain_new_save_data_root)

        print('[INFO] Update distribution')
        logging.info('[INFO] Update distribution')
        combine_two_distribution_uncertain(config.old_save_data_root, config.uncertain_new_save_data_root,
                                           config.uncertain_updated_save_data_root)

        print('[INFO] Validate latent drift after uncertain update')
        logging.info('[INFO] Validate latent drift after uncertain update')
        validate_drift(val_p1_part_loader_2, os.path.join(config.certain_model_root, config.used_certain_seq_model),
                       os.path.join(config.certain_model_root, config.used_certain_sta_model),
                       os.path.join(config.uncertain_model_root, config.used_seq_model_uncertain_update),
                       os.path.join(config.uncertain_model_root, config.used_sta_model_uncertain_update),
                       config, config.uncertain_driftvalidate_save_data_root)

        print('[INFO] Load test data p1val')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p1val')
        test_dataset_p1val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p1val = DataLoader(test_dataset_p1val, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part1val')
        logging.info('[INFO] Evaluate uncertain trained model, use part1val')
        eval_model_stage2('update part2 uncertain, test p1val', config, test_loader_p1val, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p1val, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p1val, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

        print('[INFO] Load test data p2val')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p2val')
        test_dataset_p2val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p2val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p2val = DataLoader(test_dataset_p2val, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part2val')
        logging.info('[INFO] Evaluate uncertain trained model, use part2val')
        eval_model_stage2('update part2 uncertain, test p2val', config, test_loader_p2val, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p2val, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p2val, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

        print('[INFO] Evaluate model')
        print('[INFO] Load test data p3')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p3')
        test_dataset_p3 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p3],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p3 = DataLoader(test_dataset_p3, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part3')
        logging.info('[INFO] Evaluate uncertain trained model, use part3')
        eval_model_stage2('update part2 uncertain, test p3', config, test_loader_p3, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p3, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p3, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

        print('[INFO] Load test data p4val')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p4val')
        test_dataset_p4val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p4val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p4val = DataLoader(test_dataset_p4val, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part4val')
        logging.info('[INFO] Evaluate uncertain trained model, use part4val')
        eval_model_stage2('update part2 uncertain, test p4val', config, test_loader_p4val, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p4val, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p4val, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

    elif args.used_self_labeled_data == 'no':
        # ===================
        # 训练模型
        # ===================
        print('[INFO] Load train data (identify ori dist dict labels)')
        logging.info('[INFO] Load train data (identify ori dist dict labels)')
        # 如果使用根据原始数据生成的标签来更新模型
        train_dataset = StaSeqTrafficNormalizedDatasetUpdateOri(
            config.normal_uncertain_files + config.attack_uncertain_files,
            config.ori_file_root, config.ori_label_root, config.ori_scaler_path,
            config.class_dict, config)

        sample_weights = get_sample_weights(train_dataset)
        sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
        train_loader_weighted = DataLoader(train_dataset, batch_size=config.batch_size, sampler=sampler)
        train_loader_noweight = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=False)

        # 适用训练初始模型的数据，约束新的特征空间和之前不是特别偏移
        print('[INFO] Load old p1 dataset')
        logging.info('[INFO] Load old p1 dataset')
        val_dataset_p1 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1], config.class_dict,
            config.detail_class_dict, config, False, config.ori_scaler_path
        )
        val_p1_part_sampler = RandomSampler(val_dataset_p1, num_samples=3000,
                                            generator=torch.Generator().manual_seed(42))
        val_p1_part_loader = DataLoader(val_dataset_p1, batch_size=config.batch_size, sampler=val_p1_part_sampler)
        val_p1_part_loader_cycle = itertools.cycle(val_p1_part_loader)

        # 用于验证差异
        val_p1_part_sampler_2 = RandomSampler(val_dataset_p1, num_samples=3000,
                                              generator=torch.Generator().manual_seed(50))
        val_p1_part_loader_2 = DataLoader(val_dataset_p1, batch_size=config.batch_size, sampler=val_p1_part_sampler)

        print('[INFO] Begin update model with uncertain')
        logging.info('[INFO] Begin update model with uncertain')
        uncertain_train_update_model(config, train_loader_weighted, val_p1_part_loader_cycle,
                                     os.path.join(config.certain_model_root, config.used_certain_seq_model),
                                     os.path.join(config.certain_model_root, config.used_certain_sta_model),
                                     config.uncertain_model_root,
                                     config.old_p2cer_seq_centers_path, config.old_p2cer_sta_centers_path)
        get_uncertain_related(config, train_loader_noweight,
                              os.path.join(config.uncertain_model_root, config.used_seq_model_uncertain_update),
                              os.path.join(config.uncertain_model_root, config.used_sta_model_uncertain_update),
                              config.uncertain_new_save_data_root)

        print('[INFO] Update distribution')
        logging.info('[INFO] Update distribution')
        combine_two_distribution_uncertain(config.old_save_data_root, config.uncertain_new_save_data_root,
                                           config.uncertain_updated_save_data_root)

        # ===========================
        # 验证更新后的模型的偏移，及在各个验证数据集上的性能
        # ===========================
        print('[INFO] Validate latent drift after uncertain update')
        logging.info('[INFO] Validate latent drift after uncertain update')
        validate_drift(val_p1_part_loader_2, os.path.join(config.certain_model_root, config.used_certain_seq_model),
                       os.path.join(config.certain_model_root, config.used_certain_sta_model),
                       os.path.join(config.uncertain_model_root, config.used_seq_model_uncertain_update),
                       os.path.join(config.uncertain_model_root, config.used_sta_model_uncertain_update),
                       config, config.uncertain_driftvalidate_save_data_root)

        print('[INFO] Load test data p1val')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p1val')
        test_dataset_p1val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p1val = DataLoader(test_dataset_p1val, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part1val')
        logging.info('[INFO] Evaluate uncertain trained model, use part1val')
        eval_model_stage2('update part2 uncertain, test p1val', config, test_loader_p1val, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p1val, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p1val, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

        print('[INFO] Load test data p2val')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p2val')
        test_dataset_p2val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p2val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p2val = DataLoader(test_dataset_p2val, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part2val')
        logging.info('[INFO] Evaluate uncertain trained model, use part2val')
        eval_model_stage2('update part2 uncertain, test p2val', config, test_loader_p2val, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p2val, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p2val, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

        print('[INFO] Evaluate model')
        print('[INFO] Load test data p3')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p3')
        test_dataset_p3 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p3],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p3 = DataLoader(test_dataset_p3, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part3')
        logging.info('[INFO] Evaluate uncertain trained model, use part3')
        eval_model_stage2('update part2 uncertain, test p3', config, test_loader_p3, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p3, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p3, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)

        print('[INFO] Load test data p4val')
        logging.info('[INFO] Evaluate model')
        logging.info('[INFO] Load test data p4val')
        test_dataset_p4val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p4val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p4val = DataLoader(test_dataset_p4val, batch_size=config.batch_size, shuffle=False)
        print('[INFO] Evaluate uncertain trained model, use part4val')
        logging.info('[INFO] Evaluate uncertain trained model, use part4val')
        eval_model_stage2('update part2 uncertain, test p4val', config, test_loader_p4val, config.uncertain_model_root,
                          config.uncertain_updated_test_result_root_p4val, config.uncertain_updated_save_data_root,
                          config.uncertain_update_test_save_data_root_p4val, config.used_seq_model_uncertain_update,
                          config.used_sta_model_uncertain_update)