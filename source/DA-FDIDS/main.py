#!/opt/conda/envs/py3.9/bin/python
# DA-FDIDS: B0 (DIDS-MFL) -> B8 (Full DA-FDIDS) progressive runner.
# All B0 logic preserved from original DIDS-MFL baseline.
# New components (B1-B8) enabled via CLI switches, all default OFF.

import argparse
import csv
import json
import logging
import os
import random
import time
from collections import Counter

import numpy as np
import torch
import torch.nn.functional as F
import tqdm
from sklearn.manifold import TSNE
from sklearn.metrics import f1_score, normalized_mutual_info_score, precision_recall_fscore_support

from torch_geometric.loader import TemporalDataLoader
from torch_geometric.nn import TGNMemory
from torch_geometric.nn.models.tgn import IdentityMessage, LastAggregator, LastNeighborLoader

# B0 original modules (untouched)
from model.MGD import MGD
from model.SE import SelfExpr
from utils.LOSS import Loss
from utils.MLP import MLPPredictor
from utils.funcs import MFL, cal_norm, enhance_sim_matrix, filtered_data, nodeMap

# B1-B8 new modules (built from PPT specs)
from model.traffic_encoder import TrafficEncoder
from utils.domain_adaptation import (
    DomainDiscriminator,
    FeatureAttentionWeighter,
    GradientReversalLayer,
    mmd_loss,
    ndcg_at_k,
    rbf_similarity_matrix,
    trainable_parameter_count,
)

import matplotlib.pyplot as plt
plt.switch_backend('agg')


# =========================================================================
# CLI
# =========================================================================
def parse_args():
    p = argparse.ArgumentParser(description='DA-FDIDS progressive runner (B0-B8)')

    # Data & episode
    p.add_argument('--dataset_train', '--dataset', dest='dataset_train', type=str, default='CIC-BoT-IoT_new')
    p.add_argument('--dataset_test', type=str, default=None)
    p.add_argument('--way', type=int, default=5)
    p.add_argument('--k_shot', type=int, default=5)
    p.add_argument('--q_query', type=int, default=15)
    p.add_argument('--pretrain_epochs', type=int, default=1)
    p.add_argument('--meta_epochs', type=int, default=100)
    p.add_argument('--repetitions', type=int, default=10)
    p.add_argument('--max_restarts', type=int, default=10)
    p.add_argument('--seed', type=int, default=3407)
    p.add_argument('--batch_size', type=int, default=50)

    # --- Component switches (all default OFF = pure B0) ---
    p.add_argument('--use_foundation_encoder', action='store_true', help='B1: TrafficEncoder before TGNMemory')
    p.add_argument('--use_lora_adapt', action='store_true', help='B2: Online LoRA few-shot adaptation')
    p.add_argument('--use_cache_fusion', action='store_true', help='B3: Cache retrieval + similarity fusion')
    p.add_argument('--use_grl_da', action='store_true', help='B4: GRL domain-adversarial training')
    p.add_argument('--use_mmd_align', action='store_true', help='B5: MMD distribution alignment')
    p.add_argument('--use_stable_lora', action='store_true', help='B6: Stable-LoRA MMD constraint')
    p.add_argument('--use_rbf_cache', action='store_true', help='B7: Multi-scale RBF cache kernel')
    p.add_argument('--use_mha_weighting', action='store_true', help='B7: MHA feature weighting')
    p.add_argument('--adaptive_cache_alpha', action='store_true', help='B8: Episode-adaptive cache alpha')

    # --- Component hyperparameters ---
    p.add_argument('--load_foundation_ckpt', action='store_true')
    p.add_argument('--foundation_ckpt', type=str, default='./checkpoints/encoder_pretrained.pth')
    p.add_argument('--encoder_dim', type=int, default=64)
    p.add_argument('--encoder_hid', type=int, default=128)
    p.add_argument('--encoder_dropout', type=float, default=0.1)

    p.add_argument('--lora_rank', type=int, default=4)
    p.add_argument('--lora_alpha', type=float, default=1.0)
    p.add_argument('--lora_steps', type=int, default=3)
    p.add_argument('--lora_lr', type=float, default=1e-3)
    p.add_argument('--no_lora_reset_each_episode', action='store_true')

    p.add_argument('--cache_alpha', type=float, default=0.7, help='MFL weight in S_final = alpha*S_MFL + (1-alpha)*S_cache')
    p.add_argument('--cache_time_decay', action='store_true')
    p.add_argument('--cache_tau', type=float, default=3600.0)
    p.add_argument('--subspace_dim', type=int, default=4)

    p.add_argument('--grl_lambda', type=float, default=1.0)
    p.add_argument('--domain_loss_weight', type=float, default=0.1)
    p.add_argument('--mmd_weight', type=float, default=0.1)
    p.add_argument('--stable_lora_weight', type=float, default=0.1)

    p.add_argument('--mha_heads', type=int, default=4)
    p.add_argument('--ndcg_k', type=int, default=5)

    # Output control
    p.add_argument('--smoke_test', action='store_true')
    p.add_argument('--skip_plots', action='store_true')
    p.add_argument('--output_csv', type=str, default='')
    p.add_argument('--output_json', type=str, default='')
    p.add_argument('--no_checkpoint', action='store_true')
    p.add_argument('--checkpoint_dir', type=str, default='')

    return p.parse_args()


# =========================================================================
# Helpers (refactored from original main.py)
# =========================================================================
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def resolve_data_path(base_name):
    """Resolve .pt file with fuzzy name matching."""
    import glob as _glob
    candidates = [f'./data/{base_name}.pt', f'./data/{base_name}_new.pt']
    for path in candidates:
        if os.path.exists(path):
            return path
    all_pts = _glob.glob('./data/*.pt')
    keywords = base_name.lower().replace('-', ' ').replace('_', ' ').split()
    for pt in all_pts:
        pt_lower = os.path.basename(pt).lower()
        if all(kw in pt_lower for kw in keywords):
            return pt
    raise FileNotFoundError(f'No data file found for {base_name}')


