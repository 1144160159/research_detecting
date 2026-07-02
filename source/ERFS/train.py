import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
from time import time
import argparse
from sklearn import metrics
from attention import Attention
import psutil
import os
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
import os
from sklearn.preprocessing import label_binarize
import pickle

os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3'

#python home/Text-Level-GNN/train.py
import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


class GloveTokenizer:
    def __init__(self, filename, unk='<unk>', pad='<pad>'):
        self.filename = filename
        self.unk = unk
        self.pad = pad
        self.stoi = dict()
        self.itos = dict()
        self.embedding_matrix = list()
        with open(filename, 'r', encoding='utf8') as f: # Read tokenizer file
            for i, line in enumerate(f):
                values = line.split()
                self.stoi[values[0]] = i
                self.itos[i] = values[0]
                self.embedding_matrix.append([float(v) for v in values[1:]])
        if self.unk is not None: # Add unk token into the tokenizer
            i += 1
            self.stoi[self.unk] = i
            self.itos[i] = self.unk
            self.embedding_matrix.append(np.random.rand(len(self.embedding_matrix[0])))
        if self.pad is not None: # Add pad token into the tokenizer
            i += 1
            self.stoi[self.pad] = i
            self.itos[i] = self.pad
            self.embedding_matrix.append(np.zeros(len(self.embedding_matrix[0])))
        self.embedding_matrix = np.array(self.embedding_matrix).astype(np.float32) # Convert if from double to float for efficiency

    def encode(self, sentence):
        if type(sentence) == str:
            sentence = sentence.split(' ')
        elif len(sentence): # Convertible to list
            sentence = list(sentence)
        else:
            raise TypeError('sentence should be either a str or a list of str!')
        encoded_sentence = []
        for word in sentence:
            encoded_sentence.append(self.stoi.get(word, self.stoi[self.unk]))
        return encoded_sentence

    def decode(self, encoded_sentence):
        try:
            encoded_sentence = list(encoded_sentence)
        except Exception as e:
            print(e)
            raise TypeError('encoded_sentence should be either a str or a data type that is convertible to list type!')
        sentence = []
        for encoded_word in encoded_sentence:
            sentence.append(self.itos[encoded_word])
        return sentence

    def embedding(self, encoded_sentence):
        return self.embedding_matrix[np.array(encoded_sentence)]


class TextLevelGNNDataset(Dataset): # For instantiating train, validation and test dataset
    def __init__(self, node_sets, neighbor_sets, public_edge_mask, labels):
        super(TextLevelGNNDataset).__init__()
        self.node_sets = node_sets
        self.neighbor_sets = neighbor_sets
        self.public_edge_mask = public_edge_mask
        self.labels = labels

    def __getitem__(self, i):
        return torch.LongTensor(self.node_sets[i]), \
               torch.nn.utils.rnn.pad_sequence([torch.LongTensor(neighbor) for neighbor in self.neighbor_sets[i]], batch_first=True, padding_value=1), \
               self.public_edge_mask[torch.LongTensor(self.node_sets[i]).unsqueeze(-1).repeat(1, torch.nn.utils.rnn.pad_sequence([torch.LongTensor(neighbor) for neighbor in self.neighbor_sets[i]], batch_first=True, padding_value=1).shape[-1]), torch.nn.utils.rnn.pad_sequence([torch.LongTensor(neighbor) for neighbor in self.neighbor_sets[i]], batch_first=True, padding_value=1)], \
               torch.FloatTensor(self.labels[i])

    def __len__(self):
        return len(self.labels)


