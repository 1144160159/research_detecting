from collections import Counter
from sklearn.decomposition import TruncatedSVD
import torch
import torch.nn.functional as F
from scipy.sparse.linalg import svds
from torch_geometric.data import TemporalData
from torch_geometric.utils import to_undirected, degree
from torch_scatter import scatter_add
import numpy as np
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
from utils.LayerNorm import LayerNorm


def nodeMap(edge_index, mode='encode', decode_dict=None):
    if mode == 'encode':
        src, dst = edge_index.tolist()
        nodeSet = sorted(list(set(src + dst)))
        assoc = list(range(0, len(nodeSet)))
        m = [dict(zip(nodeSet, assoc)), dict(zip(assoc, nodeSet))]
        src = [m[0][i] for i in src]
        dst = [m[0][i] for i in dst]
        edge_index = torch.stack((torch.tensor(src), torch.tensor(dst)), dim=0)
        return edge_index, m
    elif mode == 'decode':
        src, dst = edge_index.tolist()
        src = [decode_dict[i] for i in src]
        dst = [decode_dict[i] for i in dst]
        edge_index = torch.stack((torch.tensor(src), torch.tensor(dst)), dim=0)
        return edge_index
    else:
        print('Error mode.')


def get_act(act_type):
    act_type = act_type.lower()
    if act_type == 'identity':
        return torch.nn.Identity()
    if act_type == 'relu':
        return torch.nn.ReLU(inplace=True)
    elif act_type == 'elu':
        return torch.nn.ELU(inplace=True)
    elif act_type == 'tanh':
        return torch.nn.Tanh()
    elif act_type == 'sigmoid':
        return torch.nn.LogSigmoid()
    else:
        raise NotImplementedError


def cal_norm(edge_index, num_nodes=None, self_loop=False, cut=False):
    # calculate normalization factors: (2*D)^{-1/2}
    if num_nodes is None:
        num_nodes = edge_index.max() + 1
    D = degree(edge_index[0], num_nodes)
    if self_loop:
        D = D + 1

    if cut:  # for symmetric adj
        D = torch.sqrt(1 / D)
        D[D == float("inf")] = 0.
        edge_index = to_undirected(edge_index, num_nodes=num_nodes)
        row, col = edge_index
        mask = row < col
        edge_index = edge_index[:, mask]
    else:
        D = torch.sqrt(1 / 2 / D)
        D[D == float("inf")] = 0.
    # D = Tensor([0.5] * num_nodes).to(device)
    if D.dim() == 1:
        D = D.unsqueeze(-1)
    return D, edge_index


@torch.enable_grad()
def regularize(z, x, reg_type, edge_index=None, norm_factor=None):
    z_reg = norm_factor * z

    if reg_type == 'Lap':  # Laplacian Regularization
        row, col = edge_index
        loss = scatter_add(((z_reg.index_select(0, row) - z_reg.index_select(0, col)) ** 2).sum(-1), col, dim=0,
                           dim_size=z.size(0))
        return loss.mean()

    elif reg_type == 'Dec':  # Feature Decorrelation
        zzt = torch.mm(z_reg.t(), z_reg)
        Dig = 1. / torch.sqrt(1e-8 + torch.diag(zzt, 0))
        z_new = torch.mm(z_reg, torch.diag(Dig))
        zzt = torch.mm(z_new.t(), z_new)
        zzt = zzt - torch.diag(torch.diag(zzt, 0))
        zzt = F.hardshrink(zzt, lambd=0.5)
        square_loss = F.mse_loss(zzt, torch.zeros_like(zzt))
        return square_loss

    else:
        raise NotImplementedError

def filtered_data(data, num, min_samples=100):
    unique_attacks = data['attack'].unique()
    # Filter to classes with enough samples for k_shot+q_query across all splits
    counts_all = Counter(data['attack'].tolist())
    eligible = [a.item() for a in unique_attacks if counts_all.get(a.item(), 0) >= min_samples]
    if len(eligible) < num:
        raise ValueError(f'Only {len(eligible)} classes have >= {min_samples} samples, need {num}.')
    perm = torch.randperm(len(eligible))[:num]
    selected_attacks = torch.tensor([eligible[i] for i in perm])
    other_attacks_mask = ~torch.isin(unique_attacks, selected_attacks)
    other_attacks = unique_attacks[other_attacks_mask]
    # print("selected:",selected_attacks)
    # print("other:",other_attacks)

    counts = Counter(data['attack'][torch.isin(data['attack'], selected_attacks)].tolist())
    counts_other = Counter(data['attack'][torch.isin(data['attack'], other_attacks)].tolist())
    # print("counts",counts)
    # print("counts_other",counts_other)
    sorted_attacks = sorted(counts, key=counts.get, reverse=True)
    sorted_other = sorted(counts_other, key=counts_other.get, reverse=True)

    attack_to_new_index = {attack: idx for idx, attack in enumerate(sorted_attacks)}
    attack_to_other_index = {attack: idx for idx, attack in enumerate(sorted_other)}
    selected_indices = torch.where(torch.isin(data['attack'], selected_attacks))[0]
    other_indices = torch.where(~torch.isin(data['attack'], selected_attacks))[0]

    def create_temporal_data(data, indices, attack_to_index):
        new_attack_indices = torch.tensor([attack_to_index[a.item()] for a in data['attack'][indices]], dtype=torch.long)
        return TemporalData(
            src=data['src'][indices],
            dst=data['dst'][indices],
            t=data['t'][indices],
            msg=data['msg'][indices],
            src_layer=data['src_layer'][indices],
            dst_layer=data['dst_layer'][indices],
            dt=data['dt'][indices],
            label=data['label'][indices],
            attack=new_attack_indices
        )

    filtered_data_selected = create_temporal_data(data, selected_indices, attack_to_new_index)
    other_data_selected = create_temporal_data(data, other_indices, attack_to_other_index)

    # torch.save(filtered_data_selected, f"{save_path}_selected.pt")
    # torch.save(other_data_selected, f"{save_path}_other.pt")
    # print(filtered_data_selected)
    return filtered_data_selected, other_data_selected