def min_max_normalize(values):
    """Original B0 min_max_normalize, adapted for list input."""
    arr = list(values)
    min_v, max_v = min(arr), max(arr)
    diff = max_v - min_v
    if diff == 0:
        diff = 0.1
    return [(x - min_v) / diff for x in arr]


def sample_episode(datax, classes, k, num_query):
    """Episode sampling: k support + num_query query per class."""
    indices_support = []
    indices_query = []
    required = k + num_query
    for cls in classes:
        x = np.where(datax.attack.cpu().numpy() == cls)[0]
        if len(x) < required:
            raise ValueError(f'Class {cls} has {len(x)} samples, needs {required}.')
        selected = np.random.choice(x, size=required, replace=False).tolist()
        indices_support.extend(selected[:k])
        indices_query.extend(selected[k:])
    return datax[indices_support], datax[indices_query]


def split_train_val_test(datax, classes, test_ratio=0.2, train_ratio=0.6):
    """B0-style stratified class-balanced split. Original logic preserved."""
    train_indices, val_indices, test_indices = [], [], []
    attack_np = datax.attack.cpu().numpy()
    for cls in classes:
        class_indices = np.where(attack_np == cls)[0]
        if len(class_indices) == 0:
            continue
        class_indices = class_indices.copy()
        np.random.shuffle(class_indices)
        test_end = int(len(class_indices) * test_ratio)
        test_class = class_indices[:test_end]
        remaining = class_indices[test_end:].copy()
        np.random.shuffle(remaining)
        val_end = int(len(remaining) * (1 - train_ratio))
        val_class = remaining[:val_end]
        train_class = remaining[val_end:]
        train_indices.extend(train_class.tolist())
        val_indices.extend(val_class.tolist())
        test_indices.extend(test_class.tolist())
    return datax[train_indices], datax[val_indices], datax[test_indices]


def class_scores_from_similarity(mat, support_labels, classes, device='cpu'):
    """GPU-native class scoring from similarity matrix.

    For each query column, computes per-class mean similarity,
    min-max normalizes, and returns softmax-ready scores + argmax preds.
    """
    if not torch.is_tensor(mat):
        mat = torch.as_tensor(mat)
    mat = mat.to(device=device)
    s_labels = torch.as_tensor(support_labels, device=device)
    classes_t = torch.tensor(classes, device=device)
    scores_list = []
    for cls in classes_t:
        mask = (s_labels == cls)
        cls_mean = mat[mask].mean(dim=0) if mask.any() else torch.zeros(mat.size(1), device=device)
        scores_list.append(cls_mean)
    scores = torch.stack(scores_list, dim=1)  # (num_query, num_classes)
    scores_min = scores.min(dim=1, keepdim=True).values
    scores_max = scores.max(dim=1, keepdim=True).values
    denom = (scores_max - scores_min).clamp_min(1e-12)
    scores = (scores - scores_min) / denom
    preds = scores.argmax(dim=1).cpu().tolist()
    return scores.cpu(), preds


def cache_similarity_matrix(encoder, support, query, device,
                            use_time_decay=False, tau=3600.0,
                            use_rbf=False, feature_weighter=None):
    """B3 cache similarity: S_cache = cos_sim(q, keys) or RBF kernel.

    PPT spec: training-free support-set memory, <1ms online latency.
    Returns numpy array (num_support, num_query).
    """
    with torch.no_grad():
        s_msg = support.msg.float().to(device)
        q_msg = query.msg.float().to(device)
        if encoder is not None:
            s = encoder(s_msg, normalize=True)
            q = encoder(q_msg, normalize=True)
        else:
            s = F.normalize(s_msg, dim=-1)
            q = F.normalize(q_msg, dim=-1)

        # B7: MHA feature weighting
        if feature_weighter is not None:
            s = F.normalize(feature_weighter(s), dim=-1)
            q = F.normalize(feature_weighter(q), dim=-1)

        # B7: RBF kernel instead of dot-product cosine
        if use_rbf:
            sim = rbf_similarity_matrix(s, q)
        else:
            sim = torch.matmul(s, q.T)   # cosine similarity (vectors are normalized)
            sim = (sim + 1.0) * 0.5       # scale to [0, 1]

        # Column normalization
        col_min = sim.min(dim=0, keepdim=True).values
        col_max = sim.max(dim=0, keepdim=True).values
        sim = (sim - col_min) / (col_max - col_min).clamp_min(1e-12)

        # Optional time decay
        if use_time_decay:
            st = support.t.float().to(device).view(-1, 1)
            qt = query.t.float().to(device).view(1, -1)
            tau_val = max(float(tau), 1e-6)
            sim = sim * torch.exp(-torch.abs(qt - st) / tau_val)
            col_min2 = sim.min(dim=0, keepdim=True).values
            col_max2 = sim.max(dim=0, keepdim=True).values
            sim = (sim - col_min2) / (col_max2 - col_min2).clamp_min(1e-12)

        return sim.cpu().numpy()


def num_nodes_for(*data_objs):
    max_nodes = 0
    for data in data_objs:
        if data is None:
            continue
        max_nodes = max(max_nodes, int(data.num_nodes))
        if getattr(data, 'src', None) is not None and data.src.numel() > 0:
            max_nodes = max(max_nodes, int(torch.max(torch.cat([data.src, data.dst])).item()) + 1)
    return max_nodes


def plot_artifacts(x2, sim_matrix, labels, file_name, suffix):
    """t-SNE + heatmap visualization (B0 logic preserved)."""
    os.makedirs('./pic', exist_ok=True)
    os.makedirs('./picdata', exist_ok=True)
    np.save('./picdata/labels.npy', np.asarray(labels))
    sim_np = sim_matrix if isinstance(sim_matrix, np.ndarray) else sim_matrix.cpu().numpy()
    np.save('./picdata/heatmap_features.npy', sim_np)
    out_embedding = x2.detach().cpu().numpy()
    if out_embedding.shape[0] <= 2:
        return
    perplexity = min(20, max(1, out_embedding.shape[0] - 1))
    tsne = TSNE(n_components=2, perplexity=perplexity, early_exaggeration=12,
                random_state=42, init='random', learning_rate=1000.0)
    tsne_results = tsne.fit_transform(out_embedding)
    np.save('./picdata/t-SNE_embeddings.npy', tsne_results)
    plt.figure(figsize=(10, 8))
    plt.scatter(tsne_results[:, 0] * 0.25, tsne_results[:, 1] * 0.25, c=labels, alpha=0.6, s=150)
    plt.savefig(f'./pic/tsne{suffix}_{file_name}.pdf', bbox_inches='tight')
    plt.close('all')
    plt.figure(figsize=(24, 20))
    cax = plt.matshow(np.corrcoef(sim_np, rowvar=False), cmap='Blues')
    cax.figure.colorbar(cax, fraction=0.046, pad=0.04)
    plt.savefig(f'./pic/heatmap{suffix}_{file_name}.pdf', dpi=600, bbox_inches='tight', pad_inches=0.1)
    plt.close('all')


