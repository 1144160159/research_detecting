import copy
from model11 import MultiModalClassifier,InterNet,ByteCNN
from SelfDataset import GraphFlowDataset
import torch
from torch_geometric.data import Data
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
import torch.nn.functional as F
from utils import AverageMeter, accuracy
import time
import os
from sklearn.metrics import classification_report, confusion_matrix
import argparse
from datetime import datetime
from collections import Counter
import random
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from plt_cm import draw_confusion_matrix

def get_k_fold_data(k, i, X):
    assert k > 1
    fold_size = len(X) // k

    X_train = None
    for j in range(k):
        X_part = X[j * fold_size: (j + 1) * fold_size]
        if j == i:
            X_valid = X_part
        elif X_train is None:
            X_train = X_part
        else:
            X_train = X_train + X_part
    return X_train, X_valid

def train(train_loader, val_loader, k,model, optimizer,epochs,save_dir,suffix="",m=8):
    best_acc = 0
    counter = 0
    batch_time = AverageMeter()
    losses = AverageMeter()
    losses_intra = AverageMeter()
    losses_inter = AverageMeter()
    losses_fusion = AverageMeter()
    end = time.time()

    model.train()
    for epoch in range(epochs):
        p_bar = tqdm(range(len(train_loader)))
        for intra_batch, inter_batch, label_batch in train_loader:
            # import pdb;pdb.set_trace()
            # 数据转移到GPU
            intra_batch = intra_batch.to(device)
            inter_batch = inter_batch.to(device)
            label_batch = label_batch.to(device)

            expanded_labels = label_batch.repeat_interleave(m)

            # 前向传播
            fusion, intra, inter = model(intra_batch, inter_batch,m)
            # import pdb; pdb.set_trace()

            loss_intra = F.cross_entropy(intra, expanded_labels)
            loss_inter = F.cross_entropy(inter, expanded_labels)
            loss_fusion = F.cross_entropy(fusion, expanded_labels)
            #total loss
            loss = loss_intra + loss_inter + loss_fusion

            # loss = loss_intra
            loss.backward()
            losses.update(loss.item())
            losses_intra.update(loss_intra.item())
            losses_inter.update(loss_inter.item())
            losses_fusion.update(loss_fusion.item())
            optimizer.step()

            model.zero_grad()

            batch_time.update(time.time() - end)
            end = time.time()

            p_bar.set_description("Train Epoch:{epoch}/{epochs:3}. Batch:{bt:.3f}s. Loss:{loss:.4f}. Loss_intra:{loss_intra:.4f}. Loss_inter:{loss_inter:.4f}. Loss_fu:{loss_fusion:.4f}. ".format(
                epoch=epoch + 1,
                epochs=epochs,
                bt=batch_time.avg,
                loss=losses.avg,
                loss_intra=losses_intra.avg,
                loss_inter=losses_inter.avg,
                loss_fusion=losses_fusion.avg,
            ))
            p_bar.update()

        p_bar.close()

        ### val
        test_loss, test_acc = test(val_loader, model,m=m,model_mode=0)

        is_best = test_acc > best_acc
        if is_best:
            counter = 0
            best_acc = test_acc
            best_model = copy.deepcopy(model)
            print(f"save best model at {k}th-folds--{epoch} epoch, acc is {best_acc}")
        else:
            counter += 1
            if counter > 50:
                print('EarlyStopping!!!   Saving Best_acc is {}'.format(best_acc))
                # return best_acc
                break
        print()

    file_path = os.path.join(save_dir, f"best_model_{k}-fold_ep{epochs}_acc{best_acc:.2f}{suffix}.pth")
    torch.save(best_model.state_dict(), file_path)
    return file_path