class TextLevelGNNDatasetClass: # This class is used to achieve parameters sharing among datasets
    def __init__(self, train_filename, test_filename, tokenizer, MAX_LENGTH=10, p=2, min_freq=2, train_validation_split=0.8):
        self.train_filename = 'home/Text-Level-GNN' + train_filename
        self.test_filename = 'home/Text-Level-GNN' + test_filename
        self.tokenizer = tokenizer
        self.MAX_LENGTH = MAX_LENGTH
        self.p = p
        self.min_freq = min_freq
        self.train_validation_split = train_validation_split

        self.train_data = pd.read_csv(self.train_filename, sep='\t', header=None)
        self.test_data = pd.read_csv(self.test_filename, sep='\t', header=None)

        self.stoi = {'<unk>': 0, '<pad>': 1} # Re-index
        self.itos = {0: '<unk>', 1: '<pad>'} # Re-index
        self.vocab_count = len(self.stoi)
        self.embedding_matrix = None
        self.label_dict = dict(zip(self.train_data[0].unique(), pd.get_dummies(self.train_data[0].unique()).values.tolist()))

        self.train_dataset, self.validation_dataset = random_split(self.train_data.to_numpy(), [int(len(self.train_data) * train_validation_split), len(self.train_data) - int(len(self.train_data) * train_validation_split)])
        self.test_dataset = self.test_data.to_numpy()

        self.build_vocab() # Based on train_dataset only. Updates self.stoi, self.itos, self.vocab_count and self.embedding_matrix

        self.train_dataset, self.validation_dataset, self.test_dataset, self.edge_stat, self.public_edge_mask = self.prepare_dataset()

    def build_vocab(self):
        vocab_list = [str(sentence).split(' ') for _, sentence in self.train_dataset]
        unique_vocab = []
        for vocab in vocab_list:
            unique_vocab.extend(vocab)
        unique_vocab = list(set(unique_vocab))
        for vocab in unique_vocab:
            if vocab in self.tokenizer.stoi.keys():
                self.stoi[vocab] = self.vocab_count
                self.itos[self.vocab_count] = vocab
                self.vocab_count += 1
        self.embedding_matrix = self.tokenizer.embedding(self.tokenizer.encode(list(self.stoi.keys())))

    def prepare_dataset(self): # will also build self.edge_stat and self.public_edge_mask
        # preparing self.train_dataset
        node_sets = [[self.stoi.get(vocab, 0) for vocab in str(sentence).strip().split(' ')][:self.MAX_LENGTH] for _, sentence in self.train_dataset]
        # Only retrieve the first MAX_LENGTH words in each document

        vocab_list = []
        vocab_all = []

        # sentence =  self.train_dataset[0]
        # vocab_all.append(sentence)
        # text = str(sentence).strip().split(' ')
        # for v in range(1,len(text)):
        #     node_sets2 = [self.stoi.get(text[v], 0)][:self.MAX_LENGTH]
        #     vocab_all.append([text[v], node_sets2])
        #import pudb;pu.db
        # vocab_all.append(sentence)
        # vocab_list.append(sentence)



        # for i in range(10):
        #     vocab_all.append(self.train_dataset[i])
        # # import pudb;pu.db
        # with open("home/Text-Level-GNN/vocab_list_4.txt", "w", encoding='latin1') as f:
        #     f.write(" ".join(str(a) for a in vocab_all))


        # f.write(" ".join(str(a.item()) for a in emb))


        # for _, sentence in self.train_dataset:
        #
        #     text = str(sentence).strip().split(' ')
        #     vocab_all.append(text)
        #     for v in range(len(text)):
        #         node_sets2 = [self.stoi.get(text[v], 0)][:self.MAX_LENGTH]
        #         # kcc = 0
        #         # if text[v] in vocab_list:
        #         #     kcc = 1
        #         # if kcc ==0:
        #         #     vocab_list.append(text[v])
        #         vocab_all.append([text[v], node_sets2])
        # # for b in vocab_all:
        # #     b = '%s' % b
        # # import pudb;pu.db
        #     with open("home/Text-Level-GNN/vocab_list.txt", "w",encoding='latin1') as f:
        #         f.write(" ".join('%s' % a for a in vocab_all))


        neighbor_sets = [create_neighbor_set(node_set, p=self.p) for node_set in node_sets]
        labels = [self.label_dict[label] for label, _ in self.train_dataset]
        #import pudb;pu.db
        # Construct edge statistics and public edge mask

        testa = []
        edge_stat, public_edge_mask = self.build_public_edge_mask(node_sets, neighbor_sets, min_freq=self.min_freq)

        numa=0
        for t in range(len(node_sets)):
            numa = numa+len(node_sets[t])
        testa.append(numa)
        testa.append(edge_stat.numel())
        public_edge_num = (public_edge_mask == True).sum()
        testa.append(public_edge_num)


        # with open("home/Text-Level-GNN/edge_4.txt", "w", encoding='latin1') as f:
        #     for o in testa:
        #         f.write(str(o) + '\n ')

        #
        # with open("home/Text-Level-GNN/edge_1.txt", "w", encoding='latin1') as f:
        #     f.write("   ".join(testa))


        train_dataset = TextLevelGNNDataset(node_sets, neighbor_sets, public_edge_mask, labels)

        # preparing self.validation_dataset
        node_sets = [[self.stoi.get(vocab, 0) for vocab in str(sentence).strip().split(' ')][:self.MAX_LENGTH] for _, sentence in self.validation_dataset] # Only retrieve the first MAX_LENGTH words in each document
        neighbor_sets = [create_neighbor_set(node_set, p=self.p) for node_set in node_sets]
        labels = [self.label_dict[label] for label, _ in self.validation_dataset]
        validation_dataset = TextLevelGNNDataset(node_sets, neighbor_sets, public_edge_mask, labels)

        # preparing self.test_dataset
        node_sets = [[self.stoi.get(vocab, 0) for vocab in str(sentence).strip().split(' ')][:self.MAX_LENGTH] for _, sentence in self.test_dataset] # Only retrieve the first MAX_LENGTH words in each document
        neighbor_sets = [create_neighbor_set(node_set, p=self.p) for node_set in node_sets]
        labels = [self.label_dict[label] for label, _ in self.test_dataset]
        test_dataset = TextLevelGNNDataset(node_sets, neighbor_sets, public_edge_mask, labels)

        return train_dataset, validation_dataset, test_dataset, edge_stat, public_edge_mask

    def build_public_edge_mask(self, node_sets, neighbor_sets, min_freq=2):
        edge_stat = torch.zeros(self.vocab_count, self.vocab_count)

        for node_set, neighbor_set in zip(node_sets, neighbor_sets):
            for neighbor in neighbor_set:
                for to_node in neighbor:
                    edge_stat[node_set, to_node] += 1
        public_edge_mask = edge_stat < min_freq # mark True at uncommon edges
        #import pudb;pu.db
        return edge_stat, public_edge_mask