# =========================================================================
# DAFDIDSRunner
# =========================================================================
class DAFDIDSRunner:
    def __init__(self, args):
        self.args = args
        set_seed(args.seed)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

        # B0-compatible dataset naming
        self.dataset_test = args.dataset_test or args.dataset_train
        self.file_name = self.dataset_test

        os.makedirs('./checkpoints', exist_ok=True)
        logging.basicConfig(
            filename=f'evaluation_{self.file_name}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True,
        )
        print(f'Device={self.device}')
        logging.info('Switches: foundation=%s lora=%s cache=%s grl=%s mmd=%s stable_lora=%s rbf=%s mha=%s adaptive_alpha=%s',
                     args.use_foundation_encoder, args.use_lora_adapt, args.use_cache_fusion,
                     args.use_grl_da, args.use_mmd_align, args.use_stable_lora,
                     args.use_rbf_cache, args.use_mha_weighting, args.adaptive_cache_alpha)

        self.classes = list(range(args.way))
        self.episode_max_n = args.way * (args.k_shot + args.q_query)
        self.memory_dim = self.time_dim = self.embedding_dim = 64
        self.cost_records = []

        # ---- Load data (B0 logic lines 36-98) ----
        train_path = resolve_data_path(args.dataset_train)
        test_path = resolve_data_path(self.dataset_test)

        self.data_all = torch.load(train_path, weights_only=False)
        idx = (self.data_all.attack >= 0).nonzero(as_tuple=False).view(-1)
        self.data_all = self.data_all[idx]
        print("after filter -1:", self.data_all.attack.unique(return_counts=True))

        if test_path != train_path:
            self.raw_test = torch.load(test_path, weights_only=False)
            idx_t = (self.raw_test.attack >= 0).nonzero(as_tuple=False).view(-1)
            self.raw_test = self.raw_test[idx_t]
        else:
            self.raw_test = self.data_all

        self.raw_msg_dim = int(self.data_all.msg.size(-1))
        test_msg_dim = int(self.raw_test.msg.size(-1))

        # Cross-domain feature alignment
        if test_msg_dim != self.raw_msg_dim:
            target_dim = min(self.raw_msg_dim, test_msg_dim)
            if self.raw_msg_dim > target_dim:
                print(f'Feature aligned: train {self.raw_msg_dim}d -> {target_dim}d')
                self.data_all.msg = self.data_all.msg[..., :target_dim]
                self.raw_msg_dim = target_dim
            if test_msg_dim > target_dim:
                print(f'Feature aligned: test {test_msg_dim}d -> {target_dim}d')
                self.raw_test.msg = self.raw_test.msg[..., :target_dim]

        # B0 filtered_data: data1 = selected, _ = other
        self.class_meta_train = args.way
        self.class_meta_test = args.way
        self.data1, _ = filtered_data(self.data_all, self.class_meta_train)
        self.data = self.data1
        print(self.data['attack'].unique())
        print(self.data1)

        # Cross-domain: separate test pool from target dataset
        if test_path != train_path:
            self.meta_test_pool, _ = filtered_data(self.raw_test, args.way)
            self.meta_test_pool = self.meta_test_pool.to(self.device)
            print(f'Cross-domain test pool: {Counter(self.meta_test_pool.attack.cpu().tolist())}')
        else:
            self.meta_test_pool = self.data1.to(self.device)

        # ---- Validate switch dependencies ----
        if args.use_lora_adapt and not args.use_foundation_encoder:
            raise ValueError('--use_lora_adapt requires --use_foundation_encoder')
        da_flags = (args.use_grl_da or args.use_mmd_align or args.use_stable_lora or
                    args.use_mha_weighting or args.adaptive_cache_alpha)
        if da_flags and not args.use_foundation_encoder:
            raise ValueError('DA-FDIDS switches require --use_foundation_encoder')
        cache_enhance = args.use_rbf_cache or args.use_mha_weighting or args.adaptive_cache_alpha
        if cache_enhance and not args.use_cache_fusion:
            raise ValueError('Cache retrieval enhancements require --use_cache_fusion')

        # ---- Build components ----

        # B1: TrafficEncoder
        self.traffic_encoder = None
        if args.use_foundation_encoder:
            self.traffic_encoder = TrafficEncoder(
                self.raw_msg_dim, args.encoder_dim,
                hid=args.encoder_hid, dropout=args.encoder_dropout,
                lora_rank=args.lora_rank if args.use_lora_adapt else 0,
                lora_alpha=args.lora_alpha,
            ).to(self.device)
            if args.load_foundation_ckpt:
                self._load_encoder_ckpt(args.foundation_ckpt)
            if args.use_lora_adapt:
                self.traffic_encoder.freeze_base_parameters()
            print(f'Foundation encoder ON: raw_msg_dim={self.raw_msg_dim}, out_dim={args.encoder_dim}, params={self.traffic_encoder.parameter_summary()}')
        else:
            print(f'Baseline B0 mode: msg_dim={self.raw_msg_dim}')

        self.msg_dim = args.encoder_dim if args.use_foundation_encoder else self.raw_msg_dim

        # B4: DomainDiscriminator
        self.domain_discriminator = None
        if args.use_grl_da:
            self.domain_discriminator = DomainDiscriminator(
                self.msg_dim, hidden_dim=32, grl_lambda=args.grl_lambda).to(self.device)

        # B7: FeatureAttentionWeighter
        self.feature_weighter = None
        if args.use_mha_weighting:
            self.feature_weighter = FeatureAttentionWeighter(self.msg_dim, num_heads=args.mha_heads).to(self.device)

        # B0: TGNMemory + MGD + predictors + SelfExpr (lines 100-142 logic)
        self.num_nodes = num_nodes_for(self.data1, self.data, self.raw_test)
        if self.data.src is None or len(self.data.src) == 0:
            self.neighbor_loader = LastNeighborLoader(self.data1.num_nodes, size=20, device=self.device)
        else:
            self.neighbor_loader = LastNeighborLoader(self.data.num_nodes + self.data1.num_nodes, size=20, device=self.device)

        self.memory = TGNMemory(
            self.num_nodes, self.msg_dim, self.memory_dim, self.time_dim,
            message_module=IdentityMessage(self.msg_dim, self.memory_dim, self.time_dim),
            aggregator_module=LastAggregator(),
        ).to(self.device)

        gind_params = {
            'num_layers': 1, 'alpha': 0.02, 'hidden_channels': 64, 'drop_input': True, 'dropout_imp': 0.5,
            'dropout_exp': 0.0, 'iter_nums': [36, 4], 'linear': True, 'double_linear': True,
            'act_imp': 'tanh', 'act_exp': 'elu', 'rescale': True, 'residual': True,
            'norm': 'LayerNorm', 'final_reduce': None,
        }
        self.mgd = MGD(in_channels=self.embedding_dim, out_channels=self.embedding_dim, **gind_params).to(self.device)
        self.bin_predictor = MLPPredictor(in_features=self.embedding_dim, out_classes=2).to(self.device)
        self.mul_predictor = MLPPredictor(in_features=self.embedding_dim, out_classes=self.class_meta_test).to(self.device)
        self.criterion = Loss(2, self.class_meta_test)
        self.semodel = SelfExpr(self.episode_max_n).to(self.device)

        # Optimizers
        da_params = []
        if self.domain_discriminator is not None:
            da_params += list(self.domain_discriminator.parameters())
        if self.feature_weighter is not None:
            da_params += list(self.feature_weighter.parameters())
        self.optimizer1 = torch.optim.Adam(list(self.semodel.parameters()) + da_params)
        self._reset_pretrain_optimizer()

        # B0: association tensor
        if self.data.src is None or len(self.data.src) == 0:
            self.assoc = torch.empty(self.data1.num_nodes, dtype=torch.long, device=self.device)
        else:
            self.assoc = torch.empty(self.data1.num_nodes + self.data.num_nodes, dtype=torch.long, device=self.device)

        self.train_loader = TemporalDataLoader(self.data, batch_size=args.batch_size)
        self.checkpoint_dir = args.checkpoint_dir or os.path.join('./checkpoints', self.file_name)
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Encoder helpers
    # ------------------------------------------------------------------
    def _load_encoder_ckpt(self, path):
        if not os.path.exists(path):
            print(f'Warning: checkpoint {path} not found; using random init')
            return
        ckpt = torch.load(path, map_location=self.device, weights_only=False)
        state = ckpt.get('encoder_state_dict', ckpt)
        missing, unexpected = self.traffic_encoder.load_state_dict(state, strict=False)
        print(f'Loaded encoder ckpt: missing={len(missing)} unexpected={len(unexpected)}')

    def _reset_pretrain_optimizer(self):
        params = list(self.memory.parameters()) + list(self.mgd.parameters())
        if self.traffic_encoder is not None:
            params += [p for p in self.traffic_encoder.parameters() if p.requires_grad]
        self.optimizer = torch.optim.Adam(params, lr=0.0001)

    def encode_msg(self, msg):
        """B1: encode raw msg through TrafficEncoder, or return raw."""
        if self.traffic_encoder is not None:
            return self.traffic_encoder(msg)
        return msg

    def reset_episode_state(self):
        """B0: clear TGN memory and neighbor loader for new episode."""
        self.memory.reset_state()
        self.neighbor_loader.reset_state()

    def edge_vectors(self, batch):
        """B0 core: TGNMemory + MGD -> cat(z_src, z_dst) edge vectors.

        Original B0 logic preserved: nodeMap -> cal_norm -> mgd -> cat.
        Extended: TrafficEncoder encodes msg before memory update.
        """
        src, dst, t, msg = batch.src, batch.dst, batch.t, batch.msg
        n_id = torch.cat([src, dst]).unique()
        n_id, _, _ = self.neighbor_loader(n_id)
        self.assoc[n_id] = torch.arange(n_id.size(0), device=self.device)
        z, _ = self.memory(n_id)
        ed, _ = nodeMap(torch.stack((src, dst), dim=0))
        ed = ed.to(self.device)
        norm_factor, ed = cal_norm(ed, num_nodes=len(z), self_loop=False)
        z = self.mgd(z, ed, norm_factor).to(self.device)
        vectors = torch.cat([z[self.assoc[src]], z[self.assoc[dst]]], dim=1)
        encoded = self.encode_msg(msg)
        if self.traffic_encoder is not None:
            encoded = encoded.detach()
        self.memory.update_state(src, dst, t, encoded)
        self.neighbor_loader.insert(src, dst)
        return vectors

    # ------------------------------------------------------------------
    # B2: Online LoRA adaptation (PPT spec: 3 steps, lr=1e-3, rank=4)
    # ------------------------------------------------------------------
    def online_lora_adapt(self, support):
        args = self.args
        if not args.use_lora_adapt:
            return None, {'enabled': False, 'seconds': 0.0, 'params': 0, 'loss': 0.0}

        lora_state = self.traffic_encoder.lora_state_dict() if not args.no_lora_reset_each_episode else None
        params = self.traffic_encoder.lora_parameters()
        opt = torch.optim.Adam(params, lr=args.lora_lr)
        labels = support.attack.long().to(self.device)
        start = time.perf_counter()
        final_loss = 0.0
        self.traffic_encoder.train()

        for _ in range(args.lora_steps):
            z = self.traffic_encoder(support.msg.float().to(self.device), normalize=True)
            # Prototype-based cross-entropy on support set
            classes = torch.unique(labels, sorted=True)
            prototypes = []
            for cls in classes:
                mask = labels == cls
                prototypes.append(z[mask].mean(dim=0) if mask.any() else torch.zeros_like(z[0]))
            prototypes = torch.stack(prototypes, dim=0)
            z_n = F.normalize(z, dim=-1)
            p_n = F.normalize(prototypes, dim=-1)
            logits = torch.matmul(z_n, p_n.T) / 0.2
            mapping = {int(c.item()): i for i, c in enumerate(classes)}
            target = torch.tensor([mapping[int(l.item())] for l in labels], device=self.device)
            loss = F.cross_entropy(logits, target)
            opt.zero_grad()
            loss.backward()
            opt.step()
            final_loss = float(loss.item())

        elapsed = time.perf_counter() - start
        summary = self.traffic_encoder.parameter_summary()
        record = {'enabled': True, 'seconds': elapsed, 'params': summary['lora'], 'loss': final_loss}
        self.cost_records.append(record)
        print(f'LORA_ADAPT params={summary["lora"]} trainable={summary["trainable"]} '
              f'steps={args.lora_steps} sec={elapsed:.4f} loss={final_loss:.6f}')
        return lora_state, record

    def restore_lora(self, state):
        if state is not None:
            self.traffic_encoder.load_lora_state_dict(state)

    # ------------------------------------------------------------------
    # B0: pre_train (lines 451-485, preserved exactly)
    # ------------------------------------------------------------------
    def pre_train(self):
        self.memory.train()
        self.mgd.train()
        self.bin_predictor.train()
        self.mul_predictor.train()
        if self.traffic_encoder is not None:
            self.traffic_encoder.train()
        self.reset_episode_state()
        total_loss = 0.0
        n_batches = 0
        train_gen = tqdm.tqdm(self.train_loader, desc='Pretrain', disable=self.args.smoke_test)
        for batch in train_gen:
            batch = batch.to(self.device)
            self.optimizer.zero_grad()
            src, dst, t, msg, label, attack = batch.src, batch.dst, batch.t, batch.msg, batch.label, batch.attack
            n_id = torch.cat([src, dst]).unique()
            n_id, _, _ = self.neighbor_loader(n_id)
            self.assoc[n_id] = torch.arange(n_id.size(0), device=self.device)
            z, _ = self.memory(n_id)
            ed, _ = nodeMap(torch.stack((src, dst), dim=0))
            ed = ed.to(self.device)
            norm_factor, ed = cal_norm(ed, num_nodes=len(z), self_loop=False)
            z = self.mgd(z, ed, norm_factor).to(self.device)
            bin_out = self.bin_predictor(z[self.assoc[src]], z[self.assoc[dst]])
            mul_out = self.mul_predictor(z[self.assoc[src]], z[self.assoc[dst]])
            loss = self.criterion(bin_out, mul_out, label.long(), attack.long(), z)
            encoded = self.encode_msg(msg)
            if self.traffic_encoder is not None:
                encoded = encoded.detach()
            self.memory.update_state(src, dst, t, encoded)
            self.neighbor_loader.insert(src, dst)
            loss.backward()
            self.optimizer.step()
            self.memory.detach()
            total_loss += float(loss.item())
            n_batches += 1
            if self.args.smoke_test and n_batches >= 2:
                break
        return total_loss / max(n_batches, 1)

    # ------------------------------------------------------------------
    # run_episode: 17-step core pipeline (PPT Deck E)
    # ------------------------------------------------------------------
    def run_episode(self, pool, split, train=False, verbose=False, plot_suffix='', reset_state=True):
        args = self.args

        # B0: reset state per caller control (meta_train resets once; val/test reset each call)
        if reset_state:
            self.reset_episode_state()

        # B0: train/val/test split + episode sampling
        train_data, val_data, test_data = split_train_val_test(pool, self.classes)
        split_data = {'train': train_data, 'val': val_data, 'test': test_data}[split]
        support, query = sample_episode(split_data, self.classes, args.k_shot, args.q_query)
        support = support.to(self.device)
        query = query.to(self.device)
        true_sup = support.attack.cpu().tolist()

        # Step 3 [B6]: Save z_pre for Stable-LoRA constraint
        z_pre = None
        if train and args.use_stable_lora and self.traffic_encoder is not None:
            with torch.no_grad():
                z_pre = self.traffic_encoder(support.msg.float().to(self.device), normalize=True)

        # Step 4 [B2]: Online LoRA adaptation
        lora_state, lora_record = self.online_lora_adapt(support)

        # Steps 5-7: TGN pipeline (state reset handled by caller)
        self.semodel.train(train)
        self.mgd.train(train)
        if self.traffic_encoder is not None:
            self.traffic_encoder.train(train)
        if train:
            self.optimizer1.zero_grad()

        Epsilon = 0.3  # B0 constant

        with torch.set_grad_enabled(train):
            # Steps 6-7: Edge vectors for support and query
            support_vectors = self.edge_vectors(support)
            query_vectors = self.edge_vectors(query)

            # Encoded features (used by GRL/MMD/Stable/Adaptive)
            s_enc_norm = None
            q_enc_norm = None
            _need_enc = (self.traffic_encoder is not None and (
                args.use_grl_da or args.use_mmd_align or args.use_stable_lora or
                (args.use_cache_fusion and args.adaptive_cache_alpha)
            ))
            if _need_enc:
                s_enc_norm = self.traffic_encoder(support.msg.float().to(self.device), normalize=True)
                q_enc_norm = self.traffic_encoder(query.msg.float().to(self.device), normalize=True)

            # Step 8 [B4]: GRL domain-adversarial loss
            grl_loss_val = 0.0
            if train and args.use_grl_da and self.domain_discriminator is not None:
                if s_enc_norm is None:
                    s_enc_norm = self.traffic_encoder(support.msg.float().to(self.device), normalize=True)
                    q_enc_norm = self.traffic_encoder(query.msg.float().to(self.device), normalize=True)
                domain_logits = self.domain_discriminator(torch.cat([s_enc_norm, q_enc_norm], dim=0))
                domain_targets = torch.cat([
                    torch.zeros(s_enc_norm.size(0), device=self.device),
                    torch.ones(q_enc_norm.size(0), device=self.device),
                ])
                grl_loss_val = F.binary_cross_entropy_with_logits(domain_logits, domain_targets)

            # Step 9 [B5]: MMD support-query alignment
            mmd_val = 0.0
            if train and args.use_mmd_align and self.traffic_encoder is not None:
                if s_enc_norm is None:
                    s_enc_norm = self.traffic_encoder(support.msg.float().to(self.device), normalize=True)
                    q_enc_norm = self.traffic_encoder(query.msg.float().to(self.device), normalize=True)
                mmd_val = mmd_loss(s_enc_norm, q_enc_norm)

            # Step 10 [B6]: Stable-LoRA constraint MMD(z_pre, z_post)
            stable_lora_val = 0.0
            if train and args.use_stable_lora and z_pre is not None:
                z_post = s_enc_norm if s_enc_norm is not None else self.traffic_encoder(
                    support.msg.float().to(self.device), normalize=True)
                stable_lora_val = mmd_loss(z_pre, z_post)

            # Step 11: SelfExpr -> c, x2 (B0 logic)
            concatenated = torch.cat([support_vectors, query_vectors], dim=0)
            c, x2 = self.semodel(concatenated)
            # Convert to numpy for MFL (B0 API compatibility)
            C_np = c.cpu().detach().numpy()

            # Step 12: MFL + enhance_sim_matrix (B0 logic)
            L1 = MFL(x=x2, C=C_np, gamma=0.1, Eta=0.1, alpha=0.1)
            if L1 is None:
                L1 = np.zeros_like(C_np)
            else:
                L1 = L1.cpu().detach().numpy() if torch.is_tensor(L1) else L1
            C1 = C_np + Epsilon * L1
            L = enhance_sim_matrix(C1, self.class_meta_test, args.subspace_dim, 1)

            # Extract support-query submatrix
            num_sup = support.num_events
            mat = L[:num_sup, num_sup:]

            # Step 13 [B3]: Cache fusion
            cache_mat_np = None
            if args.use_cache_fusion:
                active_alpha = args.cache_alpha
                # [B8] Adaptive cache alpha from MMD
                if args.adaptive_cache_alpha and self.traffic_encoder is not None:
                    with torch.no_grad():
                        if s_enc_norm is not None:
                            eps_mmd = mmd_loss(s_enc_norm, q_enc_norm)
                        else:
                            s_enc_norm = self.traffic_encoder(support.msg.float().to(self.device), normalize=True)
                            q_enc_norm = self.traffic_encoder(query.msg.float().to(self.device), normalize=True)
                            eps_mmd = mmd_loss(s_enc_norm, q_enc_norm)
                        active_alpha = min(1.0, max(0.0, args.cache_alpha - eps_mmd.item()))
                # S_cache = cos_sim or RBF kernel
                cache_mat_np = cache_similarity_matrix(
                    self.traffic_encoder, support, query, self.device,
                    use_time_decay=args.cache_time_decay, tau=args.cache_tau,
                    use_rbf=args.use_rbf_cache, feature_weighter=self.feature_weighter,
                )
                # S_final = alpha * S_MFL + (1-alpha) * S_cache
                mat = active_alpha * mat + (1.0 - active_alpha) * cache_mat_np

            # Step 14: Class scores from similarity
            scores, preds = class_scores_from_similarity(
                mat, support.attack.detach(), self.classes, device=self.device)
            scores = scores.to(self.device)
            true_q = query.attack.long().detach().cpu().tolist()
            ce_target = query.attack.long().to(self.device)

            # Step 15: Total loss (B0: CE + reconstruction)
            loss = (F.cross_entropy(scores, ce_target) + torch.norm(x2 - concatenated)) * 0.01
            if train:
                if args.use_grl_da:
                    loss = loss + args.domain_loss_weight * grl_loss_val
                if args.use_mmd_align:
                    loss = loss + args.mmd_weight * mmd_val
                if args.use_stable_lora:
                    loss = loss + args.stable_lora_weight * stable_lora_val

            # Step 16: Backward
            if train:
                loss.backward()
                self.optimizer1.step()
            self.memory.detach()

        # Step 17 [B2]: Restore LoRA to pre-adaptation state
        self.restore_lora(lora_state)

        # ---- Metrics ----
        test_f1 = f1_score(true_q, preds, average='weighted')
        test_nmi = normalized_mutual_info_score(true_q, preds)
        precision, recall, _, _ = precision_recall_fscore_support(true_q, preds, average='weighted', zero_division=0)

        ndcg5 = 0.0
        if args.use_cache_fusion and cache_mat_np is not None:
            try:
                q_labels = query.attack.long().to(self.device)
                s_labels = support.attack.long().to(self.device)
                ndcg5 = ndcg_at_k(torch.as_tensor(cache_mat_np, device=self.device), s_labels, q_labels, k=args.ndcg_k)
            except Exception:
                ndcg5 = 0.0

        if verbose:
            print(f'{split.upper()} episode: f1={test_f1:.4f} nmi={test_nmi:.4f} '
                  f'precision={precision:.4f} recall={recall:.4f} loss={float(loss.item()):.6f}')

        # B0: t-SNE + heatmap
        if plot_suffix and not args.skip_plots and not args.smoke_test:
            labels = support.attack.detach().cpu().tolist() + true_q
            plot_artifacts(x2, L, labels, self.file_name, plot_suffix)

        return {
            'f1': float(test_f1),
            'nmi': float(test_nmi),
            'precision': float(precision),
            'recall': float(recall),
            'loss': float(loss.item()),
            'lora_seconds': float(lora_record['seconds']),
            'lora_params': int(lora_record['params']),
            'grl_loss': float(grl_loss_val) if not isinstance(grl_loss_val, float) else grl_loss_val,
            'mmd_loss': float(mmd_val.item()) if torch.is_tensor(mmd_val) else float(mmd_val),
            'stable_lora_loss': float(stable_lora_val.item()) if torch.is_tensor(stable_lora_val) else float(stable_lora_val),
            'ndcg_at_k': float(ndcg5),
            'trainable_params': int(trainable_parameter_count(self.traffic_encoder)),
        }

    # ------------------------------------------------------------------
    # meta_train: unified pipeline via run_episode (B0-B8)
    # B0 original: resets memory ONCE at start, accumulates across epochs.
    # ------------------------------------------------------------------
    def meta_train(self, verbose=True):
        self.semodel.reset()
        self.reset_episode_state()  # B0: reset once before epoch loop
        best_f1 = 0.0
        epochs = self.args.meta_epochs
        last_f1 = 0.0

        for epoch in range(epochs):
            result = self.run_episode(self.data1, 'train', train=True, verbose=False, reset_state=False)
            f1 = result['f1']
            nmi = result['nmi']
            loss = result['loss']

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}: F1 Score = {f1:.4f}, NMI Score = {nmi:.4f}, Loss = {loss:.4f}")
                logging.info(f"Epoch {epoch + 1}: F1 Score = {f1:.4f}, NMI Score = {nmi:.4f}, Loss = {loss:.4f}")

            if not self.args.smoke_test:
                self._save_checkpoint('last.pth')
                if f1 > best_f1:
                    best_f1 = f1
                    self._save_checkpoint('best.pth')
            last_f1 = f1

        return last_f1

    # ------------------------------------------------------------------
    # meta_val: unified pipeline via run_episode
    # ------------------------------------------------------------------
    def meta_val(self):
        self.reset_episode_state()  # Fresh state for validation
        result = self.run_episode(self.data1, 'val', train=False, reset_state=False)
        return result['f1']

    # ------------------------------------------------------------------
    # meta_test: unified pipeline via run_episode (+ visualization)
    # ------------------------------------------------------------------
    def meta_test(self, verbose=False, plot_suffix=''):
        self.reset_episode_state()  # Fresh state for testing
        result = self.run_episode(self.meta_test_pool, 'test', train=False, verbose=verbose,
                                  plot_suffix=plot_suffix, reset_state=False)
        return result['f1'], result['nmi'], result['precision'], result['recall']

    # ------------------------------------------------------------------
    # Checkpoint
    # ------------------------------------------------------------------
    def _save_checkpoint(self, name):
        if self.args.no_checkpoint:
            return
        ckpt = {
            'memory_state_dict': self.memory.state_dict(),
            'mgd_state_dict': self.mgd.state_dict(),
            'semodel_state_dict': self.semodel.state_dict(),
            'optimizer_state_dict': self.optimizer1.state_dict(),
            'args': vars(self.args),
        }
        if self.traffic_encoder is not None:
            ckpt['traffic_encoder_state_dict'] = self.traffic_encoder.state_dict()
        torch.save(ckpt, os.path.join(self.checkpoint_dir, name))

    def _load_checkpoint(self):
        if self.args.no_checkpoint or self.args.smoke_test:
            return False
        path = os.path.join(self.checkpoint_dir, 'best.pth')
        if not os.path.exists(path):
            return False
        try:
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)
            self.mgd.load_state_dict(checkpoint['mgd_state_dict'])
            semodel_state = checkpoint.get('semodel_state_dict')
            if semodel_state is not None:
                saved_w = semodel_state.get('weight', torch.empty(0))
                if saved_w.shape == self.semodel.state_dict()['weight'].shape:
                    self.semodel.load_state_dict(semodel_state)
                    self.optimizer1.load_state_dict(checkpoint['optimizer_state_dict'])
                    if self.traffic_encoder is not None and 'traffic_encoder_state_dict' in checkpoint:
                        self.traffic_encoder.load_state_dict(checkpoint['traffic_encoder_state_dict'], strict=False)
                    print('Loaded checkpoint from best.pth')
                    return True
                print('Skipped semodel load: shape mismatch.')
        except Exception as e:
            print(f'Checkpoint load failed: {e}')
        return False

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    def _cost_summary(self):
        if not self.cost_records:
            return {'lora_adapt_seconds_mean': 0.0, 'lora_adapt_seconds_total': 0.0, 'lora_params': 0}
        seconds = [r['seconds'] for r in self.cost_records]
        params = max(r['params'] for r in self.cost_records)
        return {
            'lora_adapt_seconds_mean': float(np.mean(seconds)),
            'lora_adapt_seconds_total': float(np.sum(seconds)),
            'lora_params': int(params),
        }

    def _write_outputs(self, summary):
        if self.args.output_json:
            os.makedirs(os.path.dirname(self.args.output_json) or '.', exist_ok=True)
            with open(self.args.output_json, 'w') as f:
                json.dump(summary, f, indent=2)
        if self.args.output_csv:
            os.makedirs(os.path.dirname(self.args.output_csv) or '.', exist_ok=True)
            exists = os.path.exists(self.args.output_csv)
            with open(self.args.output_csv, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
                if not exists:
                    writer.writeheader()
                writer.writerow(summary)

    def _summarize(self, results):
        def _ms(key):
            vals = [r[key] for r in results]
            return float(np.mean(vals)), float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        f1_m, f1_s = _ms('f1')
        nmi_m, nmi_s = _ms('nmi')
        p_m, p_s = _ms('precision')
        r_m, r_s = _ms('recall')
        summary = {
            'dataset_train': self.args.dataset_train, 'dataset_test': self.dataset_test,
            'way': self.args.way, 'k_shot': self.args.k_shot, 'q_query': self.args.q_query,
            'episodes': len(results),
            'foundation': self.args.use_foundation_encoder,
            'lora': self.args.use_lora_adapt, 'cache': self.args.use_cache_fusion,
            'cache_alpha': self.args.cache_alpha,
            'grl_da': self.args.use_grl_da, 'mmd_align': self.args.use_mmd_align,
            'stable_lora': self.args.use_stable_lora,
            'rbf_cache': self.args.use_rbf_cache, 'mha_weighting': self.args.use_mha_weighting,
            'adaptive_cache_alpha': self.args.adaptive_cache_alpha,
            'f1_mean': f1_m, 'f1_std': f1_s,
            'nmi_mean': nmi_m, 'nmi_std': nmi_s,
            'precision_mean': p_m, 'precision_std': p_s,
            'recall_mean': r_m, 'recall_std': r_s,
            **self._cost_summary(),
        }
        print(f'Average F1 Score: {f1_m:.4f} +/- {f1_s:.4f}')
        print(f'Average NMI: {nmi_m:.4f} +/- {nmi_s:.4f}')
        return summary

    # ------------------------------------------------------------------
    # run(): unified outer loop (B0-B8)
    # ------------------------------------------------------------------
    def run(self):
        args = self.args

        # Pretrain
        for epoch in range(args.pretrain_epochs):
            loss = self.pre_train()
            print(f'Epoch: {epoch:02d}, Loss: {loss:.4f}')
        print("Initializing...")

        # Smoke test shortcut
        if args.smoke_test:
            f1_train = self.meta_train(verbose=False)
            f1_val = self.meta_val()
            f1_test, nmi_test, prec_test, rec_test = self.meta_test(verbose=False)
            summary = self._summarize([{
                'f1': float(f1_test), 'nmi': float(nmi_test),
                'precision': float(prec_test), 'recall': float(rec_test),
                'lora_seconds': 0.0, 'lora_params': 0,
                'grl_loss': 0.0, 'mmd_loss': 0.0, 'stable_lora_loss': 0.0,
                'ndcg_at_k': 0.0, 'trainable_params': 0,
            }])
            self._write_outputs(summary)
            print('SMOKE_TEST_OK ' + json.dumps(summary, sort_keys=True))
            return summary

        # Checkpoint resume (only for eval-only mode: max_restarts=0 and not disabled)
        if not args.no_checkpoint and args.max_restarts == 0 and self._load_checkpoint():
            f1, nmi, precision, recall = self.meta_test(verbose=True, plot_suffix='end')
            print(f'Testing F1: {f1:.4f}, NMI: {nmi}')
            return None

        # Quality-triggered restart loop
        test_f1_scores = []
        restart_count = 0
        while args.max_restarts > 0:
            test_f1_scores.clear()
            for i in range(1):
                f1_train = self.meta_train(verbose=False)
                f1, nmi, _, _ = self.meta_test()
                test_f1_scores.append(f1)
                print("f1", f1)
            if min(test_f1_scores) < 0.8 or min(test_f1_scores) == 1:
                restart_count += 1
                if restart_count >= args.max_restarts:
                    print(f'Reached max_restarts={args.max_restarts}; continuing.')
                    break
                print('Restarting split (probe f1 too low or perfect).')
                self.data1, _ = filtered_data(self.data_all, self.class_meta_train)
                self.data = self.data1
                continue
            break

        # Main repetition loop
        f1_scores, nmi_scores, precision_scores, recall_scores = [], [], [], []
        for i in range(1, args.repetitions + 1):
            f1_train = self.meta_train()
            print(f'Training Repetition: {i:01d}, Training F1: {f1_train:.4f}')
            logging.info(f'Training Repetition: {i:01d}, Training F1: {f1_train:.4f}')

            f1_v = self.meta_val()
            print(f'Validation Repetition: {i:01d}, Validation F1: {f1_v:.4f}')
            logging.info(f'Validation Repetition: {i:01d}, Validation F1: {f1_v:.4f}')

            # plot_suffix triggers t-SNE + heatmap inside run_episode
            f1, nmi, precision, recall = self.meta_test(plot_suffix=str(i))
            f1_scores.append(f1)
            nmi_scores.append(nmi)
            precision_scores.append(precision)
            recall_scores.append(recall)
            print(f'Testing Repetition: {i:01d}, Testing F1: {f1:.4f}')
            logging.info(f'Testing Repetition: {i:01d}, Testing F1: {f1:.4f}')

        # Summary statistics
        avg_f1 = np.mean(f1_scores) if f1_scores else 0
        avg_nmi = np.mean(nmi_scores) if nmi_scores else 0
        avg_precision = np.mean(precision_scores) if precision_scores else 0
        avg_recall = np.mean(recall_scores) if recall_scores else 0
        std_f1 = np.std(f1_scores, ddof=1) if f1_scores else 0
        std_nmi = np.std(nmi_scores, ddof=1) if nmi_scores else 0
        std_precision = np.std(precision_scores, ddof=1) if precision_scores else 0
        std_recall = np.std(recall_scores, ddof=1) if recall_scores else 0

        print("F1 scores:", f1_scores)
        print("NMI scores:", nmi_scores)
        print(f'Average Precision: {avg_precision:.4f} +/- {std_precision:.4f}')
        print(f'Average Recall: {avg_recall:.4f} +/- {std_recall:.4f}')
        print(f'Average F1 Score: {avg_f1:.4f} +/- {std_f1:.4f}')
        print(f'Average NMI: {avg_nmi:.4f} +/- {std_nmi:.4f}')

        logging.info("F1 scores:")
        logging.info(f1_scores)
        logging.info("NMI scores:")
        logging.info(nmi_scores)
        logging.info(f'Average Precision: {avg_precision:.4f} +/- {std_precision:.4f}')
        logging.info(f'Average Recall: {avg_recall:.4f} +/- {std_recall:.4f}')
        logging.info(f'Average F1 Score: {avg_f1:.4f} +/- {std_f1:.4f}')
        logging.info(f'Average NMI: {avg_nmi:.4f} +/- {std_nmi:.4f}')

        summary = {
            'dataset_train': args.dataset_train, 'dataset_test': self.dataset_test,
            'way': args.way, 'k_shot': args.k_shot, 'q_query': args.q_query,
            'f1_mean': avg_f1, 'f1_std': std_f1,
            'nmi_mean': avg_nmi, 'nmi_std': std_nmi,
            'precision_mean': avg_precision, 'precision_std': std_precision,
            'recall_mean': avg_recall, 'recall_std': std_recall,
        }
        self._write_outputs(summary)
        print('RUN_METRICS_JSON ' + json.dumps(summary, sort_keys=True))
        return summary


# =========================================================================
if __name__ == '__main__':
    runner = DAFDIDSRunner(parse_args())
    runner.run()
