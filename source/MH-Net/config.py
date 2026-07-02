'''
Training Configuration
'''

# subgraph
class Config:
    BATCH_SIZE = 102
    GRADIENT_ACCUMULATION = 5
    MAX_EPOCH = 20
    LR = 1e-2
    LR_MIN = 1e-4
    LABEL_SMOOTHING = 0
    WEIGHT_DECAY = 0
    WARM_UP = 0.1
    SEED = 32
    DROPOUT = 0.2
    DOWNSTREAM_DROPOUT = 0.0

    EMBEDDING_SIZE = 64
    H_FEATS = 128
    NUM_CLASSES = 14

    PMI_WINDOW_SIZE = 5
    PAD_TRUNC_DIGIT = 256
    FLOW_PAD_TRUNC_LENGTH = 50
    BYTE_PAD_TRUNC_LENGTH = 150
    HEADER_BYTE_PAD_TRUNC_LENGTH = 50
    ANOMALOUS_FLOW_THRESHOLD = 10000

'''
ISCX-VPN Dataset Configuration
'''
class ISCXVPNConfig(Config):
    TRAIN_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/train.npz'
    HEADER_TRAIN_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/header_train.npz'
    TEST_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/test.npz'
    HEADER_TEST_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/header_test.npz'
    TEST_DATA_FLOW = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/test_flow.npz'
    HEADER_TEST_DATA_FLOW = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/header_test_flow.npz'
    
    TRAIN_GRAPH_COMBINE = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_8bit/train_graph_combine.dgl'
    TEST_GRAPH_COMBINE = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_8bit/test_graph_combine.dgl'
    TRAIN_GRAPH_COMBINE_4bit = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_4bit/train_graph_combine.dgl'
    TEST_GRAPH_COMBINE_4bit = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_4bit/test_graph_combine.dgl'
    
    TRAIN_GRAPH_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/header_train_graph.dgl'
    TEST_GRAPH_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github/header_test_graph_flow.dgl'
    
    TRAIN_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/train.npz'
    HEADER_TRAIN_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/header_train.npz'
    TEST_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/test.npz'
    HEADER_TEST_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/header_test.npz'
    TEST_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/test_flow.npz'
    HEADER_TEST_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/header_test_flow.npz'
    
    TRAIN_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/header_train_graph.dgl'
    TEST_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx4bit_github/header_test_graph_flow.dgl'
    
    MIX_MODEL_CHECKPOINT= r'/data1/yhd/code/code/CLE-TFE/official_hetro/res_iscx_vpn/bit_and_normal_iscx_multimodal_Hetero_1_4_batch.pth'
    
    NUM_CLASSES = 6
    MAX_SEG_PER_CLASS = 9999
    NUM_WORKERS = 5

    BATCH_SIZE = 24
    GRADIENT_ACCUMULATION = 1
    MAX_EPOCH = 20
    LR = 1e-2
    LR_MIN = 1e-4
    LABEL_SMOOTHING = 0
    WEIGHT_DECAY = 0
    WARM_UP = 0.1
    SEED = 32
    DROPOUT = 0.0
    DOWNSTREAM_DROPOUT = 0.0
    EMBEDDING_SIZE = 64
    H_FEATS = 128

    DIR_PATH_DICT = {0: r'/data1/yhd/code/dataset/iscx_vpn/Chat',
                     1: r'/data1/yhd/code/dataset/iscx_vpn/Email',
                     2: r'/data1/yhd/code/dataset/iscx_vpn/File',
                     3: r'/data1/yhd/code/dataset/iscx_vpn/P2P',
                     4: r'/data1/yhd/code/dataset/iscx_vpn/Streaming',
                     5: r'/data1/yhd/code/dataset/iscx_vpn/VoIP',
                     }
    DIR_SAVE_DICT = {
                    0: r'/data1/yhd/code/dataset/iscx_vpn/Chat',
                    1: r'/data1/yhd/code/dataset/iscx_vpn/Email',
                    2: r'/data1/yhd/code/dataset/iscx_vpn/File',
                    3: r'/data1/yhd/code/dataset/iscx_vpn/P2P',
                    4: r'/data1/yhd/code/dataset/iscx_vpn/Streaming',
                    5: r'/data1/yhd/code/dataset/iscx_vpn/VoIP'
    }

