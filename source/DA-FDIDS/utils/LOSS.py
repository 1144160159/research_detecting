from utils.funcs import *


class Orthorize_Loss(torch.nn.Module):
    def __init__(self):
        super(Orthorize_Loss, self).__init__()

    def forward(self, z):
        zzt = torch.mm(z.t(), z)
        Dig = 1. / torch.sqrt(1e-8 + torch.diag(zzt, 0))
        z_new = torch.mm(z, torch.diag(Dig))
        zzt = torch.mm(z_new.t(), z_new)
        zzt = zzt - torch.diag(torch.diag(zzt, 0))
        zzt = F.hardshrink(zzt, lambd=0.5)
        square_loss = F.mse_loss(zzt, torch.zeros_like(zzt))
        return square_loss


class FocalLoss(torch.nn.Module):
    def __init__(self, class_num, alpha=None, gamma=2, size_average=True):
        super(FocalLoss, self).__init__()
        if alpha is None:
            self.alpha = Variable(torch.ones(class_num, 1))
        else:
            if isinstance(alpha, Variable):
                self.alpha = alpha
            else:
                self.alpha = Variable(alpha)
        self.gamma = gamma
        self.class_num = class_num
        self.size_average = size_average

    def forward(self, inputs, targets):
        N, C = inputs.size(0), inputs.size(1)
        P = F.softmax(inputs, dim=-1)

        # 关键：scatter index 必须是 int64
        ids = targets.view(-1, 1).to(device=inputs.device, dtype=torch.long)

        class_mask = torch.zeros((N, C), device=inputs.device, dtype=inputs.dtype)
        class_mask.scatter_(1, ids, 1.0)

        alpha = self.alpha.to(inputs.device)
        alpha = alpha[ids.view(-1)]  # (N,) or (N,1) 都可

        probs = (P * class_mask).sum(1).view(-1, 1).clamp_min(1e-12)
        log_p = probs.log()

        batch_loss = -alpha.view(-1, 1) * (torch.pow((1 - probs), self.gamma)) * log_p

        return batch_loss.mean() if self.size_average else batch_loss.sum()


from torch.autograd import Variable

from utils.funcs import *


class Loss(torch.nn.Module):
    def __init__(self, label_num, class_num, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Loss1 = FocalLoss(label_num)
        self.Loss2 = FocalLoss(class_num)
        self.Loss3 = Orthorize_Loss()

    def forward(self, bin_inputs, mul_inputs, label, attack, z):
        return self.Loss1(bin_inputs, label) + self.Loss2(mul_inputs, attack) + self.Loss3(z)
