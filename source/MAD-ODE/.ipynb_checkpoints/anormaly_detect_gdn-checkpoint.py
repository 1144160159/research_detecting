import numpy as np
from scipy.stats import rankdata, iqr, trim_mean
from sklearn.metrics import precision_score, recall_score, roc_auc_score, f1_score
import pandas as pd

# calculate F1 scores
def eval_scores(scores, true_scores, th_steps, return_thresold=False):      #true_scores是gt_labels
    padding_list = [0]*(len(true_scores) - len(scores))
    # print(padding_list)

    if len(padding_list) > 0:
        scores = padding_list + scores

    scores_sorted = rankdata(scores, method='ordinal')
    th_steps = th_steps
    # th_steps = 500
    th_vals = np.array(range(th_steps)) * 1.0 / th_steps
    fmeas = [None] * th_steps
    thresholds = [None] * th_steps
    for i in range(th_steps):
        cur_pred = scores_sorted > th_vals[i] * len(scores)

        fmeas[i] = f1_score(true_scores, cur_pred)
        a = int(th_vals[i] * len(scores)+1)
        score_index = scores_sorted.tolist().index(int(th_vals[i] * len(scores)+1))
        thresholds[i] = scores[score_index]

    if return_thresold:
        return fmeas, thresholds
    return fmeas

def get_best_performance_data(total_err_scores, gt_labels, topk=1):

    total_features = total_err_scores.shape[0]

    # topk_indices = np.argpartition(total_err_scores, range(total_features-1-topk, total_features-1), axis=0)[-topk-1:-1]
    topk_indices = np.argpartition(total_err_scores, range(total_features-topk-1, total_features), axis=0)[-topk:]

    total_topk_err_scores = []
    topk_err_score_map=[]

    a = np.take_along_axis(total_err_scores, topk_indices, axis=0)
    #total_err_scores所有指标所有时间点的异常分数[27,1999]，total_topk_err_scores每个时间点的异常分数[1999，]
    total_topk_err_scores = np.sum(a, axis=0)

    final_topk_fmeas ,thresolds = eval_scores(total_topk_err_scores, gt_labels, 400, return_thresold=True)

    th_i = final_topk_fmeas.index(max(final_topk_fmeas))
    thresold = thresolds[th_i]

    pred_labels = np.zeros(len(total_topk_err_scores))
    pred_labels[total_topk_err_scores > thresold] = 1

    for i in range(len(pred_labels)):
        pred_labels[i] = int(pred_labels[i])
        gt_labels[i] = int(gt_labels[i])

    pre = precision_score(gt_labels, pred_labels)
    rec = recall_score(gt_labels, pred_labels)

    f1 = f1_score(gt_labels, pred_labels)
    print("f1:", f1)
    print('#####################')

    auc_score = roc_auc_score(gt_labels, total_topk_err_scores)

    return max(final_topk_fmeas), pre, rec, auc_score, thresold

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


dataset = 'WADI'        #SWaT/WADI

label_data = np.load('./results/{}/test_labels.npy'.format(dataset))   # 44992   GTS取单步出来的这个形状，GTA取单步会多一维
pred_data = np.load('./results/{}/test_preds.npy'.format(dataset)) # (44992, 51)
true_data = np.load('./results/{}/test_trues.npy'.format(dataset)) # (44992, 51)

true_data = true_data.reshape(-1,true_data.shape[-1])   # (1077504, 51)
pred_data = pred_data.reshape(-1,pred_data.shape[-1])
label_data = label_data.reshape(-1).tolist()

scores = get_err_scores(true_data, pred_data)  # 异常分数 <class 'tuple'>: (51, 1077504)

top1_best_info = get_best_performance_data(scores, label_data, topk=1)

print('=========================** Result **============================\n')

info = top1_best_info

print(f'F1 score: {info[0]}')
print(f'precision: {info[1]}')
print(f'recall: {info[2]}\n')



