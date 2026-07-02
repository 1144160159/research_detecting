from data_provider.data_factory import data_provider
from exp.exp_basic import Exp_Basic
from models import CTT
from utils.tools import EarlyStopping, adjust_learning_rate

import numpy as np
import torch
import torch.nn as nn
from torch import optim
from torch.optim import lr_scheduler 

import os
import time

import warnings
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report
import torch.nn.functional as F
from sklearn.metrics import confusion_matrix

warnings.filterwarnings('ignore')

def focal_loss(logits, targets, alpha=1.0, gamma=2.0, smoothing=0.1):
    num_classes = logits.size(1)
    with torch.no_grad():
        true_dist = torch.zeros_like(logits)
        true_dist.fill_(smoothing / (num_classes - 1))
        true_dist.scatter_(1, targets.data.unsqueeze(1), 1.0 - smoothing)
    ce_loss = -(true_dist * F.log_softmax(logits, dim=1)).sum(dim=1)
    pt = torch.exp(-ce_loss)
    focal = alpha * (1 - pt) ** gamma * ce_loss
    return focal.mean()

class FocalLoss(nn.Module):
    def __init__(self, alpha=1.0, gamma=2.0, smoothing=0.1):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.smoothing = smoothing
    
    def forward(self, logits, targets):
        return focal_loss(logits, targets, self.alpha, self.gamma, self.smoothing)


