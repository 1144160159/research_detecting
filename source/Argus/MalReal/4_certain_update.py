#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   4_certain_update.py
@Contact :   hanxueying@iie.ac.cn
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2024/7/24 14:18   xueying      1.0       
'''

import os
import sys, importlib
import torch
import logging
from datetime import datetime
import argparse
from torch.utils.data import DataLoader, WeightedRandomSampler, RandomSampler

sys.path.append('/home/hxy/driftDetect/newcode0625')
sys.path.append('D:\PycharmProject\DriftDetection/newcode0625')

StaSeqTrafficNormalizedDatasetUpdate = importlib.import_module('myutil').StaSeqTrafficNormalizedDatasetUpdate
get_sample_weights = importlib.import_module('myutil').get_sample_weights
certain_train_update_model = importlib.import_module('myutil').certain_train_update_model
get_certain_related = importlib.import_module('myutil').get_certain_related
combine_two_distribution_certain = importlib.import_module('myutil').combine_two_distribution_certain
DatasetConfig1 = importlib.import_module('dataconfig_ctu').DatasetConfig1
StaSeqTrafficNormalizedDataset = importlib.import_module('myutil').StaSeqTrafficNormalizedDataset
eval_model_stage2 = importlib.import_module('myutil').eval_model_stage2
validate_drift = importlib.import_module('myutil').validate_drift
StaSeqTrafficNormalizedDatasetUpdateOri = importlib.import_module('myutil').StaSeqTrafficNormalizedDatasetUpdateOri

parser = argparse.ArgumentParser(description='step 4 certain update',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--config_folder', type=str)
parser.add_argument('--data_folder', type=str)
parser.add_argument('--model_folder', type=str)
parser.add_argument('--used_config', type=str, default='config1')
parser.add_argument('--new_normal_file', type=str, default=None)
parser.add_argument('--new_attack_file', type=str, default=None)
parser.add_argument('--idcl_eps', type=float, default=0.5)
parser.add_argument('--idcl_minpts', type=int, default=10)
parser.add_argument('--edge_div_node_threshold', type=float, default=5)
parser.add_argument('--edge_div_com_threshold', type=float, default=10)
parser.add_argument('--old_test_part_name', type=str, default='p2')  # 也就是原来更新用哪个数据，现在测试用什么数据
parser.add_argument('--used_seq_model_old_num', type=int, default=266)
parser.add_argument('--used_sta_model_old_num', type=int, default=266)
parser.add_argument('--used_seq_model_certainupdate_num', type=int, default=10)
parser.add_argument('--used_sta_model_certainupdate_num', type=int, default=10)
parser.add_argument('--min_sample_each_file_certain', type=int, default=1000)
parser.add_argument('--cu_seq_margin', type=float, default=10)
parser.add_argument('--cu_sta_margin', type=float, default=10)
parser.add_argument('--seq_contra_lamda', type=float, default=1)
parser.add_argument('--seq_recon_lamda', type=float, default=0.05)
parser.add_argument('--seq_dist_lamda', type=float, default=0.0001)
parser.add_argument('--sta_contra_lamda', type=float, default=1)
parser.add_argument('--sta_recon_lamda', type=float, default=0.05)
parser.add_argument('--sta_dist_lamda', type=float, default=0.0001)
parser.add_argument('--used_self_labeled_data', type=str, default='yes')  # 是否使用自己生成的标签数据来更新模型（可能存在被错误标记的数据）
parser.add_argument('--execute_folder_name', type=str, default='6_ctu_script_new')
parser.add_argument('--train_epoch', type=int, default=100)

args = parser.parse_args()


def check_paths(paths):
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)


class UpdateCertainConfig:
    def __init__(self, used_config, config_folder, data_folder, model_folder, new_normal_file, new_attack_file,
                 idcl_eps=0.5, idcl_minpts=10,
                 edge_div_node_threshold=5, edge_div_com_threshold=10, old_test_part_name='p2',
                 used_seq_model_old_num=350, used_sta_model_old_num=350,
                 used_seq_model_certainupdate_num=10, used_sta_model_certainupdate_num=10,
                 min_sample_each_file_certain=1000,
                 cu_seq_margin=10, cu_sta_margin=10,
                 seq_contra_lamda=1, seq_recon_lamda=0.05, seq_dist_lamda=0.0001,
                 sta_contra_lamda=1, sta_recon_lamda=0.05, sta_dist_lamda=0.0001, execute_folder_name='none',
                 used_self_labeled_data='yes', train_epoch=100):

        """
        :param new_normal_file_name: 正常文件在聚类之后一起存储到了一个新的文件中，这是那个文件的名字 'normal_kmeans_k2_dm0.05.pickle'
        :param update_train_part: 使用哪部分数据来更新模型，一般情况下只能是p2，对应1_identify_drift.py中的test_part_name
        :param used_mode: 使用哪个模型，这里只给出数字，具体的名字由后面组合得到
        :param min_sample_each_file_certain: 如果一个文件中的样本数少于这些，就不使用这个文件
        :param cu_seq_margin, cu_sta_margin: 更新模型的时候的margin参数
        :param xxx_lamda: 各项损失的权重
        """
        self.used_config = used_config

        self.config_folder = config_folder
        self.data_folder = data_folder
        self.model_folder = model_folder
        self.ori_file_root = f'/home/hxy/driftDetect/0_data/2_captured_traffic/ctu_all_run_data/{self.data_folder}'
        self.new_normal_file = new_normal_file
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
        else:
            print(f'[ERROR] Config input unmatch, input: {self.used_config}')
            logging.info(f'[ERROR] Config input unmatch, input: {self.used_config}')

        # 来自step2的参数
        # 确定certain的列，这几个没有变化，就不通过参数传递了
        self.cocertain_row = 'dist_co_certain'  # 看seq和sta的结果是否一致
        self.consider_unmatch = True  # 是否考虑seq和sta结果不一致的情况，true就是把不匹配的也视为uncertain
        self.used_uncertain_row = 'cla_md_recon_uncertain_3'
        self.regenerate_cocertain = False
        # 在identify的时候聚类的参数
        self.idcl_eps = idcl_eps  # 0.5
        self.idcl_minpts = idcl_minpts  # 10
        # 在判断聚类得到的簇是否为恶意时的参数
        self.edge_div_node_threshold = edge_div_node_threshold  # 5
        self.edge_div_com_threshold = edge_div_com_threshold  # 10

        # 主要是用来产生路径
        self.certain_name_folder = f'{self.cocertain_row}-{self.used_uncertain_row}-eps{self.idcl_eps}minpts{self.idcl_minpts}-thre{self.edge_div_node_threshold}_{self.edge_div_com_threshold}'
        # 用于更新模型的数据所在的路径（如果使用的是identify drift生成的数据）
        self.certain_data_root = os.path.join(self.ori_file_root,
                                              f'{self.old_test_part_name}_certain/{self.certain_name_folder}')
        # 根据原始数据生成的真实的数据标签所在的路径（如果不使用identify drift生成的数据）[这个只和原始的聚类的划分有关，和config folder没有关系]
        self.ori_label_root = os.path.join(self.ori_file_root, f'ori_label_{self.old_test_part_name}')  # 只有标签，没有数据

        # 更新的基准是哪个模型
        self.used_seq_model_old = f'seq_model_{used_seq_model_old_num}.pth'
        self.used_sta_model_old = f'sta_model_{used_sta_model_old_num}.pth'

        # 更新后的模型是哪个
        self.used_seq_model_certain_update = f'seq_model_{used_seq_model_certainupdate_num}.pth'
        self.used_sta_model_certain_update = f'sta_model_{used_sta_model_certainupdate_num}.pth'

        # 旧模型的路径
        self.step1_model_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/model/part1/{self.model_folder}'
        self.old_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/part1/{self.config_folder}'
        # 更新后的模型的路径（路径中包含了原来使用的是什么模型）
        self.certain_model_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/model/p1{self.old_test_part_name}_certain' \
                                  f'/{self.config_folder}/certain_usesl_{used_self_labeled_data}_om{used_seq_model_old_num}_{used_sta_model_old_num}'

        # 使用了更新后的模型的临时的一个路径文件夹，因为后面很多用这个的
        certain_update_tmp_folder_name = f'certain_usesl_{used_self_labeled_data}_om{used_seq_model_old_num}_{used_sta_model_old_num}_cm{used_seq_model_certainupdate_num}_{used_sta_model_certainupdate_num}'
        # 单纯p2的数据作为训练数据的更新结果（原来使用的模型，certain更新使用的模型）
        self.certain_new_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain' \
                                          f'/{self.config_folder}/{certain_update_tmp_folder_name}/{self.old_test_part_name}_new'
        # 将p1和p2的数据合并得到的结果
        self.certain_updated_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain' \
                                              f'/{self.config_folder}/{certain_update_tmp_folder_name}/{self.old_test_part_name}_updated'
        # 验证在使用certain更新的模型上，数据偏移了多少，存储中间结果，主要是用过去的数据处理
        self.certain_driftvalidate_save_data_root = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain_driftvalidate' \
                                                    f'/{self.config_folder}/{certain_update_tmp_folder_name}'

        check_paths([self.certain_model_root, self.certain_new_save_data_root, self.certain_updated_save_data_root,
                     self.certain_driftvalidate_save_data_root])

        # 验证更新后的模型在其他数据集上的性能
        self.certain_update_test_save_data_root_p1val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p1val'
        self.certain_update_test_result_root_p1val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p1val'
        self.certain_update_test_save_data_root_p2val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p2val'
        self.certain_update_test_result_root_p2val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p2val'
        self.certain_update_test_save_data_root_p3 = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p3'
        self.certain_update_test_result_root_p3 = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p3'
        self.certain_update_test_save_data_root_p4val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/save_data/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p4val'
        self.certain_update_test_result_root_p4val = f'/home/hxy/driftDetect/newcode0625/{execute_folder_name}/result/p1{self.old_test_part_name}_certain/{self.config_folder}/{self.old_test_part_name}_updated/{certain_update_tmp_folder_name}/p4val'
        check_paths([self.certain_update_test_save_data_root_p1val, self.certain_update_test_result_root_p1val,
                     self.certain_update_test_save_data_root_p2val, self.certain_update_test_result_root_p2val,
                     self.certain_update_test_save_data_root_p3, self.certain_update_test_result_root_p3,
                     self.certain_update_test_save_data_root_p4val, self.certain_update_test_result_root_p4val])

        self.min_sample_each_file_certain = min_sample_each_file_certain  # 1000  # 如果一个文件中的样本数少于这些，就不使用这个文件

        # 测试数据的路径
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

        # =======
        # 更新训练模型的参数
        self.batch_size = 1024
        self.train_epoch = train_epoch
        self.seq_lr = 0.001
        self.sta_lr = 0.001
        self.seq_eta_min = 1e-05
        self.sta_eta_min = 1e-05

        self.seq_margin = cu_seq_margin  # 10
        self.sta_margin = cu_sta_margin  # 10
        self.temperature = 1

        # 在计算损失的时候各项的权重
        self.seq_contra_lamda = seq_contra_lamda  # 1
        self.seq_recon_lamda = seq_recon_lamda  # 0.05  # /20
        self.seq_dist_lamda = seq_dist_lamda  # 0.0001  # /10000
        self.sta_contra_lamda = sta_contra_lamda  # 1
        self.sta_recon_lamda = sta_recon_lamda  # 0.05  # /20
        self.sta_dist_lamda = sta_dist_lamda  # 0.0001  # /10000

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

        logging.basicConfig(level=logging.DEBUG,
                            filename=f'log/updata-certain-{self.config_folder}-certain_usesl_{used_self_labeled_data}.log',
                            format='%(message)s')
        logging.info('\n\n ====== ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ======\n\n')
        logging.info('\n******** update certain ********\n')
        logging.info(f'** certain: {self.certain_name_folder} **')
        logging.info(f'** ori model: {self.used_seq_model_old}, {self.used_sta_model_old}')
        logging.info(f'** used updated model: {self.used_seq_model_certain_update}, {self.used_sta_model_certain_update}')

        # 原来的scaler的路径
        self.ori_scaler_path = os.path.join(self.old_save_data_root, 'scaler.pickle')


if __name__ == '__main__':
    config = UpdateCertainConfig(args.used_config, args.config_folder, args.data_folder, args.model_folder,
                                 args.new_normal_file, args.new_attack_file,
                                 args.idcl_eps, args.idcl_minpts, args.edge_div_node_threshold,
                                 args.edge_div_com_threshold,
                                 args.old_test_part_name,
                                 args.used_seq_model_old_num, args.used_sta_model_old_num,
                                 args.used_seq_model_certainupdate_num, args.used_sta_model_certainupdate_num,
                                 args.min_sample_each_file_certain,
                                 args.cu_seq_margin, args.cu_sta_margin,
                                 args.seq_contra_lamda, args.seq_recon_lamda, args.seq_dist_lamda,
                                 args.sta_contra_lamda, args.sta_recon_lamda, args.sta_dist_lamda,
                                 args.execute_folder_name,
                                 args.used_self_labeled_data, args.train_epoch)

    if args.used_self_labeled_data == 'yes':
        # 如果使用drift identify步骤生成的数据更新模型
        # ============================
        # 使用第一阶段的certain数据更新模型，进行训练，并保存和训练数据相关的内容
        # ============================
        print('[INFO] Load train data (identify drift labels)')
        logging.info('[INFO] Load train data (identify drift labels)')
        train_dataset = StaSeqTrafficNormalizedDatasetUpdate(
            [os.path.join(config.certain_data_root, i) for i in os.listdir(config.certain_data_root)],
            config.ori_scaler_path, config)
        sample_weights = get_sample_weights(train_dataset)
        sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
        train_loader_weighted = DataLoader(train_dataset, batch_size=config.batch_size, sampler=sampler)
        train_loader_noweight = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=False)

        # 使用certain数据更新模型，重新训练
        print('[INFO] Use certain data to update model (identify drift labels)')
        logging.info('[INFO] Use certain data to update model (identify drift labels)')
        certain_train_update_model(config, train_loader_weighted,
                                   os.path.join(config.step1_model_root, config.used_seq_model_old),
                                   os.path.join(config.step1_model_root, config.used_sta_model_old),
                                   config.certain_model_root)
        print('[INFO] Get certain data trained model related info')
        logging.info('[INFO] Get certain data trained model related info')
        get_certain_related(config, train_loader_noweight,
                            os.path.join(config.certain_model_root, config.used_seq_model_certain_update),
                            os.path.join(config.certain_model_root, config.used_sta_model_certain_update),
                            config.certain_new_save_data_root)
        print('[INFO] Update distribution')
        logging.info('[INFO] Update distribution')
        combine_two_distribution_certain(config.old_save_data_root, config.certain_new_save_data_root,
                                         config.certain_updated_save_data_root)

        # ============================
        # 使用训练好的模型进行验证
        # ============================
        # 使用部分原始训练数据，验证更新后的模型和原始的数据有多少偏移
        print('[INFO] Validate latent drift after certain update (identify drift labels)')
        logging.info('[INFO] Validate latent drift after certain update (identify drift labels)')
        test_dataset_p1 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1], config.class_dict,
            config.detail_class_dict, config, False, config.ori_scaler_path
        )
        test_p1_part_sampler = RandomSampler(test_dataset_p1, num_samples=3000,
                                             generator=torch.Generator().manual_seed(42))
        test_p1_part_loader = DataLoader(test_dataset_p1, batch_size=config.batch_size, sampler=test_p1_part_sampler)
        validate_drift(test_p1_part_loader, os.path.join(config.step1_model_root, config.used_seq_model_old),
                       os.path.join(config.step1_model_root, config.used_sta_model_old),
                       os.path.join(config.certain_model_root, config.used_seq_model_certain_update),
                       os.path.join(config.certain_model_root, config.used_sta_model_certain_update),
                       config, config.certain_driftvalidate_save_data_root)

        # 在验证集上验证模型的性能
        # p1 val
        print('[INFO] Load test data p1val')
        logging.info('[INFO] Load test data p1val')
        test_dataset_p1val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p1val = DataLoader(test_dataset_p1val, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p1val (identify drift labels)')
        logging.info('[INFO] Evaluate certain trained model, use p1val (identify drift labels)')
        eval_model_stage2('updated part2 certain, test p1val', config, test_loader_p1val, config.certain_model_root,
                          config.certain_update_test_result_root_p1val,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p1val,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

        # p2 val
        print('[INFO] Load test data p2val')
        logging.info('[INFO] Load test data p2val')
        test_dataset_p2val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p2val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p2val = DataLoader(test_dataset_p2val, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p2val (identify drift labels)')
        logging.info('[INFO] Evaluate certain trained model, use p2val (identify drift labels)')
        eval_model_stage2('updated part2 certain, test p2val', config, test_loader_p2val, config.certain_model_root,
                          config.certain_update_test_result_root_p2val,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p2val,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

        # p3
        print('[INFO] Load test data p3')
        logging.info('[INFO] Load test data p3')
        test_dataset_p3 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p3],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p3 = DataLoader(test_dataset_p3, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p3 (identify drift labels)')
        logging.info('[INFO] Evaluate certain trained model, use p3 (identify drift labels)')
        eval_model_stage2('updated part2 certain, test p3', config, test_loader_p3, config.certain_model_root,
                          config.certain_update_test_result_root_p3,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p3,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

        # p4
        print('[INFO] Load test data p4val')
        logging.info('[INFO] Load test data p4val')
        test_dataset_p4val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p4val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p4val = DataLoader(test_dataset_p4val, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p4val (identify drift labels)')
        logging.info('[INFO] Evaluate certain trained model, use p4val (identify drift labels)')
        eval_model_stage2('updated part2 certain, test p4val', config, test_loader_p4val, config.certain_model_root,
                          config.certain_update_test_result_root_p4val,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p4val,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

    elif args.used_self_labeled_data == 'no':
        print('[INFO] Load train data (identify ori dist dict labels)')
        logging.info('[INFO] Load train data (identify ori dist dict labels)')
        # 如果使用根据原始数据生成的标签来更新模型
        train_dataset = StaSeqTrafficNormalizedDatasetUpdateOri(
            config.normal_certain_files + config.attack_certain_files,
            config.ori_file_root, config.ori_label_root, config.ori_scaler_path,
            config.class_dict, config)
        sample_weights = get_sample_weights(train_dataset)
        sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
        train_loader_weighted = DataLoader(train_dataset, batch_size=config.batch_size, sampler=sampler)
        train_loader_noweight = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=False)

        # 使用certain数据更新模型，重新训练
        print('[INFO] Use certain data to update model (identify ori dist dict labels)')
        logging.info('[INFO] Use certain data to update model (identify ori dist dict labels)')
        certain_train_update_model(config, train_loader_weighted,
                                   os.path.join(config.step1_model_root, config.used_seq_model_old),
                                   os.path.join(config.step1_model_root, config.used_sta_model_old),
                                   config.certain_model_root)
        print('[INFO] Get certain data trained model related info')
        logging.info('[INFO] Get certain data trained model related info')
        get_certain_related(config, train_loader_noweight,
                            os.path.join(config.certain_model_root, config.used_seq_model_certain_update),
                            os.path.join(config.certain_model_root, config.used_sta_model_certain_update),
                            config.certain_new_save_data_root)
        print('[INFO] Update distribution')
        logging.info('[INFO] Update distribution')
        combine_two_distribution_certain(config.old_save_data_root, config.certain_new_save_data_root,
                                         config.certain_updated_save_data_root)

        # ============================
        # 使用训练好的模型进行验证
        # ============================
        # 使用部分原始训练数据，验证更新后的模型和原始的数据有多少偏移
        print('[INFO] Validate latent drift after certain update (identify ori dist dict labels)')
        logging.info('[INFO] Validate latent drift after certain update (identify ori dist dict labels)')
        test_dataset_p1 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1], config.class_dict,
            config.detail_class_dict, config, False, config.ori_scaler_path
        )
        test_p1_part_sampler = RandomSampler(test_dataset_p1, num_samples=3000,
                                             generator=torch.Generator().manual_seed(42))
        test_p1_part_loader = DataLoader(test_dataset_p1, batch_size=config.batch_size, sampler=test_p1_part_sampler)
        validate_drift(test_p1_part_loader, os.path.join(config.step1_model_root, config.used_seq_model_old),
                       os.path.join(config.step1_model_root, config.used_sta_model_old),
                       os.path.join(config.certain_model_root, config.used_seq_model_certain_update),
                       os.path.join(config.certain_model_root, config.used_sta_model_certain_update),
                       config, config.certain_driftvalidate_save_data_root)

        # 在验证集上验证模型的性能
        # p1 val
        print('[INFO] Load test data p1val')
        logging.info('[INFO] Load test data p1val')
        test_dataset_p1val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p1val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p1val = DataLoader(test_dataset_p1val, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p1val (identify ori dist dict labels)')
        logging.info('[INFO] Evaluate certain trained model, use p1val (identify ori dist dict labels)')
        eval_model_stage2('updated part2 certain, test p1val', config, test_loader_p1val, config.certain_model_root,
                          config.certain_update_test_result_root_p1val,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p1val,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

        # p2 val
        print('[INFO] Load test data p2val')
        logging.info('[INFO] Load test data p2val')
        test_dataset_p2val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p2val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p2val = DataLoader(test_dataset_p2val, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p2val (identify ori dist dict labels)')
        logging.info('[INFO] Evaluate certain trained model, use p2val (identify ori dist dict labels)')
        eval_model_stage2('updated part2 certain, test p2val', config, test_loader_p2val, config.certain_model_root,
                          config.certain_update_test_result_root_p2val,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p2val,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

        # p3
        print('[INFO] Load test data p3')
        logging.info('[INFO] Load test data p3')
        test_dataset_p3 = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p3],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p3 = DataLoader(test_dataset_p3, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p3 (identify ori dist dict labels)')
        logging.info('[INFO] Evaluate certain trained model, use p3 (identify ori dist dict labels)')
        eval_model_stage2('updated part2 certain, test p3', config, test_loader_p3, config.certain_model_root,
                          config.certain_update_test_result_root_p3,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p3,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)

        # p4
        print('[INFO] Load test data p4val')
        logging.info('[INFO] Load test data p4val')
        test_dataset_p4val = StaSeqTrafficNormalizedDataset(
            [os.path.join(config.ori_file_root, i) for i in config.test_files_p4val],
            config.class_dict, config.detail_class_dict, config, False, config.ori_scaler_path)
        test_loader_p4val = DataLoader(test_dataset_p4val, batch_size=config.batch_size, shuffle=False)

        print('[INFO] Evaluate certain trained model, use p4val (identify ori dist dict labels)')
        logging.info('[INFO] Evaluate certain trained model, use p4val (identify ori dist dict labels)')
        eval_model_stage2('updated part2 certain, test p4val', config, test_loader_p4val, config.certain_model_root,
                          config.certain_update_test_result_root_p4val,
                          config.certain_updated_save_data_root, config.certain_update_test_save_data_root_p4val,
                          config.used_seq_model_certain_update, config.used_sta_model_certain_update)
