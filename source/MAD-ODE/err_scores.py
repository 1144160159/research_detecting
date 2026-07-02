import numpy as np
import pandas as pd
from gdn.gdn_utils import *

def moving_average(x, alpha):
    """
    对一维数组进行滑动平均
    :param x: 一维数组
    :param alpha: 平均因子，0<alpha<1
    :return: 平滑后的数组
    """
    n = len(x)
    avg = np.zeros(n)
    avg[0] = x[0]
    for i in range(1, n):
        avg[i] = alpha * x[i] + (1 - alpha) * avg[i-1]
    return avg

def get_normal_scores(gt,pre):
    feature_num = gt.shape[-1]

    all_scores =  None
    all_normals = None

    for i in range(feature_num):
        true_re_list = gt[:,i]
        pred_re_list = pre[:,i]   #(1077504)

        n_err_mean, n_err_std = get_err_mean_and_std(pred_re_list, true_re_list)

        test_delta = np.subtract(
            pred_re_list.astype(np.float64),
            true_re_list.astype(np.float64)
        )
        epsilon = 1e-6
        test_delta = np.abs(test_delta)
        # test_delta = moving_average(test_delta, 0.9)
        err_scores = (test_delta - n_err_mean) / (np.abs(n_err_std) + epsilon)

        if all_scores is None:
            all_scores = err_scores
        else:
            all_scores = np.vstack((   #所有指标所有时间点的异常分数
                all_scores,
                err_scores
            ))
    return all_scores

def get_gdn_scores(gt,pre):
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
        test_delta = np.abs(test_delta)

        err_scores = (test_delta - n_err_mid) / (np.abs(n_err_iqr) + epsilon)

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

def get_gta_scores(gt,pre):
    feature_num = gt.shape[-1]

    all_scores =  None
    all_normals = None

    for i in range(feature_num):
        true_re_list = gt[:,i]
        pred_re_list = pre[:,i]   #(1077504)

        test_delta = np.subtract(
            pred_re_list.astype(np.float64),
            true_re_list.astype(np.float64)
        )

        err_scores = test_delta ** 2
        if all_scores is None:
            all_scores = err_scores
        else:
            all_scores = np.vstack((   #所有指标所有时间点的异常分数
                all_scores,
                err_scores
            ))
    return all_scores

def anomaly_score_example(source, reconstructed):
    """
    Calculate anomaly score
    :param source: original data
    :param reconstructed: reconstructed data
    :return:
    """
    n, d = source.shape
    d_dis = np.zeros((d,))
    for i in range(d):
        dis = np.abs(source[:, i] - reconstructed[:, i])
        dis = dis - np.mean(dis)
        d_dis[i] = np.percentile(dis, 90)
    if d <= 2:
        return d / np.sum(1 / d_dis)
    topn = 1 / d_dis[np.argsort(d_dis)][-1 * 2:]
    return 2 / np.sum(topn)

def get_jump_scores(gt,pre,window =12 ,stride =2 ):
    if pre.shape != gt.shape:
        raise Exception('shape mismatches')
    n, d = gt.shape
    # 异常得分
    anomaly_score = np.zeros((n,))
    # 表示当时某个位置上被已重建窗口的数量
    anomaly_score_weight = np.zeros((n,))
    # 窗口左端点索引
    wb = 0
    while True:
        we = min(n, wb + window)
        # 窗口右端点索引 窗口数据[wb, we)
        score = anomaly_score_example(gt[wb:we], pre[wb:we])
        for i in range(we - wb):
            w = i + wb
            weight = anomaly_score_weight[w]
            anomaly_score[w] = \
                (anomaly_score[w] * weight + score) / (weight + 1)
        anomaly_score_weight[wb:we] += 1
        if we >= n:
            break
        wb += stride
    return anomaly_score