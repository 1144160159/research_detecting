from scipy.stats import iqr
from pprint import pprint
from jump.metrics import  evaluation
import numpy as np

def get_err_median_and_iqr(predicted, groundtruth):

    np_arr = np.subtract(np.array(predicted), np.array(groundtruth))

    err_median = np.median(np_arr)
    err_iqr = iqr(np_arr)

    return err_median, err_iqr

def get_err_scores(gt,pre):
    feature_num = gt.shape[-1]

    all_scores =  None
    all_normals = None

    for i in range(feature_num):
        true_re_list = gt[:,i]
        pred_re_list = pre[:,i]   #(1077504)

        n_err_mid, n_err_iqr = get_err_median_and_iqr(pred_re_list, true_re_list)

        test_delta = np.subtract(
            pred_re_list.astype(np.float64),
            true_re_list.astype(np.float64)
        )
        epsilon = 1e-2

        err_scores = (test_delta - n_err_mid) / (np.abs(n_err_iqr) + epsilon)
        err_scores = np.abs(err_scores)

        smoothed_err_scores = np.zeros(err_scores.shape)
        before_num = 3
        for i in range(before_num, len(err_scores)):
            smoothed_err_scores[i] = np.mean(err_scores[i - before_num:i + 1])

        if all_scores is None:
            all_scores = smoothed_err_scores
        else:
            all_scores = np.vstack((   #所有指标所有时间点的异常分数
                all_scores,
                smoothed_err_scores
            ))
    return all_scores

dataset = 'SWaT'        #SWaT/WADI

label_data = np.load('./results/{}/test_labels.npy'.format(dataset))   # 44992   GTS取单步出来的这个形状，GTA取单步会多一维
pred_data = np.load('./results/{}/test_preds.npy'.format(dataset)) # (44992, 51)
true_data = np.load('./results/{}/test_trues.npy'.format(dataset)) # (44992, 51)

true_data = true_data.reshape(-1,true_data.shape[-1])   # (1077504, 51)
pred_data = pred_data.reshape(-1,pred_data.shape[-1])
label_data = label_data.reshape(-1).tolist()

scores = get_err_scores(true_data, pred_data)  # 异常分数 (51, 44992)
scores = np.mean(scores,axis=0)     #(44992)

precision, recall, f1score, _ = evaluation(label_data, scores)

print('Precision: ', precision)
print('Recall: ', recall)
print('F1_score: ', f1score)