def train_intra(train_loader, val_loader, k,model, optimizer,epochs,save_dir,suffix="",m=8):
    best_acc = 0
    counter = 0
    batch_time = AverageMeter()
    losses = AverageMeter()
    end = time.time()

    model.train()
    for epoch in range(epochs):
        p_bar = tqdm(range(len(train_loader)))
        for intra_batch, inter_batch, label_batch in train_loader:
            # import pdb;pdb.set_trace()
            # 数据转移到GPU
            intra_batch = intra_batch.to(device)
            label_batch = label_batch.to(device)

            expanded_labels = label_batch.repeat_interleave(m)

            # 前向传播
            intra,_ = model(intra_batch)

            loss = F.cross_entropy(intra, expanded_labels)
            loss.backward()
            losses.update(loss.item())
            optimizer.step()

            model.zero_grad()

            batch_time.update(time.time() - end)
            end = time.time()

            p_bar.set_description("Train Epoch:{epoch}/{epochs:3}. Batch:{bt:.3f}s. Loss:{loss:.4f}. ".format(
                epoch=epoch + 1,
                epochs=epochs,
                bt=batch_time.avg,
                loss=losses.avg,
            ))
            p_bar.update()

        p_bar.close()

        ### val
        test_loss, test_acc = test(val_loader, model,m=m,model_mode=1)

        is_best = test_acc > best_acc
        if is_best:
            counter = 0
            best_acc = test_acc
            best_model = copy.deepcopy(model)
            print(f"save best model at {k}th-folds--{epoch} epoch, acc is {best_acc}")
        else:
            counter += 1
            if counter > 30:
                print('EarlyStopping!!!   Saving Best_acc is {}'.format(best_acc))
                # return best_acc
                break
        print()

    file_path = os.path.join(save_dir, f"best_model_{k}-fold_ep{epochs}_acc{best_acc:.2f}{suffix}.pth")
    torch.save(best_model.state_dict(), file_path)
    return file_path


def train_inter(train_loader, val_loader, k,model, optimizer,epochs,save_dir,suffix="",m=8):
    best_acc = 0
    counter = 0
    batch_time = AverageMeter()
    losses = AverageMeter()
    end = time.time()

    model.train()
    for epoch in range(epochs):
        p_bar = tqdm(range(len(train_loader)))
        for intra_batch, inter_batch, label_batch in train_loader:
            # import pdb;pdb.set_trace()
            # 数据转移到GPU
            inter_batch = inter_batch.to(device)
            label_batch = label_batch.to(device)

            expanded_labels = label_batch.repeat_interleave(m)

            # 前向传播
            inter,_ = model(inter_batch,m)

            loss = F.cross_entropy(inter, expanded_labels)
            loss.backward()
            losses.update(loss.item())
            optimizer.step()
            model.zero_grad()
            batch_time.update(time.time() - end)
            end = time.time()
            p_bar.set_description("Train Epoch:{epoch}/{epochs:3}. Batch:{bt:.3f}s. Loss:{loss:.4f}. ".format(
                epoch=epoch + 1,
                epochs=epochs,
                bt=batch_time.avg,
                loss=losses.avg,
            ))
            p_bar.update()

        p_bar.close()

        ### val
        test_loss, test_acc = test(val_loader, model,m=m,model_mode=2)

        is_best = test_acc > best_acc
        if is_best:
            counter = 0
            best_acc = test_acc
            best_model = copy.deepcopy(model)
            print(f"save best model at {k}th-folds--{epoch} epoch, acc is {best_acc}")
        else:
            counter += 1
            if counter > 30:
                print('EarlyStopping!!!   Saving Best_acc is {}'.format(best_acc))
                # return best_acc
                break
        print()

    file_path = os.path.join(save_dir, f"best_model_{k}-fold_ep{epochs}_acc{best_acc:.2f}{suffix}.pth")
    torch.save(best_model.state_dict(), file_path)
    return file_path


