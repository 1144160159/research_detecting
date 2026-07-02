import numpy as np
from err_scores import *
from src1.pot import *
from jump.metrics import  evaluation
from pprint import pprint
import sys
import time
from eval_methods import *
import warnings
warnings.filterwarnings("ignore")

def moving_average(matrix, alpha):
    """
    对二维矩阵的每一列进行滑动平均
    :param matrix: 二维矩阵，每一列为一个时间序列
    :param alpha: 平均因子，0<alpha<1
    :return: 平滑后的矩阵
    """
    m, n = matrix.shape
    matrix_avg = np.zeros((m, n))
    matrix_avg[:, 0] = matrix[:, 0]
    for i in range(1, n):
        matrix_avg[:, i] = alpha * matrix[:, i] + (1 - alpha) * matrix_avg[:, i-1]
    return matrix_avg
import numpy as np

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")
        #可以选择"w"
        self.log = open(filename, "a", encoding="utf-8")  # 防止编码错误
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass
    def reset(self):
        self.log.close()
        sys.stdout=self.terminal

def gdn_max(scores):
    total_features = scores.shape[0]

    # topk_indices = np.argpartition(total_err_scores, range(total_features-1-topk, total_features-1), axis=0)[-topk-1:-1]
    topk_indices = np.argpartition(scores, range(total_features-2, total_features), axis=0)[-1:]

    total_topk_err_scores = []
    topk_err_score_map=[]

    a = np.take_along_axis(scores, topk_indices, axis=0)
    #total_err_scores所有指标所有时间点的异常分数[27,1999]，total_topk_err_scores每个时间点的异常分数[1999，]
    total_topk_err_scores = np.sum(a, axis=0)
    
    return total_topk_err_scores

def mai(dataset='wadi'):
    sys.stdout = Logger('{}.log'.format(time.strftime('%m%d_%H:%M')))
    dataset = dataset   # swat/wadi/smap/msl
    model = 'GTS'      # GTS/GTA
    # print("更换数据后，GTA构图")
    print('dataset:{},model:{}'.format(dataset,model))
    test_label_data = np.load('./results/{}/test_labels.npy'.format(dataset))  # 44992   GTS取单步出来的这个形状，GTA取单步会多一维
    test_pred_data = np.load('./results/{}/test_preds.npy'.format(dataset))  # (44992, 51)
    test_true_data = np.load('./results/{}/test_trues.npy'.format(dataset))  # (44992, 51)

    train_pred_data = np.load('./results/{}/train_preds.npy'.format(dataset))
    train_true_data = np.load('./results/{}/train_trues.npy'.format(dataset))
    label_data = test_label_data.reshape(-1)

    if model == 'GTA':
        test_pred_data = test_pred_data.reshape(-1, test_pred_data.shape[-1])  # (1077504, 51)
        test_true_data = test_true_data.reshape(-1, test_true_data.shape[-1])
        train_pred_data = train_pred_data.reshape(-1, train_pred_data.shape[-1])  # (1077504, 51)
        train_true_data = train_true_data.reshape(-1, train_true_data.shape[-1])


    normal_scores_test = get_normal_scores(test_true_data,test_pred_data)    #(123, 17280)
    normal_scores_test = moving_average(normal_scores_test, 0.9)
    normal_scores_train = get_normal_scores(train_true_data, train_pred_data)   #(123, 17280)
    gdn_scores_test = get_gdn_scores(test_true_data,test_pred_data)     #(123, 172s80)
    gdn_scores_train = get_gdn_scores(train_true_data, train_pred_data)     #(123, 17280)
    gta_scores_test = get_gta_scores(test_true_data,test_pred_data)     #(123, 17280)
    gta_scores_train = get_gta_scores(train_true_data, train_pred_data)     #(123, 17280)
    jump_scores_test = get_jump_scores(test_true_data,test_pred_data)       #(17280)
    jump_scores_train = get_jump_scores(train_true_data, train_pred_data)       #(17280)

    # print('normal+POT'.center(100,'-'))
    # lossTfinal, lossFinal = gdn_max(normal_scores_train), gdn_max(normal_scores_test)
    # labelsFinal = label_data
    # result, _ = pot_eval(lossTfinal, lossFinal, labelsFinal)
    # pprint(result)

    print('normal+Gridsearch'.center(100, '-'))
    normal_Gridsearch = gdn_max(normal_scores_test)
    precision, recall, f1score, best_thr, roc_auc, ap, pr_auc = evaluation(label_data,normal_Gridsearch )
    # _ , _ ,f1score, precision,recall, _,_ = get_adjusted_composite_metrics(normal_Gridsearch, label_data)
    print('Precision: ', precision)
    print('Recall: ', recall)
    print('F1_score: ', f1score)
    print('roc_auc: ', roc_auc)
    print('pr_auc: ', pr_auc)

#     print('gdn+POT'.center(100,'-'))
#     lossTfinal, lossFinal = gdn_max(gdn_scores_train), gdn_max(gdn_scores_test)
#     labelsFinal = label_data
#     result, _ = pot_eval(lossTfinal, lossFinal, labelsFinal)
#     pprint(result)

#     print('gdn+Gridsearch'.center(100, '-'))
#     gdn_Gridsearch = gdn_max(gdn_scores_test)
#     precision, recall, f1score, _ = evaluation(label_data, gdn_Gridsearch)
#     print('Precision: ', precision)
#     print('Recall: ', recall)
#     print('F1_score: ', f1score)

#     print('gta+POT'.center(100,'-'))
#     lossTfinal, lossFinal = np.sum(gta_scores_train, axis=0), np.sum(gta_scores_test, axis=0)
#     labelsFinal = label_data
#     result, _ = pot_eval(lossTfinal, lossFinal, labelsFinal)
#     pprint(result)

#     print('gta+Gridsearch'.center(100, '-'))
#     gta_Gridsearch = np.sum(gta_scores_test,axis=0)
#     precision, recall, f1score, _ = evaluation(label_data, gta_Gridsearch)
#     print('Precision: ', precision)
#     print('Recall: ', recall)
#     print('F1_score: ', f1score)

#     print('jump+POT'.center(100,'-'))
#     lossTfinal = jump_scores_train
#     lossFinal = jump_scores_test
#     labelsFinal = label_data
#     result, _ = pot_eval(lossTfinal, lossFinal, labelsFinal)
#     pprint(result)

    print('jump+Gridsearch'.center(100, '-'))
    jump_Gridsearch = jump_scores_test
    precision, recall, f1score, _ = evaluation(label_data, jump_Gridsearch)
    print('Precision: ', precision)
    print('Recall: ', recall)
    print('F1_score: ', f1score)


if __name__ == '__main__':
    mai()