def create_neighbor_set(node_set, p=2):
    if type(node_set[0]) != int:
        raise ValueError('node_set should be a 1D list!')
    if p < 0:
        raise ValueError('p should be an integer >= 0!')
    sequence_length = len(node_set)
    neighbor_set = []
    for i in range(sequence_length):
        neighbor = []
        for j in range(-p, p+1):
            if 0 <= i + j < sequence_length:
                neighbor.append(node_set[i+j])
        neighbor_set.append(neighbor)
    return neighbor_set


def pad_custom_sequence(sequences):
    '''
    To pad different sequences into a padded tensor for training. The main purpose of this function is to separate different sequence, pad them in different ways and return padded sequences.
    Input:
        sequences <list>: A sequence with a length of 4, representing the node sets sequence in index 0, neighbor sets sequence in index 1, public edge mask sequence in index 2 and label sequence in index 3.
                          And the length of each sequences are same as the batch size.
                          sequences: [node_sets_sequence, neighbor_sets_sequence, public_edge_mask_sequence, label_sequence]
    Return:
        node_sets_sequence <torch.LongTensor>: The padded node sets sequence (works with batch_size >= 1).
        neighbor_sets_sequence <torch.LongTensor>: The padded neighbor sets sequence (works with batch_size >= 1).
        public_edge_mask_sequence <torch.BoolTensor>: The padded public edge mask sequence (works with batch_size >= 1).
        label_sequence <torch.FloatTensor>: The padded label sequence (works with batch_size >= 1).
    '''
    node_sets_sequence = []
    neighbor_sets_sequence = []
    public_edge_mask_sequence = []
    label_sequence = []
    for node_sets, neighbor_sets, public_edge_mask, label in sequences:
        node_sets_sequence.append(node_sets)
        neighbor_sets_sequence.append(neighbor_sets)
        public_edge_mask_sequence.append(public_edge_mask)
        label_sequence.append(label)
    node_sets_sequence = torch.nn.utils.rnn.pad_sequence(node_sets_sequence, batch_first=True, padding_value=1)
    neighbor_sets_sequence, _ = padding_tensor(neighbor_sets_sequence)
    public_edge_mask_sequence, _ = padding_tensor(public_edge_mask_sequence)
    label_sequence = torch.nn.utils.rnn.pad_sequence(label_sequence, batch_first=True, padding_value=1)
    return node_sets_sequence, neighbor_sets_sequence, public_edge_mask_sequence, label_sequence


