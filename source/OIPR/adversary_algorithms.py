# -*- coding: utf-8 -*-
import random
import numpy as np

def first_point_detector(gt, fpr=0, **args):
    pred = np.zeros(len(gt))
    is_anomaly = False
    for i in range(len(gt)):
        if gt[i] == 1:
            if is_anomaly == False:
                is_anomaly = True
                pred[i] = 1
            else:
                pass
        else:
            is_anomaly = False
    pred_random = random_detector(gt, fpr)
    pred = pred + (1 - gt) * pred_random
    return pred

def ts2events(x):
    events = []
    anomaly_state = False
    for i in range(len(x)):
        if x[i] == 1:
            if anomaly_state == False:
                anomaly_state = True
                start_idx = i
        elif x[i] == 0:
            if anomaly_state == True:
                anomaly_state = False
                end_idx = i
                events.append((start_idx, end_idx))
    if anomaly_state == True:
        anomaly_state = False
        end_idx = len(x)
        events.append((start_idx, end_idx))
    return events

def long_anomaly_detector(gt, L=10, fpr=0, **args):
    events_gt = ts2events(gt)    
    pred = np.zeros(len(gt))
    for e in events_gt:
        if e[1] - e[0] >= L:
            pred[e[0]: e[1]] = 1
    pred_random = random_detector(gt, fpr)
    pred = pred + (1 - gt) * pred_random    
    return pred

def random_detector(gt, anomaly_ratio, seed=3, **args):
    np.random.seed(seed)    
    pred = np.random.rand(gt.size)
    pred[pred > 1 - anomaly_ratio] = 1
    pred[pred <= 1 - anomaly_ratio] = 0
    return pred

def dispersive_disturbance_detector(gt, dis_rate=0.005, seed=3, **args):
    random.seed(seed)
    N = len(gt)
    pred = np.zeros(N)
    pred[gt==1] = 1
    for i in range( int(N * dis_rate) ):
        zero_idxs = np.where(pred==0)[0]
        idx = random.randint(0, len(zero_idxs) - 1)
        pred[zero_idxs[idx]] = 1
    return pred

def aggregation_disturbance_detector(gt, dis_rate=0.005, aggr_rate=0.05, seed=3, **args):  
    random.seed(seed)
    assert dis_rate < aggr_rate
    N = len(gt)
    pred = np.zeros(N)
    pred[gt==1] = 1
    n = int(N * aggr_rate)
    start_segment = pred[: n]
    for i in range( int(N * dis_rate) ):
        zero_idxs = np.where(start_segment==0)[0]
        idx = random.randint(0, len(zero_idxs) - 1)
        start_segment[zero_idxs[idx]] = 1
    pred[: n] = start_segment
    return pred    
    
def continuous_disturbance_detector(gt, aggr_rate=0.05, seed=3, **args):  
    N = len(gt)
    pred = np.zeros(N)
    pred[gt==1] = 1
    n = int(N * aggr_rate)
    i = n
    while n - sum(pred[:i]) > n:
        print(n - sum(pred[:i]))
        i += 1
    pred[: i] = 1
    return pred    

def all_1_detector(gt):
    pred = np.ones(len(gt))
    return pred
    
def all_0_detector(gt):
    pred = np.zeros(len(gt))
    return pred
    
    
    
    
    
    