'''
ISCX-NonVPN Dataset Configuration
'''
class ISCXNonVPNConfig(Config):
    TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/train.npz'
    HEADER_TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/header_train.npz'
    TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/test.npz'
    HEADER_TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/header_test.npz'
    TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/test_flow.npz'
    HEADER_TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/header_test_flow.npz'
    
    TRAIN_GRAPH_COMBINE = r'./res_iscx_nonvpn_4bit/train_graph_combine.dgl'
    TEST_GRAPH_COMBINE = r'./res_iscx_nonvpn_4bit/test_graph_combine.dgl'
    TRAIN_GRAPH_COMBINE_4bit = r'./res_iscx_nonvpn_4bit/train_graph_combine_4bit.dgl'
    TEST_GRAPH_COMBINE_4bit = r'./res_iscx_nonvpn_4bit/test_graph_combine_4bit.dgl'
    
    TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/header_train_graph.dgl'
    TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx-nonvpn/header_test_graph_flow.dgl'
    # TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_src_testMatch/header_test_graph_flow.dgl'
    
    TRAIN_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/train.npz'
    HEADER_TRAIN_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/header_train.npz'
    TEST_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/test.npz'
    HEADER_TEST_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/header_test.npz'
    TEST_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/test_flow.npz'
    HEADER_TEST_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/header_test_flow.npz'
    
    TRAIN_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/header_train_graph.dgl'
    TEST_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_iscx_nonvpn_4bit/header_test_graph_flow.dgl'
    
    MIX_MODEL_CHECKPOINT= r'./res_iscx_nonvpn_4bit/bit_and_normal_iscx_multimodal_Hetero.pth'

    NUM_CLASSES = 6
    MAX_SEG_PER_CLASS = 9999
    NUM_WORKERS = 5

    BATCH_SIZE = 102
    GRADIENT_ACCUMULATION = 5
    MAX_EPOCH = 40
    LR = 1e-2
    LR_MIN = 1e-5
    LABEL_SMOOTHING = 0.01
    WEIGHT_DECAY = 0
    WARM_UP = 0.1
    SEED = 32
    DROPOUT = 0.1
    DOWNSTREAM_DROPOUT = 0.15
    EMBEDDING_SIZE = 64
    H_FEATS = 128

    DIR_PATH_DICT = {0: r'/data1/yhd/code/CLE-TFE/TCP/Chat',
                     1: r'/data1/yhd/code/CLE-TFE/TCP/Email',
                     2: r'/data1/yhd/code/CLE-TFE/TCP/Streaming',
                     3: r'/data1/yhd/code/CLE-TFE/TCP/Video',
                     4: r'/data1/yhd/code/CLE-TFE/TCP/VoIP',
                     }
    DIR_SAVE_DICT = {
                     0: r'/data/data/yhd/code/CLE-TFE/ISCX_NONVPN_4bit/chat',
                     1: r'/data/data/yhd/code/CLE-TFE/ISCX_NONVPN_4bit/email',
                     2: r'/data/data/yhd/code/CLE-TFE/ISCX_NONVPN_4bit/streaming',
                     3: r'/data/data/yhd/code/CLE-TFE/ISCX_NONVPN_4bit/video',
                     4: r'/data/data/yhd/code/CLE-TFE/ISCX_NONVPN_4bit/voip',
                     }

'''
ISCX-Tor Dataset Configuration
'''

