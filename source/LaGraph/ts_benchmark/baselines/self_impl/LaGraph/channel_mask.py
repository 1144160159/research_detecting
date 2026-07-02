import torch
import torch.nn as nn
from einops import rearrange
from torch.nn.functional import gumbel_softmax


class channel_mask_generator(torch.nn.Module):
    def __init__(self, input_size, n_vars):
        super(channel_mask_generator, self).__init__()
        self.generator = nn.Sequential(torch.nn.Linear(input_size, n_vars, bias=False), nn.Sigmoid())
        with torch.no_grad():
            self.generator[0].weight.zero_()
        self.n_vars = n_vars

    def forward(self, x):  

        distribution_matrix = self.generator(x)
        
        resample_matrix = self._ste_resample(distribution_matrix)
        inverse_eye = 1 - torch.eye(self.n_vars).to(x.device)
        diag = torch.eye(self.n_vars).to(x.device)
        
        resample_matrix = torch.einsum("bchd,dd->bchd", resample_matrix, inverse_eye) + diag
        
        
        return resample_matrix

    def _ste_resample(self, distribution_matrix):
        """
        Use STE instead of Gumbel for binary hard mask
        """
        b, c, h, d = distribution_matrix.shape
        logits = distribution_matrix  # already in (0,1) from sigmoid

        mask = (logits > 0.5).float()
        ste_mask = (mask - logits).detach() + logits  # STE trick
        return ste_mask