def test(test_loader, model,is_val=True,m=8,model_mode=0):
    batch_time = AverageMeter()
    losses = AverageMeter()
    top1 = AverageMeter()
    end = time.time()
    y_true = []
    y_pred = []
    test_loader = tqdm(test_loader)

    with torch.no_grad():
        for batch_idx, (intra_batch, inter_batch, label_batch) in enumerate(test_loader):
            # 数据转移到GPU
            intra_batch = intra_batch.to(device)
            inter_batch = inter_batch.to(device)
            label_batch = label_batch.to(device)

            expanded_labels = label_batch.repeat_interleave(m)
            y_true.append(expanded_labels.cpu().numpy())

            model.eval()

            # 前向传播
            if model_mode==0:
                fusion, intra, inter = model(intra_batch, inter_batch,m)
                y_pred.append(fusion.cpu().numpy())

                loss = F.cross_entropy(fusion, expanded_labels)
                acc1 = accuracy(fusion, expanded_labels)
            elif model_mode==1:
                intra,_ = model(intra_batch)
                y_pred.append(intra.cpu().numpy())
                loss = F.cross_entropy(intra, expanded_labels)
                acc1 = accuracy(intra, expanded_labels)
            else:
                inter,_ = model(inter_batch,m)
                y_pred.append(inter.cpu().numpy())
                loss = F.cross_entropy(inter, expanded_labels)
                acc1 = accuracy(inter, expanded_labels)
            # prec1,_ = accuracy(fusion, expanded_labels, topk=(1,5))
            # import pdb;pdb.set_trace()
            losses.update(loss.item(), expanded_labels.shape[0])
            top1.update(acc1, expanded_labels.shape[0])

            batch_time.update(time.time() - end)
            end = time.time()

            test_loader.set_description("Test Iter: {batch:4}/{iter:4}. Batch: {bt:.3f}s. Loss: {loss:.4f}. acc: {top1:.2f}. ".format(
                batch=batch_idx + 1,
                iter=len(test_loader),
                bt=batch_time.avg,
                loss=losses.avg,
                top1=top1.avg,
            ))
        test_loader.close()
    if is_val:
        return losses.avg, top1.avg
    else:
        y_true = np.concatenate(y_true)
        y_pred = np.concatenate(y_pred)
        return y_true, y_pred


def plt_cm(y_true,y_pred,classes,save_path):
    # 计算混淆矩阵
    cm = confusion_matrix(y_true, y_pred)

    # 绘制混淆矩阵
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    # 在矩阵单元格中显示数值
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"混淆矩阵已保存至 {save_path}")
    # plt.show()


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type=int, default=128,
                    help='batch size')
parser.add_argument('--k_folds', type=int, default=5,
                    help='k folds')
parser.add_argument('--lr', type=float, default=0.0005,
                    help='learning rate')
parser.add_argument('--intra_hid', type=int, default=1024, ##128
                    help='intra hidden size')
parser.add_argument('--inter_hid', type=int, default=128, ##128
                    help='inter hidden size')
parser.add_argument('--epochs', type=int, default=100,
                    help='maximum number of epochs')
parser.add_argument('--num_classes', type=int, default=13,
                    help='number of classes')
parser.add_argument('--m', type=int, default=12,
                    help='number of flows in one graph')
parser.add_argument('--len_seq', type=int, default=26,
                    help='pkt length sequence')
parser.add_argument('--model_mode', type=int, default=0,
                    help='0:MutilClassifier 1:IntraClassifier 2:InterClassifier')
parser.add_argument('--cuda', default='0', type=int, help='GPU number')
args = parser.parse_args()


device = torch.device(f'cuda:{args.cuda}' if torch.cuda.is_available() else 'cpu')
# 加载数据
train_data = torch.load(f'./dataset/MQTT/processed_data/train_samples_m{args.m}_300bytes_threshold-200ms.pt')
test_data = torch.load(f'./dataset/MQTT/processed_data/test_samples_m{args.m}_300bytes_threshold-200ms.pt')