class ISCXTorConfig(Config):
    TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/train.npz'
    HEADER_TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/header_train.npz'
    TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/test.npz'
    HEADER_TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/header_test.npz'
    TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/test_flow.npz'
    HEADER_TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/header_test_flow.npz'
    
    TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/header_train_graph.dgl'
    TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_tor/header_test_graph_flow.dgl'
    # TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_src_testMatch/header_test_graph_flow.dgl'
    
    TRAIN_GRAPH_COMBINE = r'./res_ISCX_4bit_TOR/train_graph_combine.dgl'
    TEST_GRAPH_COMBINE = r'./res_ISCX_4bit_TOR/test_graph_combine.dgl'
    TRAIN_GRAPH_COMBINE_4bit = r'./res_ISCX_4bit_TOR/train_graph_combine_4bit.dgl'
    TEST_GRAPH_COMBINE_4bit = r'./res_ISCX_4bit_TOR/test_graph_combine_4bit.dgl'
    
    TRAIN_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/train.npz'
    HEADER_TRAIN_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/header_train.npz'
    TEST_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/test.npz'
    HEADER_TEST_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/header_test.npz'
    TEST_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/test_flow.npz'
    HEADER_TEST_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/header_test_flow.npz'
    
    TRAIN_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/header_train_graph.dgl'
    TEST_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_TOR/header_test_graph_flow.dgl'
    
    MIX_MODEL_CHECKPOINT= r'./res_ISCX_4bit_TOR/bit_and_normal_iscx_multimodal_Hetero.pth'
    
    NUM_CLASSES = 8
    MAX_SEG_PER_CLASS = 9999
    NUM_WORKERS = 1

    BATCH_SIZE = 32
    GRADIENT_ACCUMULATION = 1
    MAX_EPOCH = 20
    LR = 1e-2
    LR_MIN = 1e-4
    LABEL_SMOOTHING = 0
    WEIGHT_DECAY = 0
    WARM_UP = 0.1
    SEED = 32
    DROPOUT = 0.0
    DOWNSTREAM_DROPOUT = 0.0
    EMBEDDING_SIZE = 64
    H_FEATS = 128

    DIR_PATH_DICT = {0: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/Audio-streaming',
                     1: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/browsing',
                     2: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/chat',
                     3: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/file',
                     4: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/mail',
                     5: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/p2p',
                     6: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/video-streaming',
                     7: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/voip'
                     }

    DIR_SAVE_DICT = {0: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/Audio-streaming',
                     1: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/browsing',
                     2: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/chat',
                     3: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/file',
                     4: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/mail',
                     5: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/p2p',
                     6: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/video-streaming',
                     7: r'/data/data/yhd/code/TFE-GNN/ISCX-TOR/voip'
                     }


'''
ISCX-NonTor Dataset Configuration
'''
class ISCXNonTorConfig(Config):
    TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/train.npz'
    HEADER_TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/header_train.npz'
    TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/test.npz'
    HEADER_TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/header_test.npz'
    TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/test_flow.npz'
    HEADER_TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/header_test_flow.npz'
    
    TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/header_train_graph.dgl'
    TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_iscx_nontor/header_test_graph_flow.dgl'
    # TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_src_testMatch/header_test_graph_flow.dgl'
    
    TRAIN_GRAPH_COMBINE = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_4bit_nontor/train_graph_combine_4bit.dgl'
    TEST_GRAPH_COMBINE = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_4bit_nontor/test_graph_combine_4bit.dgl'
    TRAIN_GRAPH_COMBINE_4bit = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_4bit_nontor/train_graph_combine_4bit.dgl'
    TEST_GRAPH_COMBINE_4bit = r'/data1/yhd/code/code/CLE-TFE/res_ISCX_4bit_nontor/test_graph_combine_4bit.dgl'
    
    TRAIN_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/train.npz'
    HEADER_TRAIN_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/header_train.npz'
    TEST_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/test.npz'
    HEADER_TEST_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/header_test.npz'
    TEST_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/test_flow.npz'
    HEADER_TEST_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/header_test_flow.npz'
    
    TRAIN_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/header_train_graph.dgl'
    TEST_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW_4bit = r'/data1/yhd/code/code/CLE-TFE/res_iscx_github_nontor/header_test_graph_flow.dgl'
    
    MIX_MODEL_CHECKPOINT= r'./res_ISCX_4bit_nontor/bit_and_normal_iscx_multimodal_Hetero.pth'
    NUM_CLASSES = 8
    MAX_SEG_PER_CLASS = 9999
    NUM_WORKERS = 5

    BATCH_SIZE = 10
    GRADIENT_ACCUMULATION = 5
    MAX_EPOCH = 10
    LR = 1e-2
    LR_MIN = 1e-4
    LABEL_SMOOTHING = 0
    WEIGHT_DECAY = 0
    WARM_UP = 0.1
    SEED = 32
    DROPOUT = 0.2
    DOWNSTREAM_DROPOUT = 0.1
    EMBEDDING_SIZE = 64
    H_FEATS = 128

    DIR_PATH_DICT = {0: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/audio',
                     1: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/browsing',
                     2: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/chat',
                     3: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/email',
                     4: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/ftp',
                     5: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/p2p',
                     6: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/video',
                     7: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/voip',
                     }
    DIR_SAVE_DICT = {0: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/audio',
                     1: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/browsing',
                     2: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/chat',
                     3: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/email',
                     4: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/ftp',
                     5: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/p2p',
                     6: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/video',
                     7: r'/data/data/yhd/code/TFE-GNN/ISCX-NONTOR/voip',
                     }

