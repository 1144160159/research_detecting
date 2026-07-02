"""TrafficEncoder with optional LoRA adapter (B1/B2).

Based on PPT Deck B specs:
  TrafficEncoder: LoRA Linear(in->hid->64), LayerNorm, MFM/SimCLR pretrained
  LoRA: rank=4, lora_a (rank x in), lora_b (out x rank), scaling=alpha/rank
"""

import math
import torch
from torch import nn
import torch.nn.functional as F


class LoRALinear(nn.Module):
    """Linear layer with optional low-rank adapter.

    When rank=0, behaves identically to nn.Linear.
    When rank>0: output = Linear(x) + lora_b @ lora_a @ x * (alpha / rank)

    PPT spec: rank=4, alpha=1.0
    """

    def __init__(self, in_features, out_features, rank=0, alpha=1.0, bias=True):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        self.rank = int(rank)
        self.alpha = float(alpha)
        if self.rank > 0:
            # lora_A: (rank, in_features), lora_B: (out_features, rank)
            self.lora_a = nn.Parameter(torch.zeros(self.rank, in_features))
            self.lora_b = nn.Parameter(torch.zeros(out_features, self.rank))
            self.scaling = self.alpha / self.rank
            self._reset_lora_parameters()
        else:
            self.lora_a = None
            self.lora_b = None
            self.scaling = 0.0

    def _reset_lora_parameters(self):
        if self.rank > 0:
            nn.init.kaiming_uniform_(self.lora_a, a=math.sqrt(5))
            nn.init.zeros_(self.lora_b)

    def forward(self, x):
        out = self.linear(x)
        if self.rank > 0:
            # delta_W @ x: lora_b @ (lora_a @ x^T)
            delta = F.linear(F.linear(x, self.lora_a), self.lora_b)
            out = out + delta * self.scaling
        return out


class TrafficEncoder(nn.Module):
    """Foundation traffic encoder with LoRA support.

    PPT spec:
      Architecture: LoRA Linear(in_dim -> hid) -> ReLU -> Dropout -> LoRA Linear(hid -> out_dim) -> LayerNorm
      Default: hid=128, out_dim=64, dropout=0.1
      Injection point: raw msg -> TrafficEncoder -> msg_fm (B, 64) -> TGNMemory
    """

    def __init__(self, in_dim, out_dim, hid=128, dropout=0.1, lora_rank=0, lora_alpha=1.0):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.hid = hid
        self.dropout = dropout
        self.lora_rank = int(lora_rank)

        self.net = nn.Sequential(
            LoRALinear(in_dim, hid, rank=lora_rank, alpha=lora_alpha),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            LoRALinear(hid, out_dim, rank=lora_rank, alpha=lora_alpha),
            nn.LayerNorm(out_dim),
        )

    def forward(self, msg_raw, normalize=False):
        z = self.net(msg_raw.float())
        if normalize:
            z = F.normalize(z, dim=-1)
        return z

    # ---- LoRA management (used by B2 online adaptation) ----

    def freeze_base_parameters(self):
        """Freeze all parameters except LoRA weights for online adaptation."""
        for name, param in self.named_parameters():
            param.requires_grad = 'lora_' in name

    def lora_parameters(self):
        """Return only LoRA-tagged parameters."""
        return [p for name, p in self.named_parameters() if 'lora_' in name]

    def lora_state_dict(self):
        """Snapshot LoRA weights for episode reset."""
        return {k: v.detach().clone() for k, v in self.state_dict().items() if 'lora_' in k}

    def load_lora_state_dict(self, state):
        """Restore LoRA weights from snapshot."""
        current = self.state_dict()
        current.update(state)
        self.load_state_dict(current)

    def parameter_summary(self):
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        lora = sum(p.numel() for p in self.lora_parameters())
        return {'total': total, 'trainable': trainable, 'lora': lora}
