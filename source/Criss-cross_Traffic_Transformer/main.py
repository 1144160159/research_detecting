import argparse
import os
import torch
from exp.exp_main import Exp_Main
import random
import numpy as np
import json

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='The CTT model for network traffic classification and forecasting')

    # random seed
    parser.add_argument('--random_seed', type=int, default=42, help='random seed')

    # basic config
    parser.add_argument('--is_training', action='store_true', help='status')
    parser.add_argument('--model', type=str,  default='CTT', help='model name, options: [CTT]')
    parser.add_argument('--model_id', type=str, default='test', help='model id for experiment tracking')
    parser.add_argument('--mode', type=str, default='analysis', help='analysis or pred is available')
    parser.add_argument('--level', type=str, default='flow', help='packet or flow or packet2flow is available')
    
    # data loader
    parser.add_argument('--data', type=str, default='ISCX-VPN-2016', help='dataset name')
    parser.add_argument('--root_path', type=str, default='./dataset/', help='root path of the data file')
    parser.add_argument('--Train_data_path', type=str, default='ISCXVPN2016_Train.csv', help='Train data file')
    parser.add_argument('--Test_data_path', type=str, default='ISCXVPN2016_Test.csv', help='Test data file')
    parser.add_argument('--Val_data_path', type=str, default='ISCXVPN2016_Test.csv', help='Test data file')
    parser.add_argument('--features', type=str, default='MS',
                        help='forecasting task, options:[M, S, MS]; M:multivariate predict multivariate, S:univariate predict univariate, MS:multivariate predict univariate')
    parser.add_argument('--target', type=str, default='Label', help='target feature in S or MS task')
    parser.add_argument('--checkpoints', type=str, default='./checkpoints/', help='path of model checkpoints')

    # forecasting task
    parser.add_argument('--seq_len', type=int, default=64, help='input sequence length')
    parser.add_argument('--label_len', type=int, default=64, help='start token length for forecasting task')
    parser.add_argument('--pred_len', type=int, default=12, help='prediction sequence length')
    
    # CTT
    parser.add_argument('--fc_dropout', type=float, default=0.3, help='fully connected dropout')
    parser.add_argument('--head_dropout', type=float, default=0.1, help='head dropout')
    parser.add_argument('--cross_attn_dropout', type=float, default=0.1, help='cross attention dropout')
    parser.add_argument('--cross_dropout', type=float, default=0.1, help='cross function dropout')
    parser.add_argument('--patch_len', type=int, default=4, help='patch length')
    parser.add_argument('--stride', type=int, default=2, help='stride')
    parser.add_argument('--padding_patch', default='end', help='None: None; end: padding on the end')
    # Formers 
    parser.add_argument('--embed_type', type=int, default=0, help='0: default 1: value embedding + temporal embedding + positional embedding 2: value embedding + temporal embedding 3: value embedding + positional embedding 4: value embedding')
    parser.add_argument('--enc_in', type=int, default=17, help='encoder input size') 
    parser.add_argument('--dec_in', type=int, default=17, help='decoder input size')
    parser.add_argument('--c_out', type=int, default=7, help='the number of categories of the dataset')
    parser.add_argument('--d_model', type=int, default=128, help='dimension of hidden states in the model')
    parser.add_argument('--n_heads', type=int, default=16, help='number of heads in the multi-head attention')
    parser.add_argument('--e_layers', type=int, default=3, help='number of encoder layers')
    parser.add_argument('--d_layers', type=int, default=1, help='num of decoder layers')
    parser.add_argument('--d_ff', type=int, default=256, help='dimension of fcn')
    parser.add_argument('--factor', type=int, default=10, help='attn factor')
    parser.add_argument('--dropout', type=float, default=0.0, help='dropout')
    parser.add_argument('--embed', type=str, default='timeF',
                        help='time features encoding, options:[timeF, fixed, learned]')
    parser.add_argument('--revin', type=int, default=0, help='RevIN; True 1 False 0')
    parser.add_argument('--affine', type=int, default=0, help='RevIN-affine; True 1 False 0')
    parser.add_argument('--subtract_last', type=int, default=0, help='0: subtract mean; 1: subtract last')
    parser.add_argument('--individual', type=int, default=0, help='individual head; True 1 False 0')
    parser.add_argument('--activation', type=str, default='gelu', help='activation')
    parser.add_argument('--use_Label', action='store_false', help='whether use former Label')
    # optimization
    parser.add_argument('--num_workers', type=int, default=1, help='data loader num workers')
    parser.add_argument('--itr', type=int, default=1, help='experiments times')
    parser.add_argument('--train_epochs', type=int, default=100, help='train epochs')
    parser.add_argument('--batch_size', type=int, default=128, help='batch size of train input data')
    parser.add_argument('--patience', type=int, default=20, help='early stopping patience')
    parser.add_argument('--learning_rate', type=float, default=0.0001, help='optimizer learning rate')
    parser.add_argument('--des', type=str, default='test', help='exp description')
    parser.add_argument('--loss', type=str, default='CE', help='loss function')
    # upsampling for imbalanced classification
    parser.add_argument('--use_upsample', action='store_true', help='whether to upsample minority classes in training set')
    parser.add_argument('--upsample_strategy', type=str, default='balanced',
                        choices=['balanced', 'median', 'mean'],
                        help='upsampling strategy: balanced (to max), median (to median), mean (to mean)')
    parser.add_argument('--lradj', type=str, default='type3', help='adjust learning rate')
    parser.add_argument('--pct_start', type=float, default=0.3, help='pct_start')

    # GPU
    parser.add_argument('--use_gpu', action='store_true', help='use gpu')
    parser.add_argument('--gpu', type=int, default=1, help='gpu id')
    parser.add_argument('--use_multi_gpu', action='store_true', help='use multiple gpus')
    parser.add_argument('--devices', type=str, default='0,1,2,3', help='device ids of multile gpus')
    
    # grid search
    parser.add_argument('--grid_search', action='store_true', help='enable grid search for hyperparameter tuning')
    parser.add_argument('--grid_search_space', type=str, default=None, 
                        help='path to JSON file with custom search space (optional)')
    parser.add_argument('--grid_search_metric', type=str, default='f1_score', 
                        help='metric to optimize in grid search: f1_score, accuracy, or loss')
    parser.add_argument('--grid_search_results_dir', type=str, default='./grid_search_results',
                        help='directory to save grid search results')
    
    # args = parser.parse_args()
    args, unknown = parser.parse_known_args()
    # random seed
    fix_seed = args.random_seed
    set_seed(fix_seed)
    
    c_out_dict = {'ISCX-VPN-2016':7,'ISCX-Tor-2017':8,'USTC-TFC2016':20,'CIC-IoT-2022':10,'CSTNet':120}
    if args.mode == 'analysis':
        args.pred_len = args.seq_len
        args.c_out = c_out_dict[args.data]
        args.use_Label = False
        args.use_CNN = True
    else:
        args.target = 'Label'
        args.level = 'flow'
        args.c_out = c_out_dict[args.data]
        args.use_CNN = False
    args.use_gpu = True if torch.cuda.is_available() and args.use_gpu else False


    if args.use_gpu and args.use_multi_gpu:
        args.dvices = args.devices.replace(' ', '')
        device_ids = args.devices.split(',')
        args.device_ids = [int(id_) for id_ in device_ids]
        args.gpu = args.device_ids[0]

    print('Args in experiment:')
    print(args)

    # Grid search mode
    if args.grid_search and args.is_training:
        from utils.grid_search import run_grid_search, get_default_search_space
        
        # Load custom search space if provided
        if args.grid_search_space and os.path.exists(args.grid_search_space):
            with open(args.grid_search_space, 'r') as f:
                search_space = json.load(f)
            print(f"Loaded custom search space from {args.grid_search_space}")
        else:
            search_space = get_default_search_space()
            print("Using default search space")
        
        print(f"Grid search will optimize: {args.grid_search_metric}")
        print(f"Search space: {search_space}")
        
        # Run grid search
        best_params, best_score = run_grid_search(
            base_args=args,
            search_space=search_space,
            metric=args.grid_search_metric,
            results_dir=args.grid_search_results_dir
        )
        
        # Update args with best parameters
        print(f"\n{'='*80}")
        print("Updating arguments with best parameters from grid search:")
        for key, value in best_params.items():
            setattr(args, key, value)
            print(f"  {key}: {value}")
        print(f"{'='*80}\n")
        
        # Re-apply mode-specific settings after grid search
        if args.mode == 'analysis':
            args.pred_len = args.seq_len
        else:
            args.target = 'Label'
            args.level = 'flow'
    
    Exp = Exp_Main  

    if args.is_training:
        for ii in range(args.itr): # for each try time 
            # setting record of experiments
            setting = '{}_{}_{}_{}_{}_ft{}_sl{}_ll{}_pl{}_dm{}_nh{}_el{}_dl{}_df{}_fc{}_eb{}_dt{}_{}_{}_{}'.format(
                args.level,
                args.enc_in,
                args.model_id,
                args.model,
                args.data,
                args.features,
                args.seq_len,
                args.label_len,
                args.pred_len,
                args.d_model,
                args.n_heads,
                args.e_layers,
                args.d_layers,
                args.d_ff,
                args.factor,
                args.embed,
                args.des,ii,
                args.learning_rate
                )

            exp = Exp(args)  # set experiments
            print('>>>>>>>start training : {}>>>>>>>>>>>>>>>>>>>>>>>>>>'.format(setting))
            exp.train(setting)

            print('>>>>>>>testing : {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'.format(setting))
            exp.test(setting)

            if args.do_predict:
                print('>>>>>>>predicting : {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'.format(setting))
                exp.predict(setting, True)

            torch.cuda.empty_cache()
    else:
        ii = 0
        setting = '{}_{}_{}_{}_ft{}_sl{}_ll{}_pl{}_dm{}_nh{}_el{}_dl{}_df{}_fc{}_eb{}_dt{}_{}_{}'.format(
                                                                                                    args.enc_in,
                                                                                                    args.model_id,
                                                                                                    args.model,
                                                                                                    args.data,
                                                                                                    args.features,
                                                                                                    args.seq_len,
                                                                                                    args.label_len,
                                                                                                    args.pred_len,
                                                                                                    args.d_model,
                                                                                                    args.n_heads,
                                                                                                    args.e_layers,
                                                                                                    args.d_layers,
                                                                                                    args.d_ff,
                                                                                                    args.factor,
                                                                                                    args.embed,
                                                                                                    args.des, ii)
        exp = Exp(args)  # set experiments
        print('>>>>>>>testing : {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'.format(setting))
        exp.test(setting, test=1)
        torch.cuda.empty_cache()
        