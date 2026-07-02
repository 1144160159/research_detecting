'''Some helper functions for PyTorch, including:
    - get_mean_and_std: calculate the mean and std value of dataset.
'''
import torch

def accuracy(output, target):
    """Computes the Top-1 accuracy"""
    # 获取预测的类别索引（即最大值所在的索引）
    _, pred = output.max(1)
    # 计算预测正确的样本数
    correct = pred.eq(target).sum().item()
    # 计算准确率（百分比）
    accuracy = correct / target.size(0) * 100.0
    return accuracy


class AverageMeter(object):
    """Computes and stores the average and current value
       Imported from https://github.com/pytorch/examples/blob/master/imagenet/main.py#L247-L262
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
