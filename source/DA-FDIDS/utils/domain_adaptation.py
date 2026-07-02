"""Domain adaptation utilities for DA-FDIDS (B4-B7).

Based on PPT Deck B specs:
  B4: GRL (Gradient Reversal Layer) + DomainDiscriminator
  B5: MMD (Maximum Mean Discrepancy) with multi-scale RBF kernel
  B7: MHA Feature Weighting + RBF cache similarity + NDCG@K
"""

import torch
from torch import nn
import torch.nn.functional as F


# =========================================================================
# B4: Gradient Reversal Layer
# PPT spec: forward identity, backward dL/dx = -lambda * dL_adv/dx
# =========================================================================

class _GradientReverseFunction(torch.autograd.Function):
    """Autograd function that reverses gradient sign multiplied by lambda."""

    @staticmethod
    def forward(ctx, x, lambd):
        ctx.lambd = float(lambd)
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        # Reverse gradient: multiply by -lambda
        return -ctx.lambd * grad_output, None


class GradientReversalLayer(nn.Module):
    """Gradient Reversal Layer wrapper.

    PPT spec: placed before domain discriminator.
    lambda_adv default = 0.1 (configurable).
    """

    def __init__(self, lambd=1.0):
        super().__init__()
        self.lambd = float(lambd)

    def forward(self, x):
        return _GradientReverseFunction.apply(x, self.lambd)


class DomainDiscriminator(nn.Module):
    """Domain discriminator with built-in GRL.

    PPT spec: GRL -> Linear(in_dim, 32) -> ReLU -> Linear(32, 1)
    Output: scalar logit per sample (binary domain classification).
    Loss: BCE(source=0, target=1).
    """

    def __init__(self, in_dim, hidden_dim=32, grl_lambda=1.0):
        super().__init__()
        self.grl = GradientReversalLayer(grl_lambda)
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x):
        return self.net(self.grl(x)).view(-1)


# =========================================================================
# B5: MMD with multi-scale RBF kernel
# PPT spec: MMD^2 = E[k(x,x)] + E[k(y,y)] - 2E[k(x,y)]
#           k(x,y) = exp(-||x-y||^2 / 2*sigma^2)
#           Multi-scale: sigma in {0.1, 0.5, 1.0, 5.0, 10.0}
# =========================================================================

def multi_scale_rbf_kernel(x, y, sigmas=(0.1, 0.5, 1.0, 5.0, 10.0)):
    """Multi-scale Gaussian RBF kernel matrix.

    K(x,y) = sum_i exp(-||x-y||^2 / (2 * sigma_i^2))

    PPT spec: captures both fine-grained (small sigma) and
    coarse-grained (large sigma) similarity structures.
    """
    x = x.float()
    y = y.float()
    # Squared pairwise Euclidean distance
    dist = torch.cdist(x, y, p=2).pow(2)
    kernels = []
    for sigma in sigmas:
        denom = 2.0 * float(sigma) ** 2
        kernels.append(torch.exp(-dist / max(denom, 1e-12)))
    # Sum across scales
    return torch.stack(kernels, dim=0).sum(dim=0)


def mmd_loss(x, y, sigmas=(0.1, 0.5, 1.0, 5.0, 10.0)):
    """Maximum Mean Discrepancy between two distributions.

    MMD^2(x, y) = E[k(x,x)] + E[k(y,y)] - 2*E[k(x,y)]

    PPT spec: used for:
      B5: support-query distribution alignment (lambda_mmd=0.1)
      B6: Stable-LoRA constraint MMD(z_pre, z_post)
    Returns scalar tensor.
    """
    if x.numel() == 0 or y.numel() == 0:
        return x.new_tensor(0.0)
    k_xx = multi_scale_rbf_kernel(x, x, sigmas)
    k_yy = multi_scale_rbf_kernel(y, y, sigmas)
    k_xy = multi_scale_rbf_kernel(x, y, sigmas)
    return k_xx.mean() + k_yy.mean() - 2.0 * k_xy.mean()


# =========================================================================
# B7: MHA Feature Weighting
# PPT spec: Multi-head self-attention for feature subspaces
#           Up-weight domain-invariant dims, down-weight domain-specific
# =========================================================================

class FeatureAttentionWeighter(nn.Module):
    """Multi-Head Attention feature re-weighting.

    PPT spec: applies self-attention to feature dimensions,
    residual connection + LayerNorm.
    num_heads=4 (default, auto-adjusted to divide dim evenly).
    """

    def __init__(self, dim, num_heads=4):
        super().__init__()
        # Auto-adjust heads to divide dim evenly
        heads = max(1, min(int(num_heads), int(dim)))
        while dim % heads != 0 and heads > 1:
            heads -= 1
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x):
        # Add singleton sequence dimension for MHA (batch, 1, dim)
        seq = x.unsqueeze(1)
        weighted, _ = self.attn(seq, seq, seq, need_weights=False)
        return self.norm((weighted + seq).squeeze(1))


# =========================================================================
# B7: RBF similarity for cache retrieval
# PPT spec: multi-scale RBF kernel similarity with column normalization
# =========================================================================

def _normalize_columns(sim):
    """Min-max column-wise normalization to [0, 1]."""
    col_min = sim.min(dim=0, keepdim=True).values
    col_max = sim.max(dim=0, keepdim=True).values
    return (sim - col_min) / (col_max - col_min).clamp_min(1e-12)


def rbf_similarity_matrix(support_z, query_z, sigmas=(0.1, 0.5, 1.0, 5.0, 10.0)):
    """RBF kernel similarity for cache retrieval (B7).

    PPT spec: replaces dot-product cosine sim with multi-scale RBF,
    capturing fine+coarse-grained feature similarity.
    """
    return _normalize_columns(multi_scale_rbf_kernel(support_z, query_z, sigmas))


# =========================================================================
# B7: NDCG@K evaluation
# PPT spec: measures cache retrieval quality,
# NDCG@5 +11.5% with multi-scale RBF vs baseline
# =========================================================================

def ndcg_at_k(sim, support_labels, query_labels, k=5):
    """Normalized Discounted Cumulative Gain at K.

    PPT spec: evaluates cache retrieval ranking quality.
    Higher = retrieved neighbors better match query class.
    """
    if sim.numel() == 0:
        return 0.0
    k = max(1, min(int(k), sim.size(0)))
    support_labels = support_labels.view(-1)
    query_labels = query_labels.view(-1)

    scores = []
    # DCG discounts: 1/log2(rank+1) starting from rank=1
    discounts = 1.0 / torch.log2(torch.arange(k, device=sim.device, dtype=torch.float32) + 2.0)
    ideal = discounts.sum().clamp_min(1e-12)

    for col in range(sim.size(1)):
        # Top-K support items by similarity to this query
        order = torch.argsort(sim[:, col], descending=True)[:k]
        relevance = (support_labels[order] == query_labels[col]).float()
        dcg = (relevance * discounts).sum()
        scores.append(float(dcg.div(ideal).item()))

    return float(sum(scores) / max(len(scores), 1))


# =========================================================================
# Utility
# =========================================================================

def trainable_parameter_count(module):
    """Count trainable parameters in a module."""
    if module is None:
        return 0
    return int(sum(p.numel() for p in module.parameters() if p.requires_grad))
