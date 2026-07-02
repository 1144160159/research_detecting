from torch import nn
import torch
import pandas as pd


class Word2VecTorch(nn.Module):
    def __init__(self, vocab_size, word_to_ind, embedding_dim=50):
        super().__init__()

        # the word-to-index dictionary
        self.word_to_ind = word_to_ind
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        # | input_layer | u | embedding_layer | v | output_layer | 
        self.u_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.v_embedding = nn.Embedding(vocab_size, embedding_dim)
        

        self.log_sigmoid = nn.LogSigmoid()
        
        # Initialize the weights randomly
        self.init_range =  0.5 / embedding_dim
        
        
        self.u_embedding.weight.data.uniform_(-self.init_range, self.init_range)
        self.v_embedding.weight.data.uniform_(-0, 0)
       

    def get_embeddings(self, ips, labels):
        #print(self.word_to_ind)
        
        #EDITED TO SUPPORT IPS THAT ARE FILTERED OUT 
        ips = [ ip for ip in ips if ip in self.word_to_ind.keys()]
        
        
        ips_inds = [torch.tensor(self.word_to_ind[ip]).cpu() for ip in ips]
        embeddings = [self.u_embedding.weight.data.cpu().numpy()[ind] for ind in ips_inds]
        embeddings = pd.DataFrame(embeddings, index=ips)
        embeddings = embeddings.reset_index() \
            .rename(columns={'index': 'ip'}) \
            .merge(labels, on='ip', how='left') \
            .set_index('ip')
        return embeddings

    def forward(self, targets, contexts):  # target, context,neg
        # batch looks like the following:
        #   array([[a,b,1],
        #          [c,d,1],
        #          [c,m,0],
        #          [c,g,0]])
        # Look up the embeddings for the target words.
        # shape: (batch size, embedding dimension)

        tagets_embeddings = self.u_embedding(targets)
        n_batch, _ = tagets_embeddings.shape
        # View this as a 3-dimensional tensor, with
        # shape (batch size, 1, embedding dimension)
        tagets_embeddings = tagets_embeddings.view(n_batch, 1, self.embedding_dim)
        # Look up the embeddings for the positive and negative context words.
        # shape: (batch size, nbr contexts, emb dim)
        context_embeddings = self.v_embedding(contexts)
        # Transpose the tensor for matrix multiplication
        # shape: (batch size, emb dim, nbr contexts)
        context_embeddings = context_embeddings.view(n_batch, 1, self.embedding_dim)
        context_embeddings = context_embeddings.transpose(1, 2)
        # Compute the dot products between target word embeddings and context
        # embeddings. We express this as a batch matrix multiplication (bmm).
        # shape: (batch size, 1, nbr contexts)
        dots = tagets_embeddings.bmm(context_embeddings)
        # View this result as a 2-dimensional tensor.
        # shape: (batch size, nbr contexts)
        dots = dots.view(n_batch, 1)
        return dots


    def update(self, new_vocab_size, new_word_to_ind):
        """
        Update the model with the new vocab and word_to_ind
        """
        # create a new_u_embedding layer and assign the new weights 
        # by concatenating the old weights with a new random vector new_vocab_size*embedding_dim
       
        
        new_u_embedding = nn.Embedding(new_vocab_size, self.embedding_dim)
        new_u_embedding.weight = nn.Parameter(torch.cat((self.u_embedding.weight.data,
                                                         torch.nn.init.uniform_(
                                                             torch.empty(new_vocab_size - self.vocab_size, self.embedding_dim),
                                                             a=-self.init_range,
                                                             b=self.init_range).to(self.u_embedding.weight.device))))
        self.u_embedding = new_u_embedding

        # create a new_v_embedding layer and assign the new weights 
        # by concatenating the old weights with a new random vector new_vocab_size*embedding_dim
        new_v_embedding = nn.Embedding(new_vocab_size, self.embedding_dim)
        new_v_embedding.weight = nn.Parameter(torch.cat((self.v_embedding.weight.data,
                                                         torch.nn.init.uniform_(
                                                             torch.empty(new_vocab_size - self.vocab_size, self.embedding_dim),
                                                             a=-0,
                                                             b=0).to(self.u_embedding.weight.device))))
        self.v_embedding = new_v_embedding

        # update the vocab size
        self.vocab_size = new_vocab_size
        # update the word_to_ind
        self.word_to_ind = new_word_to_ind
        

                
                
    def update_with_removal(self, new_vocab_size: int, new_word_to_ind: dict[int,str]):
       
        # Initialize new embedding layers
        new_u_embedding = nn.Embedding(new_vocab_size, self.embedding_dim)
        old_u_parameters = nn.ParameterList([nn.Parameter(row.unsqueeze(0)) for row in self.u_embedding.weight.data])
        new_u_parameters = []

        new_v_embedding = nn.Embedding(new_vocab_size, self.embedding_dim)
        old_v_parameters = nn.ParameterList([nn.Parameter(row.unsqueeze(0)) for row in self.v_embedding.weight.data])
        new_v_parameters = []

        # Populate new parameters
        #print(self.word_to_ind)
        #print("\n\n\n\n")
        #print(new_word_to_ind)
        for ip_new, index_new in new_word_to_ind.items():
            
            
            # FIRST CASE -> IP IN THE SAME POSITION
            if ip_new in self.word_to_ind and self.word_to_ind[ip_new] == index_new:
                new_u_parameters.append(old_u_parameters[self.word_to_ind[ip_new]].data)
                new_v_parameters.append(old_v_parameters[self.word_to_ind[ip_new]].data)

            # SECOND CASE -> IP IN A DIFFERENT POSITION
            elif ip_new in self.word_to_ind and self.word_to_ind[ip_new] != index_new:
                new_u_parameters.append(old_u_parameters[self.word_to_ind[ip_new]].data)
                new_v_parameters.append(old_v_parameters[self.word_to_ind[ip_new]].data)

            # THIRD CASE -> IP NOT PRESENT IN THE PREVIOUS
            else:
                new_u_param = torch.empty(1, self.embedding_dim).uniform_(-self.init_range, self.init_range).to(self.u_embedding.weight.device)
                new_u_parameters.append(new_u_param)

                new_v_param = torch.empty(1, self.embedding_dim).uniform_(-self.init_range, self.init_range).to(self.v_embedding.weight.device)
                new_v_parameters.append(new_v_param)

        # Ensure the tensors are properly concatenated into a 2D tensor
        new_u_weight = torch.cat(new_u_parameters, dim=0)  # Shape: [new_vocab_size, embedding_dim]
        new_v_weight = torch.cat(new_v_parameters, dim=0)  # Shape: [new_vocab_size, embedding_dim]

        # Assign the weights to the new embeddings
        new_u_embedding.weight = nn.Parameter(new_u_weight)
        new_v_embedding.weight = nn.Parameter(new_v_weight)

        # Update embeddings
        self.u_embedding = new_u_embedding
        self.v_embedding = new_v_embedding
        
        # update the vocab size
        self.vocab_size = new_vocab_size
        # update the word_to_ind
        self.word_to_ind = new_word_to_ind

        