def padding_tensor(sequences, padding_idx=1):
    '''
    To pad tensor of different shape to be of the same shape, i.e. padding [tensor.rand(2, 3), tensor.rand(3, 5)] to a shape (2, 3, 5), where 0th dimension is batch_size, 1st and 2nd dimensions are padded.
    Input:
        sequences <list>: A list of tensors
        padding_idx <int>: The index that corresponds to the padding index
    Return:
        out_tensor <torch.tensor>: The padded tensor
        mask <torch.tensor>: A boolean torch tensor where 1 (represents '<pad>') are marked as true
    '''
    num = len(sequences)
    max_len_0 = max([s.shape[0] for s in sequences])
    max_len_1 = max([s.shape[1] for s in sequences])
    out_dims = (num, max_len_0, max_len_1)
    out_tensor = sequences[0].data.new(*out_dims).fill_(padding_idx)
    for i, tensor in enumerate(sequences):
        len_0 = tensor.size(0)
        len_1 = tensor.size(1)
        out_tensor[i, :len_0, :len_1] = tensor
    mask = out_tensor == padding_idx # Marking all places with padding_idx as mask
    return out_tensor, mask


class MessagePassing(nn.Module):
    def __init__(self, vertice_count, input_size, out_size, dropout_rate=0.02, padding_idx=1):
        super(MessagePassing, self).__init__()
        self.vertice_count = vertice_count # |V|
        self.input_size = input_size # d
        self.out_size = out_size # c
        self.dropout_rate = dropout_rate
        self.padding_idx = padding_idx
        self.information_rate = nn.Parameter(torch.rand(self.vertice_count, 1)) # (|V|, 1), which means it is a column vector
        
        self.att = Attention(input_size, input_size)
        self.linear = nn.Linear(self.input_size, self.out_size) # (d, c)
        self.dropout = nn.Dropout(self.dropout_rate)
        self.batchnorm = nn.BatchNorm1d(out_size)
        # self.ep = epoch

    def forward(self, node_sets, embedded_node, edge_weight, embedded_neighbor_node):
        # node_sets: (batch_size, l)
        # embedded_node: (batch_size, l, d)
        # edge_weight: (batch_size, max_sentence_length, max_neighbor_count)
        # embedded_neighbor_node: (batch_size, max_sentence_length, max_neighbor_count, d)

        tmp_tensor = (edge_weight.view(-1, 1) * embedded_neighbor_node.view(-1, self.input_size)).view(embedded_neighbor_node.shape) # (batch_size, max_sentence_length, max_neighbor_count, d)
        tmp_tensor = tmp_tensor.masked_fill(tmp_tensor == 0, -1e18) # (batch_size, max_sentence_length, max_neighbor_count, d), mask for M such that masked places are marked as -1e18
        tmp_tensor = self.dropout(tmp_tensor)
        M = tmp_tensor.max(dim=2)[0] # (batch_size, max_sentence_length, d), which is same shape as embedded_node (batch_size, l, d)
        information_rate = self.information_rate[node_sets] # (batch_size, l, 1)
        information_rate = information_rate.masked_fill((node_sets == self.padding_idx).unsqueeze(-1), 1) # (batch_size, l, 1), Fill the information rate of the padding index as 1, such that new e_n = (1-i_r) * M + i_r * e_n = (1-1) * 0 + 1 * e_n = e_n (no update)
        embedded_node = (1 - information_rate) * M + information_rate * embedded_node # (batch_size, l, d)

        #import pudb;pu.db
        embedded_node = self.att(embedded_node)
        emb_list = []
        for i in range(10):
            emb_list.append(embedded_node[0].sum(dim = 1))


        # " ".join(str(a.item()) for a in emb)
        # import pudb;pu.db
        sum_embedded_node = embedded_node.sum(dim=1) # (batch_size, d)

        sum_embedded_node = self.linear(sum_embedded_node)
        sum_embedded_node = self.batchnorm(sum_embedded_node)
        sum_embedded_node = F.relu(sum_embedded_node)

        x = sum_embedded_node
        # import pudb;pu.db
        # x = F.relu(self.batchnorm(self.linear(sum_embedded_node))) # (batch_size, c)
#         x = self.dropout(x) # if putting dropout with p=0.5 here, it is equivalent to wiping 4 choices out of 8 choices on the question sheet, which does not make sense. If a dropout layer is placed at here, it works the best when p=0 (disabled), followed by p=0.05, ..., p=0.5 (worst and does not even converge).
        y = F.softmax(x, dim=1) # (batch_size, c) along the c dimension
        return y,emb_list


