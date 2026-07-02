# -*- coding: utf-8 -*-
from sklearn.metrics import precision_recall_fscore_support
def cal_f1_score(precision, recall):
    return 2 * precision * recall / (precision + recall) if (precision + recall) != 0 else 0.0

# In[] PW metrics
def evaluate_PW(y_true, y_pred):
    precision, recall, f1_score, support = precision_recall_fscore_support(
        y_true, y_pred, average='binary')
    return precision, recall, f1_score

# In[] OIPR metrics
from OIPR import OIPR
def evaluate_OIPR(y_true, y_pred, **args):
    evaluator = OIPR(**args) 
    evaluator.load_gt_events(y_true)
    evaluator.load_pred_events(y_pred)
    evaluator.run()     
    precision = evaluator.get_precision()
    recall = evaluator.get_recall()
    f1_score = cal_f1_score(precision, recall)
    return precision, recall, f1_score