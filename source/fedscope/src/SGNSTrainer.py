from logging import INFO
import sys
from src.data_generation import ContextGenerator
import torch
import time
from torch import nn
import numpy as np

from flwr.common.logger import log
from logging import CRITICAL, DEBUG, ERROR, INFO, WARN

def convert_batch_of_words_to_inds(batch, word_to_ind):
            return np.array([(word_to_ind[x[0]], word_to_ind[x[1]]) for x in batch])
def convert_ns_table_to_inds_ns_table(batch, word_to_ind):
            return [(word_to_ind[x[0]], x[1],x[2]) for x in batch]
class SGNSTrainer:
   
    
    def __init__(self, pairs, model, ns_table, n_epochs, k, word_to_ind, batch_size,device, optimizer='adam'):
        super().__init__()
        
        self.model = model.to(device)
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.device = device
        self.pairs = convert_batch_of_words_to_inds(pairs,word_to_ind)
        self.k = k
        self.context_generator = ContextGenerator(ns_table=convert_ns_table_to_inds_ns_table(ns_table,word_to_ind=word_to_ind), k=self.k)
        self.word_to_ind = word_to_ind

        if optimizer == 'adam':
            self.optimizer = torch.optim.Adam(self.model.parameters())  #, lr=params['lr'])
        elif optimizer == 'sgd':
            self.optimizer = torch.optim.SGD(self.model.parameters())  #, lr=params['lr'])

        # We'll use a binary cross-entropy loss, since we have a binary classification problem:
        # distinguishing positive from negative contexts.
        self.loss = nn.BCEWithLogitsLoss()
        self.epoch = 0

   
    def train(self):
 
        batch_size = self.batch_size
        t0 = time.time()
        losses_list = []

        for epoch in range(self.n_epochs):
            log(DEBUG,f'Epoch {epoch + 1}.')
    
            ran_ind = np.random.randint(0, len(self.pairs), size=len(self.pairs))
            
            j = 0
            # constants for later verbosity
            loss_in_epoch = 0
            n_pairs_epoch = 0

            while (j + 1) * batch_size < len(self.pairs):
                # get a batch of examples

                index=ran_ind[(j * batch_size):((j + 1) * batch_size)]
                
                batch_of_examples = self.context_generator.create_batch(true_pairs=self.pairs[index])
                
                # convert from words to inds
                #batch_of_examples = convert_batch_of_words_to_inds(batch_of_examples, self.word_to_ind)

                targets = batch_of_examples[:, 0].astype(int)
                contexts = batch_of_examples[:, 1].astype(int)
                y = batch_of_examples[:, 2].astype(int)

                # convert to tensors
                targets = torch.as_tensor(targets).to(self.device)
                contexts = torch.as_tensor(contexts).to(self.device)
                y = torch.as_tensor(y).to(self.device)  # .unsqueeze(1)

                # update j
                j += 1

                # clear grads from optimizer
                self.optimizer.zero_grad()

                # Compute the output from the model.
                # That is, the dot products between target embeddings
                # and context embeddings.
                scores = self.model(targets, contexts).squeeze(1)
                loss = self.loss(scores, y.float())

                # Compute gradients and update the embeddings.
                loss.backward()
                self.optimizer.step()

                # We'll print some diagnostics periodically.
                loss_in_epoch += loss.item()
                n_pairs_epoch += (batch_size + 1) * self.k
                losses_list.append(loss.item())
                if ((j % 100) == 0):
                    log(DEBUG,f'iter {j}, loss {loss.item()}')
                    
            # Print diagnostics
            t1 = time.time()
            log(DEBUG,f'epoch: {epoch}, loss: {loss_in_epoch / n_pairs_epoch:.4f}, time: {t1 - t0:.2f}')
            t0 = time.time()
            # plt.plot(losses_list)
            # plt.title(f'Loss until the end of Epoch {epoch}')
            # plt.show()
            self.epoch += 1



            return loss_in_epoch/n_pairs_epoch