class TextLevelGNN(nn.Module):
    def __init__(self, pretrained_embeddings, out_size=15, dropout_rate=0, padding_idx=1):
        super(TextLevelGNN, self).__init__()
        self.out_size = out_size # c
        self.padding_idx = padding_idx
        self.weight_matrix = nn.Parameter(torch.randn(pretrained_embeddings.shape[0], pretrained_embeddings.shape[0])) # (|V|, |V|)        
        self.embedding = nn.Embedding.from_pretrained(pretrained_embeddings, freeze=False, padding_idx=self.padding_idx) # (|V|, d)
        self.message_passing = MessagePassing(vertice_count=pretrained_embeddings.shape[0], input_size=pretrained_embeddings.shape[1], out_size=self.out_size, dropout_rate=dropout_rate, padding_idx=self.padding_idx) # input_size: (d,); out_size: (c,)
        self.public_edge_weight = nn.Parameter(torch.randn(1, 1)) # (1, 1)

    def forward(self, node_sets, neighbor_sets, public_edge_mask):
        # node_sets: (batch_size, l)
        # neighbor_sets: (batch_size, max_sentence_length, max_neighbor_count)
        # neighbor_sets_mask: (batch_size, max_sentence_length, max_neighbor_count) (no need)
        # public_edge_mask: (batch_size, max_sentence_length, max_neighbor_count)

        embedded_node = self.embedding(node_sets) # (batch_size, l, d)

        edge_weight = model.weight_matrix[node_sets.unsqueeze(2).repeat(1, 1, neighbor_sets.shape[-1]), neighbor_sets] # (batch_size, max_sentence_length, max_neighbor_count), neighbor_sets.shape[-1]: eg p=2, this expression=5; p=3, this expression=7. This is to first make node_sets to have same shape with neighbor_sets, then just do 1 query instead of 32*100 queries to speed up performance
        a = edge_weight * ~public_edge_mask # (batch_size, max_sentence_length, max_neighbor_count)
        b = self.public_edge_weight.unsqueeze(2).expand(1, public_edge_mask.shape[-2], public_edge_mask.shape[-1]) * public_edge_mask # (batch_size, max_sentence_length, max_neighbor_count)
        edge_weight = a + b # (batch_size, max_sentence_length, max_neighbor_count)
        embedded_neighbor_node = self.embedding(neighbor_sets) # (batch_size, max_sentece_length, max_neighbor_count, d)
        # import pudb;pu.db
        # Apply mask to edge_weight, to mask and cut-off any relationships to the padding nodes
        edge_weight = edge_weight.masked_fill((node_sets.unsqueeze(2).repeat(1, 1, neighbor_sets.shape[-1]) == self.padding_idx) | (neighbor_sets == self.padding_idx), 0) # (batch_size, max_sentence_length, max_neighbor_count)
        x, emb_list = self.message_passing(node_sets, embedded_node, edge_weight, embedded_neighbor_node) # (batch_size, c)
        return x,emb_list

#python home/Text-Level-GNN/train.py
parser = argparse.ArgumentParser()
parser.add_argument('--cuda', default='3', type=str, required=False,
                    help='Choosing which cuda to use')
parser.add_argument('--embedding_size', default=300, type=int, required=False,
                    help='Number of hidden units in each layer of the graph embedding part')
parser.add_argument('--p', default=3, type=int, required=False,
                    help='The window size')
parser.add_argument('--min_freq', default=2, type=int, required=False,
                    help='The minimum no. of occurrence for a word to be considered as a meaningful word. Words with less than this occurrence will be mapped to a globally shared embedding weight (to the <unk> token). It corresponds to the parameter k in the original paper.')
parser.add_argument('--max_length', default=70, type=int, required=False,
                    help='The max length of each document to be processed')
parser.add_argument('--dropout', default=0, type=float, required=False,
                    help='Dropout rate')
parser.add_argument('--lr', default=0.0005, type=float, required=False,
                    help='Initial learning rate')
parser.add_argument('--lr_decay_factor', default=0.9, type=float, required=False,
                    help='Multiplicative factor of learning rate decays')
parser.add_argument('--lr_decay_every', default=5, type=int, required=False,
                    help='Decaying learning rate every ? epochs')
