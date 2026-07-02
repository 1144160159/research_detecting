import torch
import torch.nn as nn
import torch.nn.functional as F
class moving_avg(nn.Module):
    """
    Moving average block to highlight the trend of time series
    """
    def __init__(self, kernel_size, stride):
        super(moving_avg, self).__init__()
        self.kernel_size = kernel_size
        self.avg = nn.AvgPool1d(kernel_size=kernel_size, stride=stride, padding=0)

    def forward(self, x):
        # padding on the both ends of time series
        front = x[:, 0:1, :].repeat(1, (self.kernel_size - 1) // 2, 1)
        end = x[:, -1:, :].repeat(1, (self.kernel_size - 1) // 2, 1)
        x = torch.cat([front, x, end], dim=1)
        x = self.avg(x.permute(0, 2, 1))
        x = x.permute(0, 2, 1)
        return x


class series_decomp(nn.Module):
    """
    Series decomposition block
    """

    def __init__(self):
        super(series_decomp, self).__init__()
        self.moving_avg = moving_avg(25, stride=1)

    def forward(self, x):
        moving_mean = self.moving_avg(x)
        res = x - moving_mean
        return res, moving_mean


class MovingAvg(nn.Module):
    def __init__(self, kernel_size, stride=1):
        super(MovingAvg, self).__init__()
        self.kernel_size = kernel_size
        self.avg = nn.AvgPool1d(kernel_size=kernel_size, stride=stride, padding=0)

    def forward(self, x):
        pad = (self.kernel_size - 1) // 2
        front = x[:, 0:1, :].repeat(1, pad, 1)
        end = x[:, -1:, :].repeat(1, pad, 1)
        x = torch.cat([front, x, end], dim=1)
        x = self.avg(x.permute(0, 2, 1))
        return x.permute(0, 2, 1)


class GatingNet(nn.Module):
    def __init__(self, input_dim, num_experts):
        super(GatingNet, self).__init__()
        self.gate = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(input_dim, num_experts),
        )

    def forward(self, x):
        # x: [B, L, C] → permute to [B, C, L] for pooling
        x = x.permute(0, 2, 1)
        weights = F.softmax(self.gate(x), dim=1)  # [B, num_experts]
        return weights

class MoEDecomposition(nn.Module):
    def __init__(self, input_dim, kernel_sizes=[5, 15, 25, 35, 45]):
        super(MoEDecomposition, self).__init__()
        self.experts = nn.ModuleList([MovingAvg(k) for k in kernel_sizes])
        self.gating = GatingNet(input_dim=input_dim, num_experts=len(kernel_sizes))

    def forward(self, x):
        # x: [B, L, C]
        expert_outputs = [expert(x) for expert in self.experts]  # List of [B, L, C]
        stacked_means = torch.stack(expert_outputs, dim=1)  # [B, num_experts, L, C]
        gate_weights = self.gating(x).unsqueeze(-1).unsqueeze(-1)  # [B, num_experts, 1, 1]

        moving_mean = torch.sum(gate_weights * stacked_means, dim=1)  # [B, L, C]
        res = x - moving_mean
        return res, moving_mean