class CICIoTConfig(Config):
    TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/train.npz'
    HEADER_TRAIN_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_train.npz'
    TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test.npz'
    HEADER_TEST_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test.npz'
    TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_flow.npz'
    HEADER_TEST_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_flow.npz'
    
    TRAIN_GRAPH_COMBINE = r'/data/data/yhd/code/CLE-TFE/res_ciciot/train_graph_combine.dgl'
    TEST_GRAPH_COMBINE = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_graph_combine.dgl'
    TRAIN_GRAPH_COMBINE_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/train_graph_combine.dgl'
    TEST_GRAPH_COMBINE_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_graph_combine.dgl'
    
    TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/train_graph.dgl'
    HEADER_TRAIN_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_train_graph.dgl'
    TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_graph.dgl'
    HEADER_TEST_GRAPH_DATA = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_graph.dgl'
    TEST_GRAPH_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_graph_flow.dgl'
    TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_graph_flow.dgl'
    # TEST_HEADER_DATA_FLOW = r'/data/data/yhd/code/CLE-TFE/res_src_testMatch/header_test_graph_flow.dgl'
    
    TRAIN_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/train_bit.npz'
    HEADER_TRAIN_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_train_bit.npz'
    TEST_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_bit.npz'
    HEADER_TEST_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_bit.npz'
    TEST_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_flow_bit.npz'
    HEADER_TEST_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_flow_bit.npz'
    
    TRAIN_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/train_graph_bit.dgl'
    HEADER_TRAIN_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_train_graph_bit.dgl'
    TEST_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_graph_bit.dgl'
    HEADER_TEST_GRAPH_DATA_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_graph_bit.dgl'
    TEST_GRAPH_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/test_graph_flow_bit.dgl'
    TEST_HEADER_DATA_FLOW_4bit = r'/data/data/yhd/code/CLE-TFE/res_ciciot/header_test_graph_flow_bit.dgl'
    
    TRAIN_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/train_bit10.npz'
    HEADER_TRAIN_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_train_bit10.npz'
    TEST_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_bit10.npz'
    HEADER_TEST_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_bit10.npz'
    TEST_DATA_FLOW_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_flow_bit10.npz'
    HEADER_TEST_DATA_FLOW_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_flow_bit6.npz'
    
    TRAIN_GRAPH_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/train_graph_bit10.dgl'
    HEADER_TRAIN_GRAPH_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_train_graph_bit10.dgl'
    TEST_GRAPH_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_graph_bit10.dgl'
    HEADER_TEST_GRAPH_DATA_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_graph_bit10.dgl'
    TEST_GRAPH_DATA_FLOW_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_graph_flow_bit10.dgl'
    TEST_HEADER_DATA_FLOW_10bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_graph_flow_bit10.dgl'
        
    TRAIN_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/train_bit10.npz'
    HEADER_TRAIN_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_train_bit10.npz'
    TEST_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_bit10.npz'
    HEADER_TEST_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_bit10.npz'
    TEST_DATA_FLOW_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_flow_bit10.npz'
    HEADER_TEST_DATA_FLOW_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_flow_bit6.npz'
    
    TRAIN_GRAPH_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/train_graph_bit10.dgl'
    HEADER_TRAIN_GRAPH_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_train_graph_bit10.dgl'
    TEST_GRAPH_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_graph_bit10.dgl'
    HEADER_TEST_GRAPH_DATA_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_graph_bit10.dgl'
    TEST_GRAPH_DATA_FLOW_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_graph_flow_bit10.dgl'
    TEST_HEADER_DATA_FLOW_2bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_graph_flow_bit10.dgl'
    
        
    TRAIN_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/train_bit6.npz'
    HEADER_TRAIN_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_train_bit6.npz'
    TEST_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_bit6.npz'
    HEADER_TEST_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_bit6.npz'
    TEST_DATA_FLOW_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_flow_bit6.npz'
    HEADER_TEST_DATA_FLOW_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_flow_bit6.npz'
    
    TRAIN_GRAPH_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/train_graph_bit6.dgl'
    HEADER_TRAIN_GRAPH_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_train_graph_bit6.dgl'
    TEST_GRAPH_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_graph_bit6.dgl'
    HEADER_TEST_GRAPH_DATA_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_graph_bit6.dgl'
    TEST_GRAPH_DATA_FLOW_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/test_graph_flow_bit6.dgl'
    TEST_HEADER_DATA_FLOW_6bit = r'/data/data/yhd/code/CLE-TFE/TCP/header_test_graph_flow_bit6.dgl'

    MIX_MODEL_CHECKPOINT= r'./checkpoints/bit_and_normal_iscx_multimodal_wo_.pth'
    NUM_CLASSES = 6
    MAX_SEG_PER_CLASS = 9999
    NUM_WORKERS = 1

    BATCH_SIZE = 24
    GRADIENT_ACCUMULATION = 1
    MAX_EPOCH = 10
    LR = 1e-2
    LR_MIN = 1e-4
    LABEL_SMOOTHING = 0
    WEIGHT_DECAY = 5e-4
    WARM_UP = 0.1
    SEED = 32
    DROPOUT = 0.0
    DOWNSTREAM_DROPOUT = 0.0
    EMBEDDING_SIZE = 64
    H_FEATS = 128

    DIR_PATH_DICT = {0: r'/data/data/yhd/code/CLE-TFE/TCP/Chat',
                     1: r'/data/data/yhd/code/CLE-TFE/TCP/Email',
                     2: r'/data/data/yhd/code/CLE-TFE/TCP/File',
                     3: r'/data/data/yhd/code/CLE-TFE/TCP/P2P',
                     4: r'/data/data/yhd/code/CLE-TFE/TCP/Streaming',
                     5: r'/data/data/yhd/code/CLE-TFE/TCP/VoIP',
                     }
    DIR_SAVE_DICT = {
                    0: r'/data/data/yhd/code/CLE-TFE/TCP_4bit/Chat',
                    1: r'/data/data/yhd/code/CLE-TFE/TCP_4bit/Email',
                    2: r'/data/data/yhd/code/CLE-TFE/TCP_4bit/File',
                    3: r'/data/data/yhd/code/CLE-TFE/TCP_4bit/P2P',
                    4: r'/data/data/yhd/code/CLE-TFE/TCP_4bit/Streaming',
                    5: r'/data/data/yhd/code/CLE-TFE/TCP_4bit/VoIP'
    }
if __name__ == '__main__':
    config = Config()
