import torch
import torch.nn as nn
import math


class SimpleTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=512, nhead=8, num_layers=6, max_seq_len=1024):
        super().__init__()
        self.d_model = d_model
        
        # 1. Embedding & Positional Encoding
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(1, max_seq_len, d_model))
        
        # 2. Transformer Encoder (Standard Decoder-only style for GPT-like tasks)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=d_model*4, 
            batch_first=True, dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # 3. Output Head
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        # x shape: (batch_size, seq_len)
        seq_len = x.size(1)
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = x + self.pos_encoder[:, :seq_len, :]
        
        # Causal mask for autoregressive generation
        mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(x.device)
        
        output = self.transformer(x, mask=mask, is_causal=True)
        return self.fc_out(output)