parser.add_argument('--weight_decay', default=0.0001, type=float, required=False,
                    help='Weight decay (L2 penalty)')
parser.add_argument('--warm_up_epoch', default=0, type=int, required=False,
                    help='Pretraining for ? epochs before early stopping to be in effect')
parser.add_argument('--early_stopping_patience', default=10, type=int, required=False,
                    help='Waiting for ? more epochs after the best epoch to see any further improvements')
parser.add_argument('--early_stopping_criteria', default='loss', type=str, required=False,
                    choices=['accuracy', 'loss'],
                    help='Early stopping according to validation accuracy or validation loss')
parser.add_argument("--epoch", default=200, type=int, required=False,
                    help='Number of epochs to train')
args = parser.parse_args()

tokenizer = GloveTokenizer(f'home/Text-Level-GNN/embeddings/glove.6B.{args.embedding_size}d.txt')
dataset = TextLevelGNNDatasetClass(train_filename='/data/ids1217-train-all-terms.txt',
                                   test_filename='/data/ids1217-test-all-terms.txt',
                                   train_validation_split=0.8,
                                   tokenizer=tokenizer,
                                   p=args.p,
                                   min_freq=args.min_freq,
                                   MAX_LENGTH=args.max_length)
train_loader = DataLoader(dataset.train_dataset, batch_size=200, shuffle=True, collate_fn=pad_custom_sequence)
validation_loader = DataLoader(dataset.validation_dataset, batch_size=200, shuffle=True, collate_fn=pad_custom_sequence)
test_loader = DataLoader(dataset.test_dataset, batch_size=200, shuffle=True, collate_fn=pad_custom_sequence)

device = torch.device(f'cuda:{args.cuda}') if torch.cuda.is_available() else torch.device('cpu')
# import pudb;pu.db
model= TextLevelGNN(pretrained_embeddings=torch.tensor(dataset.embedding_matrix), dropout_rate=args.dropout).to(device)

criterion = nn.BCELoss()

lr = args.lr
lr_decay_factor = args.lr_decay_factor
lr_decay_every = args.lr_decay_every
weight_decay = args.weight_decay

warm_up_epoch = args.warm_up_epoch
early_stopping_patience = args.early_stopping_patience
early_stopping_criteria = args.early_stopping_criteria
best_epoch = 0 # Initialize

training = {}
validation = {}
testing = {}
training['accuracy'] = []
training['loss'] = []
validation['accuracy'] = []
validation['loss'] = []
testing['accuracy'] = []
testing['loss'] = []

for epoch in range(args.epoch):
    model.train()
    train_loss = 0
    train_correct_items = 0
    previous_epoch_timestamp = time()

    if epoch % lr_decay_every == 0: # Update optimizer for every lr_decay_every epochs
        if epoch != 0: # When it is the first epoch, disable the lr_decay_factor
            lr *= lr_decay_factor
        optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    for i, (node_sets, neighbor_sets, public_edge_masks, labels) in enumerate(train_loader):
#         print('Finished batch:', i)
        node_sets = node_sets.to(device)
        neighbor_sets = neighbor_sets.to(device)
        public_edge_masks = public_edge_masks.to(device)
        labels1 = labels.to(device)
        prediction,embed = model(node_sets, neighbor_sets, public_edge_masks)
        # if epoch == 50:
        #
        #     with open("home/Text-Level-GNN/emb_list_4.txt", "w", encoding='latin1') as f:
        #         f.write(" ".join(str(a) for a in embed))


            # with open("home/Text-Level-GNN/emb_list_3.txt", "w", encoding='latin1') as f:
            #     f.write(" ".join(str(a.item()) for a in embed))
        # import pudb;pu.db
        # " ".join(str(a.item()) for a in prediction[1]

        loss = criterion(prediction, labels1).to(device)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        train_correct_items += (prediction.argmax(dim=1) == labels1.argmax(dim=1)).sum().item()
    train_accuracy = train_correct_items / len(dataset.train_dataset)
    #import pudb;pu.db
    model.eval()
    with torch.no_grad():
        validation_loss = 0
        validation_correct_items = 0
        for i, (node_sets, neighbor_sets, public_edge_masks, labels) in enumerate(validation_loader):
            node_sets = node_sets.to(device)
            neighbor_sets = neighbor_sets.to(device)
            public_edge_masks = public_edge_masks.to(device)
            labels1 = labels.to(device)
            prediction,emb1= model(node_sets, neighbor_sets, public_edge_masks)
            loss = criterion(prediction, labels1).to(device)
            validation_loss += loss.item()
            validation_correct_items += (prediction.argmax(dim=1) == labels1.argmax(dim=1)).sum().item()
        validation_accuracy = validation_correct_items / len(dataset.validation_dataset)