def enhance_sim_matrix(C, K, d, alpha):
    # C: coefficient matrix, K: number of clusters, d: dimension of each subspace
    C = 0.5 * (C + C.T)
    r = min(d * K + 1, C.shape[0] - 1)
    U, S, _ = svds(C, r, v0=np.ones(C.shape[0]))
    U = U[:, ::-1]
    S = np.sqrt(S[::-1])
    S = np.diag(S)
    U = U.dot(S)
    U = normalize(U, norm='l2', axis=1)
    Z = U.dot(U.T)
    Z = Z * (Z > 0)
    L = np.abs(Z ** alpha)
    L = 0.5 * (L + L.T)
    L = L / L.max()
    return L


def repeat_column(matrix, j):
    num_columns = matrix.shape[1]
    if j < 0 or j >= num_columns:
        raise ValueError("Invalid column index")
    column = matrix[:, j]
    repeated_column = np.tile(column, (1, num_columns - 1))
    return repeated_column


def delta2(x):
    """Vectorized delta2. x: (n, d). Returns (n, n).

    Closed form: sum_{p≠q} (c_p - c_q)(c_p - c_q)^T = 2 * (d*S - M@M^T)
    where S = x @ x.T and M = sum of columns of x.
    """
    d = x.shape[1]
    S = x @ x.T
    M = x.sum(dim=1, keepdim=True)
    return 2.0 * (d * S - M @ M.T)


# Repeat a specific column of a tensor (kept for API compatibility)
def repeat_column(tensor, col_index):
    return tensor[:, col_index].unsqueeze(1).repeat(1, tensor.shape[1]-1)



def compute_Q_star(Z, P, gamma, Phi1, Phi2, mu, Q_tilde):
    """Q* update via matrix inverse (original numerically proven path)."""
    Delta3 = P.t() @ Z + Phi1 / mu
    numerator = mu * gamma * Delta3 @ Z.t() @ P + mu * Q_tilde - Phi2
    denominator = mu * gamma ** 2 * P.t() @ Z @ Z.t() @ P + mu * torch.eye(Z.shape[0])
    Q_star = (torch.inverse(denominator) @ numerator) * 0.0001
    return Q_star
  


def compute_tilde_Q_star(Q, Phi2, mu):
    """Nuclear norm proximal operator via SVD soft-thresholding.

    Uses deprecated torch.svd for numerical robustness matching the original paper.
    """
    M = Q + Phi2 / mu
    U, Sigma, Vt = torch.svd(M)
    S = torch.matmul(U, torch.matmul(
        torch.diag(torch.sign(Sigma) * torch.maximum(torch.abs(Sigma - 1 / mu), torch.tensor(0.0))), Vt))
    return S


def MFL(x, C, gamma, Eta, alpha):
    n, d = x.shape
    Z = x.cpu()
    phi1 = torch.randn((n, d)) * 0.01
    phi2 = torch.zeros((n, n))
    mu = 0.1
    mu_max = 1e7
    mu_min = 1e-8
    mu_decay = 0.9
    Q = torch.zeros((n, n))
    Q_tilde = Q
    result = None
    layer = LayerNorm

    # Precompute constant terms (independent of Q, mu)
    delta1 = Z * (1.0 - gamma)
    x1_const = alpha * delta1 @ delta1.t()
    x2_const = Eta * delta2(Z)
    base = x1_const - x2_const
    eye_n = torch.eye(n)

    for _ in range(50):
        delta3 = Z - gamma * Q @ Z
        mat = base + mu * delta3 @ delta3.t() + eye_n * 1.000001

        # P update via solve (avoids explicit inverse)
        try:
            X = torch.linalg.solve(mat, delta3)
        except RuntimeError:
            X = torch.linalg.lstsq(mat, delta3).solution
        P = -(phi1 @ X.T)

        Q = compute_Q_star(Z, P, gamma, phi1, phi2, mu, Q_tilde=Q_tilde)
        Q_tilde = compute_tilde_Q_star(Q, phi2, mu)
        if result is None:
            result = 0.5 * (Q + Q.t())

        phi1 = phi1 + mu * (P.t() @ Z - gamma * P.t() @ Q @ Z)
        phi2 = phi2 + mu * (Q - Q_tilde)
        mu = max(min(1.01 * mu * mu_decay, mu_max), mu_min)

        expression_value = torch.norm((P @ Z - gamma * P @ Q @ Z), float('inf'))
        expression_final = layer.item(expression_value)
        if expression_final < 1e-6:
            break
    return result