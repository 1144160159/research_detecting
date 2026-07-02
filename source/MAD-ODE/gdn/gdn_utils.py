from scipy.stats import rankdata, iqr, trim_mean
from sklearn.metrics import precision_score, recall_score, roc_auc_score, f1_score
import numpy as np

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

    #total_err_scores所有指标所有时间点的异常分数[27,1999]，total_topk_err_scores每个时间点的异常分数[1999，]
    total_topk_err_scores = np.sum(np.take_along_axis(total_err_scores, topk_indices, axis=0), axis=0)

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

def get_err_mean_and_std(predicted, groundtruth):

    np_arr = np.subtract(np.array(predicted), np.array(groundtruth))

    err_mean = np.mean(np_arr)
    err_std = np.std(np_arr)

    return err_mean, err_std