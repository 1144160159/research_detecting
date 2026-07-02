from src.pot import *
from scipy.stats import iqr
from pprint import pprint

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


dataset = args.dataset

test_label_data = np.load('./results/{}/test_labels.npy'.format(dataset))   # (1472, 24)
test_pred_data = np.load('./results/{}/test_preds.npy'.format(dataset)) # (1472, 24, 27)
test_true_data = np.load('./results/{}/test_trues.npy'.format(dataset)) # (1472, 24, 27)

train_pred_data = np.load('./results/{}/train_preds.npy'.format(dataset)) # (44896, 24, 51)
train_true_data = np.load('./results/{}/train_trues.npy'.format(dataset)) # (44896, 24, 51)

train_scores = get_err_scores(train_true_data, train_pred_data)     #<class 'tuple'>: (27, 35328)
test_score = get_err_scores(test_true_data,test_pred_data)      #<class 'tuple'>: (27, 46848)

lossTfinal, lossFinal = np.mean(train_scores, axis=0), np.mean(test_score, axis=0)
labelsFinal = test_label_data

result, _ = pot_eval(lossTfinal, lossFinal, labelsFinal)

pprint(result)