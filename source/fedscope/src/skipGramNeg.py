from torch import nn
import torch
import pandas as pd

class SkipGramNeg(nn.Module):
    def __init__(self, n_vocab, n_embed, word_to_ind=None, noise_dist=None):
        super().__init__()

        self.n_vocab = n_vocab
        self.n_embed = n_embed
        self.noise_dist = noise_dist

        self.in_embed = nn.Embedding(n_vocab, n_embed)
        self.out_embed = nn.Embedding(n_vocab, n_embed)

        # Initialize both embedding tables with uniform distribution
        self.in_embed.weight.data.uniform_(-1, 1)
        # self.out_embed.weight.data.uniform_(-1, 1)
        self.out_embed.weight.data.uniform_(0, 0)

        self.word_to_ind = word_to_ind
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_embeddings(self, ips, labels):
        ips_inds = [self.word_to_ind[ip] for ip in ips]
        embeddings = [self.in_embed.weight.data.cpu().numpy()[ind] for ind in ips_inds]
        embeddings = pd.DataFrame(embeddings, index=ips)
        embeddings = embeddings.reset_index() \
            .rename(columns={'index': 'ip'}) \
            .merge(labels, on='ip', how='left') \
            .set_index('ip')
        return embeddings

    def forward_input(self, input_words):
        input_vectors = self.in_embed(input_words)
        return input_vectors  # input vector embeddings

    def forward_target(self, output_words):
        output_vectors = self.out_embed(output_words)
        return output_vectors  # output vector embeddings

    def forward_noise(self, batch_size, n_samples=5):
        """ Generate noise vectors with shape (batch_size, n_samples, n_embed)"""
        # If no Noise Distribution specified, sample noise words uniformly from vocabulary
        if self.noise_dist is None:
            noise_dist = torch.ones(self.n_vocab)
        else:
            noise_dist = self.noise_dist

        # torch.multinomial :
        # Returns a tensor where each row contains (num_samples) **indices** sampled from 
        # multinomial probability distribution located in the corresponding row of tensor input.
        noise_words = torch.multinomial(input=noise_dist,  # input tensor containing probabilities
                                        num_samples=batch_size * n_samples,  # number of samples to draw
                                        replacement=True)
        noise_words = noise_words.to(self.device)

        # use context matrix for embedding noise samples
        noise_vectors = self.out_embed(noise_words).view(batch_size, n_samples, self.n_embed)

        return noise_vectors