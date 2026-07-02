from torch import nn
import torch

class NegativeSamplingLoss(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self,
                input_vectors,
                output_vectors,
                noise_vectors):
        batch_size, embed_size = input_vectors.shape

        input_vectors = input_vectors.view(batch_size, embed_size, 1)  # batch of column vectors
        output_vectors = output_vectors.view(batch_size, 1, embed_size)  # batch of row vectors

        # log-sigmoid loss for correct pairs
        out_loss = torch.bmm(output_vectors, input_vectors).sigmoid().log().squeeze()

        # log-sigmoid loss for incorrect pairs
        noise_loss = torch.bmm(noise_vectors.neg(), input_vectors).sigmoid().log()
        noise_loss = noise_loss.squeeze().sum(1)  # sum the losses over the sample of noise vectors

        return -(out_loss + noise_loss).mean()  # average batch loss