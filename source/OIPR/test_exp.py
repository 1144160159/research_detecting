# -*- coding: utf-8 -*-
if __name__ == "__main__":
    import os
    import pandas as pd
    from evaluation_methods import evaluate_OIPR
    
    # In[]
    import yaml    
    config_file_path = os.path.join(os.path.dirname(__file__), 
                                    'config.yaml')
    
    f = open(config_file_path, 'r', encoding='utf-8')
    config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()    
    
    rl = config['rl']
    OIPR_config = config['OIPR']
    # In[]
    dataset_list = ['overlap proportion (c1)',
                    'overlap proportion (c2)',
                    'overlap proportion (c3)',
                    'overlap proportion (c4)',
                    'fragmented TP (c1)',
                    'fragmented TP (c2)',
                    'fragmented TP (c3)',
                    'fragmented FP (c1)',
                    'fragmented FP (c2)',
                    'fragmented FP (c3)',
                    'temporal shifting (c1)',
                    'temporal shifting (c2)',
                    'TP position (c1)',
                    'TP position (c2)',
                    'TP position (c3)',
                    'TP position (c4)',
                    'long anomaly effect (c1)',
                    'long anomaly effect (c2)',
                    'long anomaly effect (c3)',
                    'sparse anomalies (c1)',
                    'sparse anomalies (c2)',
                    'constant detector (c1)',
                    'constant detector (c2)',
                    ]
    
    # dataset_list = [
    #                 'random detector (c1)',
    #                 'random detector (c2)',
    #                 ]  
    
    for dataset in dataset_list:
        print(f'====={dataset}=====')
        data_df = pd.read_csv(f'./datasets/special_scenario_dataset/{dataset}.csv')
        gt = data_df['gt'].values.astype(int)
        pred = data_df['pred'].values.astype(int)            
        precision, recall, f1_score = evaluate_OIPR(gt, pred, **OIPR_config)
        print(f'OIPR: pre={round(precision, rl)}, rec={round(recall, rl)}, f1={round(f1_score, rl)}')
            
    