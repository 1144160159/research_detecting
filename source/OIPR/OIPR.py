import math
import numpy as np

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

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def omega_func(i, l_dis=10, b_dur=0.8):
    if i == 0:
        return 1
    if l_dis == 0:
        return b_dur
    return b_dur +  (1 - b_dur) * (1 - sigmoid(i * 10 / l_dis - 5)) / (1 - sigmoid(-5))

def gamma_func(i, l_obs=20):
    if i == 0:
        return 1
    if l_obs == 0:
        return 0
    return (1 - sigmoid(i * 10 / l_obs - 5)) / (1 - sigmoid(-5))

def online_opt_inter(ts, l_dis, l_obs, b_dur):
    T = len(ts)
    interest = np.zeros(T + l_obs)
    idx_start = - l_obs - 1
    idx_end = - l_obs - 1
    for i in range(T):
        if ts[i] == 1:
            if i - idx_end > l_obs:
                idx_start = i
            interest[i] = omega_func(i - idx_start, l_dis, b_dur)
            idx_end = i
        else:
            if i - idx_end <= l_obs:
                interest[i] = omega_func(i - idx_start, l_dis, b_dur) * gamma_func(i - idx_end, l_obs) 
    for i in range(T, T + l_obs):
        if i - idx_end <= l_obs:
            interest[i] = omega_func(i - idx_start, l_dis, b_dur) * gamma_func(i - idx_end, l_obs)        
    return interest
            
class OIPR():
    def __init__(self, l_dis=0, l_obs=2, b_dur=1, omega_func=omega_func, gamma_func=gamma_func, **args):
        self.l_dis = l_dis
        self.l_obs = l_obs
        self.b_dur = b_dur
        self.omega_func = omega_func
        self.gamma_func = gamma_func
    
    def load_gt_events(self, gt):
        self.gt = np.array(gt)
        self.R_set = ts2events(gt)
        if sum(self.gt) == 0:
            return
        avg_len = sum(gt) / len(self.R_set)
        if self.l_obs == 'auto':
            self.l_obs = math.ceil(avg_len)
        if self.l_dis == 'auto':
            self.l_dis = math.ceil(avg_len / 4)
        return
    
    def load_pred_events(self, pred):
        self.pred = pred
        return
    
    def get_inter_pred(self):
        self.inter_pred = online_opt_inter(self.pred, self.l_dis, self.l_obs, self.b_dur)
        
    def get_inter_gt(self):
        self.inter_gt = online_opt_inter(self.gt, self.l_dis, self.l_obs, self.b_dur)
        
    def run(self, verbose=False):
        if sum(self.gt) == 0:
            return
        self.get_inter_pred()
        self.get_inter_gt()
        TP_area = np.minimum(self.inter_pred, self.inter_gt)
        FN_area = self.inter_gt - TP_area
        FP_area = self.inter_pred - TP_area
        self.TP_area = TP_area
        self.FN_area = FN_area
        self.FP_area = FP_area   
        
        if verbose:
            import matplotlib.pyplot as plt
            N = len(self.inter_gt)
            plt.figure(figsize=(20,15))
            plt.subplot(511)
            plt.plot(self.pred, 'r', label='$pred$')
            plt.plot(self.gt, 'g', label='$gt$')
            plt.plot(self.inter_pred, 'r--', label='$\hat{I}$')
            plt.plot(self.inter_gt, 'g--', label='$I$')
            plt.legend()
            plt.subplot(512)
            plt.title(f'TP: {sum(TP_area)}')
            plt.plot(self.inter_pred, 'r--', label='$\hat{I}$')
            plt.plot(self.inter_gt, 'g--', label='$I$')
            plt.fill_between(np.linspace(0, N-1, N), np.zeros(N), TP_area, color='b', label='TP', alpha=0.2)
            plt.legend()
            plt.subplot(513)
            plt.title(f'FP: {sum(FP_area)}')
            plt.plot(self.inter_pred, 'r--', label='$\hat{I}$')
            plt.plot(self.inter_gt, 'g--', label='$I$')
            plt.fill_between(np.linspace(0, N-1, N), TP_area, self.inter_pred, color='b', label='FP', alpha=0.2)
            plt.legend()
            plt.subplot(514)
            plt.title(f'FN: {sum(FN_area)}')
            plt.plot(self.inter_pred, 'r--', label='$\hat{I}$')
            plt.plot(self.inter_gt, 'g--', label='$I$')
            plt.fill_between(np.linspace(0, N-1, N), TP_area, self.inter_gt, color='b', label='FN', alpha=0.2)
            plt.legend()
            plt.tight_layout()
            plt.show()   

        
    def get_precision(self):
        if sum(self.gt) == 0:
            return 0.0    
        TP = sum(self.TP_area)
        FP = sum(self.FP_area)
        if TP + FP == 0:
            return 0.0
        precision = TP / (TP + FP)
        return precision

    def get_recall(self):
        if sum(self.gt) == 0:
            return 0.0
        TP = sum(self.TP_area)
        FN = sum(self.FN_area)
        if TP + FN == 0:
            return 0.0
        recall = TP / (TP + FN)
        return recall    
     
    
if __name__ == "__main__":       
    gt = np.zeros(500)
    gt[100:200] = 1
    gt[330:400] = 1
    pred = np.zeros(500)
    pred[110] = 1
    pred[250] = 1
    
    config = {'l_dis': 5, 
              'l_obs': 20, 
              'b_dur': 0.5}
        
    evaluator = OIPR(**config) 
    evaluator.load_gt_events(gt)
    evaluator.load_pred_events(pred)    
    evaluator.run(verbose=True)
    precision = evaluator.get_precision()
    recall = evaluator.get_recall()
    print(f'OIPR: pre={precision}, rec={recall}')