### 统计各类别数量
train_label = Counter(sample['label'] for sample in train_data)
test_label = Counter(sample['label'] for sample in test_data)
print('train label count:',train_label)
print('test label count:',test_label)
# import pdb;pdb.set_trace()
random.seed(42)
random.shuffle(train_data)

save_model_dir = "./save_model/MQTT"
os.makedirs(save_model_dir, exist_ok=True)

# import pdb;pdb.set_trace()
# 创建或打开结果文件
# 生成带时间戳的结果文件名
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = f"{save_model_dir}/model{args.model_mode}_m{args.m}_bs{args.batch_size}_lr{args.lr}_cross_validation_report_{timestamp}.txt"
with open(results_file, "w") as f:
    f.write(f"{'='*40}\n")
    f.write(f"K-Fold Cross Validation Results ({args.k_folds} folds)\n")
    f.write(f"{'='*40}\n\n")

### k-fold交叉验证
for k in range(1,args.k_folds+1):
    print(f"\n{'=' * 20} 第 {k }/{args.k_folds} 折 {'=' * 20}")
    train_, val_ = get_k_fold_data(args.k_folds, k-1, train_data)

    train_label_ = Counter(sample['label'] for sample in train_)
    val_label_ = Counter(sample['label'] for sample in val_)
    # import pdb;pdb.set_trace()

    print(f"train samples label count: {train_label_}")  # 输出样本数
    print(f"val samples label count: {val_label_}")

    # 创建数据加载器
    train_dataset = GraphFlowDataset(train_)
    val_dataset = GraphFlowDataset(val_)

    train_dataloader = DataLoader(train_dataset,batch_size=args.batch_size,shuffle=True,collate_fn=train_dataset.collate_fn)
    val_dataloader = DataLoader(val_dataset,batch_size=args.batch_size,shuffle=False,collate_fn=test_dataset.collate_fn)

    if args.model_mode ==0:
        model = MultiModalClassifier(num_classes=args.num_classes, len_seq=args.len_seq,intra_hid=args.intra_hid,inter_hid=args.inter_hid).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
        best_model_path = train(train_dataloader, val_dataloader, k, model, optimizer, args.epochs, save_model_dir,
                        f"_{args.num_classes}class_m{args.m}_bs{args.batch_size}_lr{args.lr}_model{args.model_mode}",args.m)
    elif args.model_mode ==1:
        model = ByteCNN(num_classes=args.num_classes,hidden_dim=args.intra_hid).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
        best_model_path = train_intra(train_dataloader, val_dataloader, k, model, optimizer, args.epochs, save_model_dir,
                                f"_{args.num_classes}class_m{args.m}_bs{args.batch_size}_lr{args.lr}_model{args.model_mode}",args.m)
    else:
        model = InterNet(num_classes=args.num_classes,num_features=args.len_seq,nhid=args.inter_hid).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
        best_model_path = train_inter(train_dataloader,val_dataloader,k,model,optimizer,args.epochs,save_model_dir,
                                f"_{args.num_classes}class_m{args.m}_bs{args.batch_size}_lr{args.lr}_model{args.model_mode}",args.m)
    # import pdb;pdb.set_trace()
    ###load model,test
    model.load_state_dict(torch.load(best_model_path))
    model.eval()
    y_true, y_pred = test(test_dataloader, model,is_val=False,m=args.m,model_mode=args.model_mode)
    y_pred = np.argmax(y_pred, axis=1)
    # import pdb;pdb.set_trace()
    report = classification_report(y_true,y_pred, digits=4)
    print( report)
    # 追加写入到结果文件
    with open(results_file, "a") as f:
        f.write(f"{'=' * 20} Fold {k}/{args.k_folds} {'=' * 20}\n")
        f.write(f"训练样本数: {len(train_)}\n")
        f.write(f"验证样本数: {len(val_)}\n")
        f.write(f"模型路径: {best_model_path}\n\n")
        f.write(f"{report}\n\n")

