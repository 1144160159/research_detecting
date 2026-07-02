from data_provider.data_loader import Dataset_Packet2Flow, Dataset_Flow, Dataset_Packet
from torch.utils.data import DataLoader

data_dict = {
    "flow":Dataset_Flow,
    "packet":Dataset_Packet,
    "packet2flow":Dataset_Packet2Flow,
}

def data_provider(args, flag):
    Data = data_dict[args.level]
    if flag == 'test':
        shuffle_flag = False
        drop_last = True
        batch_size = args.batch_size
    else:
        shuffle_flag = True
        drop_last = True
        batch_size = args.batch_size

    data_set = Data(
        mode = args.mode,
        use_Label = args.use_Label,
        root_path=args.root_path,
        Train_data_path=args.Train_data_path,
        Test_data_path=args.Test_data_path,
        Val_data_path=args.Val_data_path,
        flag=flag,
        size=[args.seq_len, args.label_len, args.pred_len],
        features=args.features,
        # upsample only for training split
        use_upsample=getattr(args, 'use_upsample', False) if flag == 'train' else False,
        upsample_strategy=getattr(args, 'upsample_strategy', 'balanced'),
    )

    print(flag, len(data_set))
    data_loader = DataLoader(
        data_set,
        batch_size=batch_size,
        shuffle=shuffle_flag,
        num_workers=args.num_workers,
        drop_last=drop_last)
    
    
    return data_set, data_loader