#     model.eval()
        test_loss = 0
        test_correct_items = 0


        label_all = []
        pred_all = []
        predictions = []
        for i, (node_sets, neighbor_sets, public_edge_masks, labels) in enumerate(test_loader):
            node_sets = node_sets.to(device)
            neighbor_sets = neighbor_sets.to(device)
            public_edge_masks = public_edge_masks.to(device)
            labels1 = labels.to(device)
            prediction ,emb2= model(node_sets, neighbor_sets, public_edge_masks)
            loss = criterion(prediction, labels1).to(device)
            test_loss += loss.item()
            test_correct_items += (prediction.argmax(dim=1) == labels1.argmax(dim=1)).sum().item()
            predictions.append(prediction)
            label_all.append(labels1.argmax(dim=1))
            pred_all.append(prediction.argmax(dim=1))

    #import pudb;pu.db
    test_accuracy = test_correct_items / len(dataset.test_dataset)
    print(f'Epoch: {epoch+1}, Training Loss: {train_loss:.4f}, Validation Loss: {validation_loss:.4f}, Testing Loss: {test_loss:.4f}, Training Accuracy: {train_accuracy:.4f}, Validation Accuracy: {validation_accuracy:.4f}, Testing Accuracy: {test_accuracy:.4f}, Time Used: {time()-previous_epoch_timestamp:.2f}s')
    training['accuracy'].append(train_accuracy)
    training['loss'].append(train_loss)
    validation['accuracy'].append(validation_accuracy)
    validation['loss'].append(validation_loss)
    testing['accuracy'].append(test_accuracy)
    testing['loss'].append(test_loss)

    # add warmup mechanism for warm_up_epoch epochs
    # if epoch >= warm_up_epoch:
    #     best_epoch = warm_up_epoch
    #     # early stopping
    #     if early_stopping_criteria == 'accuracy':
    #         if validation['accuracy'][epoch] > validation['accuracy'][best_epoch]:
    #             best_epoch = epoch
    #         elif epoch >= best_epoch + early_stopping_patience:
    #             print(f'Early stopping... (No further increase in validation accuracy) for consecutive {early_stopping_patience} epochs.')
    #             break
    #     if early_stopping_criteria == 'loss':
    #         if validation['loss'][epoch] < validation['loss'][best_epoch]:
    #             best_epoch = epoch
    #         elif epoch >= best_epoch + early_stopping_patience:
    #             print(f'Early stopping... (No further decrease in validation loss) for consecutive {early_stopping_patience} epochs.')
    #             break
    # elif epoch + 1 == warm_up_epoch:
    #     print('--- Warm up finished ---')

df = pd.concat([pd.DataFrame(training), pd.DataFrame(validation), pd.DataFrame(testing)], axis=1)
df.columns = ['Training Accuracy', 'Training Loss', 'Validation Accuracy', 'Validation Loss', 'Testing Accuracy', 'Testing Loss']
df.to_csv(f'embedding_size={args.embedding_size},p={args.p},min_freq={args.min_freq},max_length={args.max_length},dropout={args.dropout},lr={args.lr},lr_decay_factor={args.lr_decay_factor},lr_decay_every={args.lr_decay_every},weight_decay={args.weight_decay},warm_up_epoch={args.warm_up_epoch},early_stopping_patience={args.early_stopping_patience},early_stopping_criteria={args.early_stopping_criteria},epoch={args.epoch}.csv') # Logging

# torch.save(model, 'home/Text-Level-GNN/model_ddos2019_700.pkl')
# pickle.dump(model, file=open('home/Text-Level-GNN/model_DDoS2019.pkl', 'wb+'))

# label = labels1.argmax(dim=1).tolist()
# pred = prediction.argmax(dim=1).tolist()

# label_new=[]
# for i in range(len(label)):
#     for j in range(len(label[i])):
#         if label[i][j] == 1.0:
#             label_new.append(j)
pred_new=[]
label_new=[]
for i in range(len(label_all)):
    for j in range(len(label_all[i])):
        label_new.append(label_all[i][j])

