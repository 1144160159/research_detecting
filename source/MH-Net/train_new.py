import argparse
import torch
import torch.nn as nn
from dgl.dataloading import GraphDataLoader
import torch.utils

from dataloader import MixTrafficFlowDataset4DGL
from model_new_aug import MixTemporalGNN
from optim import GradualWarmupScheduler
from utils import set_seed, get_device, mix_collate_cl_fn,get_all_device
from config import *

def train():
    model = MixTemporalGNN(num_classes=config.NUM_CLASSES, embedding_size=config.EMBEDDING_SIZE, h_feats=config.H_FEATS,
                           dropout=config.DROPOUT, downstream_dropout=config.DOWNSTREAM_DROPOUT, point=opt.point,
                           seq_aug_ratio=opt.seq_aug_ratio, drop_edge_ratio=opt.drop_edge_ratio,
                           drop_node_ratio=opt.drop_node_ratio, K=opt.K, hp_ratio=opt.hp_ratio, tau=opt.tau, gtau=opt.gtau)
    dataset = MixTrafficFlowDataset4DGL(
                                        hetro_path = config.TRAIN_GRAPH_COMBINE,
                                        bit_hetro_path = config.TRAIN_GRAPH_COMBINE_4bit,
                                        point=opt.point,
                                        perc=opt.perc)
    dataloader = GraphDataLoader(dataset, batch_size=config.BATCH_SIZE if opt.bs == -1 else opt.bs, shuffle=True, collate_fn=mix_collate_cl_fn,
                                 num_workers=num_workers, pin_memory=True,drop_last=True)
    
    model = model.to(device)
    model.train()
    num_steps = len(dataloader) * config.MAX_EPOCH
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LR, weight_decay=config.WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer=optimizer, T_max=num_steps - int(num_steps * config.WARM_UP), eta_min=config.LR_MIN)
    warmup_scheduler = GradualWarmupScheduler(optimizer, warmup_iter=int(num_steps * config.WARM_UP), after_scheduler=scheduler)
    warmup_scheduler.step()
    criterion = nn.CrossEntropyLoss(label_smoothing=config.LABEL_SMOOTHING)
    
    for epoch in range(config.MAX_EPOCH):
        num_correct = 0
        num_tests = 0
        num_correct_packet = 0
        num_tests_packet = 0 
        loss_all = []
        for batch_id, (hetro_data,bit_hetro_data,labels,hetro_mask,bit_hetro_mask) in enumerate(dataloader):
            hetro_data = hetro_data.to(device, non_blocking=True)
            bit_hetro_data = bit_hetro_data.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            pred, cl_loss, graph_cl_loss, packet_out, packet_label, bit_graph_cl_loss,bit_cl_loss \
                = model(hetro_data,bit_hetro_data, labels, hetro_mask,bit_hetro_mask)
            loss = criterion(pred, labels) + (cl_loss + bit_cl_loss) * opt.coe + (graph_cl_loss+bit_graph_cl_loss) * opt.coe_graph + criterion(packet_out, packet_label)
            loss_all.append(float(loss))
            num_correct += (pred.argmax(1) == labels).sum().item()
            num_tests += len(labels)
            num_correct_packet += (packet_out.argmax(1) == packet_label).sum().item()
            num_tests_packet += len(packet_label)
            loss /= (config.GRADIENT_ACCUMULATION if opt.ga == -1 else opt.ga)
            loss.backward()
            if ((batch_id + 1) % (config.GRADIENT_ACCUMULATION if opt.ga == -1 else opt.ga) == 0) or (batch_id + 1 == len(dataloader)):
                optimizer.step()
                optimizer.zero_grad()
            warmup_scheduler.step()
            if epoch % 1 == 0:
                print('In epoch {}, lr: {:.5f}, loss: {:.4f}, acc：{:.3f}, acc_packet：{:.3f}'.format( epoch, optimizer.param_groups[0]['lr'], float(loss), num_correct / num_tests, num_correct_packet / num_tests_packet))

    torch.save(model.state_dict(), config.MIX_MODEL_CHECKPOINT[:-4] + '_' + str(opt.prefix) + '.pth')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="dataset", required=True)
    parser.add_argument("--num_workers", type=int, help="num workers", default=-1)
    parser.add_argument("--prefix", type=str, required=True)
    parser.add_argument("--point", type=int, default=15)
    parser.add_argument("--coe", type=float, default=1.0)
    parser.add_argument("--coe_graph", type=float, default=1.0)
    parser.add_argument("--seq_aug_ratio", type=float, default=0.8)
    parser.add_argument("--tau", type=float, default=0.07)
    parser.add_argument("--gtau", type=float, default=0.07)
    parser.add_argument("--drop_edge_ratio", type=float, default=0.1)
    parser.add_argument("--drop_node_ratio", type=float, default=0.1)
    parser.add_argument("--K", type=int, default=15)
    parser.add_argument("--hp_ratio", type=float, default=0.5)
    parser.add_argument("--perc", type=float, default=1.0)
    parser.add_argument("--bs", type=int, default=-1)
    parser.add_argument("--ga", type=int, default=-1)
    opt = parser.parse_args()

    if opt.dataset == 'iscx-vpn':
        config = ISCXVPNConfig()
    elif opt.dataset == 'iscx-nonvpn':
        config = ISCXNonVPNConfig()
    elif opt.dataset == 'iscx-tor':
        config = ISCXTorConfig()
    elif opt.dataset == 'iscx-nontor':
        config = ISCXNonTorConfig()
    elif opt.dataset == 'ciciot':
        config = CICIoTConfig()
    else:
        raise Exception('Dataset Error')

    device = get_device(index=0)
    devices = get_all_device()
    num_workers = config.NUM_WORKERS
    set_seed()
    train()
    