class Exp_Main(Exp_Basic):
    def __init__(self, args):
        super(Exp_Main, self).__init__(args)

    def _build_model(self):
        model = CTT(self.args).float()

        if self.args.use_multi_gpu and self.args.use_gpu:
            model = nn.DataParallel(model, device_ids=self.args.device_ids)
        return model

    def _get_data(self, flag):
        data_set, data_loader = data_provider(self.args, flag)
        return data_set, data_loader

    def _select_optimizer(self):
        model_optim = optim.Adam(self.model.parameters(), lr=self.args.learning_rate)
        return model_optim

    def _select_criterion(self,name=None,label_smoothing=0.0):
        if self.args.mode == 'pred':
            criterion = nn.CrossEntropyLoss()
        elif self.args.mode == 'analysis':
            if name == "CE":
                criterion = nn.CrossEntropyLoss(label_smoothing=label_smoothing)
            elif name == "Focal":
                criterion = FocalLoss(alpha=0.25, gamma=2, smoothing=0.1)
        return criterion

    def vali(self, vali_data, vali_loader, criterion,test_data_flag=0,best_f1=0):
        total_loss = []
        preds = []
        trues = []
        
        self.model.eval()
        with torch.no_grad():
            for i, (batch_x, batch_y) in enumerate(vali_loader):
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.long().to(self.device)
                if self.args.mode == 'analysis':
                    batch_y = batch_y.reshape(-1)
                    outputs = self.model(batch_x)
                if self.args.mode == 'pred':
                    outputs = outputs[:, -self.args.pred_len:, :]
                    batch_y = batch_y[:, -self.args.pred_len:].to(self.device)
                    outputs = outputs.reshape(-1,outputs.shape[2])
                    batch_y = batch_y.reshape(-1)   
                pred = outputs
                true = batch_y
                loss = criterion(pred, true)
                total_loss.append(loss.item())
                
                pred = F.softmax(outputs, dim=1)
                pred = torch.argmax(pred, dim=1).detach().cpu().numpy() 
                true = batch_y.detach().cpu().numpy()
                preds.append(pred)
                trues.append(true)
            preds = np.array(preds)
            trues = np.array(trues)
            
        preds = preds.reshape(-1,)
        trues = trues.reshape(-1,)
        cm = confusion_matrix(trues, preds)
        report = classification_report(y_true=trues, y_pred=preds, digits=4,output_dict=True)
        f1_score = report['macro avg']['f1-score']
        accuracy = report['accuracy']
        precision = report['macro avg']['precision']
        recall = report['macro avg']['recall']
        print('The result of validation set:')
        print("f1_score: {}; accuracy: {} ; precision {} ; recall {} ;".format(f1_score,accuracy,precision,recall))
        total_loss = np.average(total_loss)
        self.model.train()
        return total_loss,best_f1

    def train(self, setting):
        train_data, train_loader = self._get_data(flag='train')
        vali_data, vali_loader = self._get_data(flag='val')

        path = os.path.join(self.args.checkpoints, setting) 
        if not os.path.exists(path):
            os.makedirs(path)

        time_now = time.time()

        train_steps = len(train_loader)
        early_stopping = EarlyStopping(patience=self.args.patience, verbose=True)
        model_optim = self._select_optimizer() 
        criterion = self._select_criterion(name=self.args.loss,label_smoothing=0)
            
        scheduler = lr_scheduler.OneCycleLR(optimizer = model_optim,
                                            steps_per_epoch = train_steps,
                                            pct_start = self.args.pct_start,
                                            epochs = self.args.train_epochs,
                                            max_lr = self.args.learning_rate) 
        best_f1 = 0
        for epoch in range(self.args.train_epochs):
            iter_count = 0
            train_loss = []

            self.model.train()
            epoch_time = time.time()
            for i, (batch_x, batch_y) in enumerate(train_loader):
                iter_count += 1
                model_optim.zero_grad()
                batch_x = batch_x.float().to(self.device) 
                batch_y = batch_y.long().to(self.device)
                if self.args.mode == 'analysis':
                    batch_y = batch_y.reshape(-1) 
                    outputs= self.model(batch_x)
                if self.args.mode == 'pred':
                    outputs = outputs[:, -self.args.pred_len:, :]
                    batch_y = batch_y[:, -self.args.pred_len:].to(self.device)
                    outputs = outputs.reshape(-1,outputs.shape[2])
                    batch_y = batch_y.reshape(-1)   
                loss = criterion(outputs, batch_y) 
                train_loss.append(loss.item()) 

                if (i + 1) % 100 == 0:
                    print("\titers: {0}, epoch: {1} | loss: {2:.7f}".format(i + 1, epoch + 1, loss.item()))
                    speed = (time.time() - time_now) / iter_count
                    left_time = speed * ((self.args.train_epochs - epoch) * train_steps - i)
                    print('\tspeed: {:.4f}s/iter; left time: {:.4f}s'.format(speed, left_time))
                    iter_count = 0
                    time_now = time.time()

                loss.backward()
                model_optim.step()
                
                if self.args.lradj == 'TST':
                    adjust_learning_rate(model_optim, scheduler, epoch + 1, self.args, printout=False)
                    scheduler.step()

            print("Epoch: {} cost time: {}".format(epoch + 1, time.time() - epoch_time))
            train_loss = np.average(train_loss)
            vali_loss,best_f1 = self.vali(vali_data, vali_loader, criterion,test_data_flag=0,best_f1=best_f1)
            print("Epoch: {0}, Steps: {1} | Train Loss: {2:.7f} Vali Loss: {3:.7f}".format(epoch + 1, train_steps, train_loss, vali_loss))
            early_stopping(vali_loss, self.model, path)
            if early_stopping.early_stop:
                print("Early stopping")
                break

            if self.args.lradj != 'TST':
                adjust_learning_rate(model_optim, scheduler, epoch + 1, self.args)
            else:
                print('Updating learning rate to {}'.format(scheduler.get_last_lr()[0]))

        best_model_path = path + '/' + 'checkpoint.pth'
        self.model.load_state_dict(torch.load(best_model_path))

        return self.model

    def test(self, setting, test=0):
        test_data, test_loader = self._get_data(flag='test')
        
        if test:
            print('loading model')
            self.model.load_state_dict(torch.load(os.path.join(setting, 'checkpoint.pth')))

        preds = []
        trues = []

        self.model.eval()
        with torch.no_grad():
            for i, (batch_x, batch_y) in enumerate(test_loader):
                batch_x = batch_x.float().to(self.device)
                batch_y = batch_y.long().to(self.device)
                if self.args.mode == 'analysis':
                    batch_y = batch_y.reshape(-1)
                    outputs = self.model(batch_x)
                if self.args.mode == 'pred':
                    outputs = outputs[:, -self.args.pred_len:, :]
                    outputs_for_plot = outputs[0]
                    batch_y = batch_y[:, -self.args.pred_len:].to(self.device)
                    
                    outputs = outputs.reshape(-1,outputs.shape[2])
                    true= batch_y.reshape(-1).detach().cpu().numpy()
                
                
                pred = F.softmax(outputs, dim=1)
                pred = torch.argmax(pred, dim=1).detach().cpu().numpy() 
                true = batch_y.detach().cpu().numpy()

                preds.append(pred)
                trues.append(true)

        preds = np.array(preds)
        trues = np.array(trues)
        preds = preds.reshape(-1,)
        trues = trues.reshape(-1,)
        report = classification_report(y_true=trues, y_pred=preds, digits=4,output_dict=True)
        f1_score = report['macro avg']['f1-score']
        accuracy = report['accuracy']
        precision = report['macro avg']['precision']
        recall = report['macro avg']['recall']

        print('The result of test set:')
        print("f1_score: {}; accuracy: {} ; precision {} ; recall {} ;".format(f1_score,accuracy,precision,recall))
        print(classification_report(y_true=trues, y_pred=preds, digits=4))
        return