for n in range(len(pred_all)):
    for s in range(len(pred_all[n])):
        pred_new.append(pred_all[n][s])
#import pudb;pu.db
# for n in range(len(pred)):
#     for s in range(len(pred[n])):
#         if pred[n][s] == 1.0:
#             pred_new.append(s)

prediction_all=[]
for p in range(len(predictions)):
    prediction_all.append(predictions[p])


a = np.array(label_new,dtype=np.float32)
b = np.array(pred_new,dtype=np.float32)

# import pudb;pu.db

print("Test Precision, Recall and F1-Score...")
print(metrics.classification_report(a, b, digits=4))
print("Macro average Test Precision, Recall and F1-Score...")
print(metrics.precision_recall_fscore_support(a, b, average='macro'))
print("Micro average Test Precision, Recall and F1-Score...")
print(metrics.precision_recall_fscore_support(a, b, average='micro'))

print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024) )

# y_test_bin = label_binarize(a, classes=np.arange(11))
#
# # 绘制每个类别的 ROC 曲线
# plt.figure()
# colors = ['r', 'g', 'b', 'c', 'm','k','#FAEBD7','#00FFFF','#7FFFD4','#F5F5DC','#FFEBCD']
# for i in range(11):
#     fpr, tpr, _ = roc_curve(y_test_bin[:, i], predictions_all[:, i])
#     roc_auc = auc(fpr, tpr)
#     plt.plot(fpr, tpr, color=colors[i], lw=2, label='Class {0} (AUC = {1:.2f})'.format(i, roc_auc))
#
# plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
# plt.xlim([0.0, 1.0])
# plt.ylim([0.0, 1.05])
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive Rate')
# plt.title('ROC curve')
# plt.legend(loc='best')
# plt.savefig("./ROC.png")
# plt.show()

# fpr, tpr, thresholds_keras = roc_curve(a, b)
# AUC = auc(fpr, tpr)
# plt.figure()
# plt.plot([0, 1], [0, 1], 'k--')
# plt.plot(fpr, tpr, label='ROC curve (area = {:.3f})'.format(AUC))
# plt.xlabel('False positive rate')
# plt.ylabel('True positive rate')
# plt.title('ROC curve')
# plt.legend(loc='best')
# plt.savefig("./ROC.png")
# plt.show()



# matrix = confusion_matrix(a, b)



# classes = ['Benign', 'Botnet', 'BruteForce', 'DDoS', 'FTP', 'GoldenEye','Heartbleed','Hulk','Infiltrating','PortScan','Slowhttp','Slowloris','SqlInjection','SSH','XSS']
# plot_Matrix(matrix, classes, title='CIC IDS2017')

# classes = ['slowread', 'slowloris', 'slowheaders', 'slowbody', 'rudy', 'Hulk','goldeneye','ddossim']
# plot_Matrix(matrix, classes, title='CIC DOS2017')

# classes = ['LDAP', 'MSSQL', 'NetBIOS', 'PortMap', 'SYN', 'UDP','UDP-Lag']
# plot_Matrix(matrix, classes, title='CIC DDoS2019')

# classes = ['Zeus', 'Virut', 'Tinba', 'Shifu', 'Nsis-ay', 'Neris','Miuref','Htbot','Geodo','Cridex','Benign']
# plot_Matrix(matrix, classes, title='USTC TFC2016')

# classes = ['Chat', 'Email', 'FileTransfer', 'P2P', 'Streaming', 'VoIP']
# plot_Matrix(matrix, classes, title='ISCX VPN-nonVPN')

# info = psutil.virtual_memory()
# print(u'内存使用：',psutil.Process(os.getpid()).memory_info().rss)
# print(u'总内存：',info.total)


# import matplotlib.pyplot as plt

# plt.plot(training['loss'], label='Training Loss')
# plt.plot(validation['loss'], label='Validation Loss')
# plt.plot(testing['loss'], label='Testing Loss')
# plt.legend()
# plt.xlabel('Epoch')
# plt.ylabel('Loss')
# plt.show()

# plt.plot(training['accuracy'], label='Training Accuracy')
# plt.plot(validation['accuracy'], label='Validation Accuracy')
# plt.plot(testing['accuracy'], label='Testing Accuracy')
# plt.legend()
# plt.xlabel('Epoch')
# plt.ylabel('Accuracy')
# plt.show()