import torch
import torch.nn as nn
import torch.nn.functional as F

class ImageMeaningEncoder(nn.Module):
    def __init__(self, vector_dim=1024, output_dim=1024):
        super(ImageMeaningEncoder, self).__init__()
        
        # 1. Image Backbone (Simplified CNN)
        # Reduces 512x512 -> 16x16 through pooling and strides
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1), # 256
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1), # 128
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1), # 64
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1), # 32
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((8, 8)) # Fixed output size regardless of input
        )
        
        # 2. Vector Processor
        self.vector_fc = nn.Sequential(
            nn.Linear(vector_dim, 512),
            nn.ReLU()
        )
        
        # 3. Fusion Layers
        # (256 channels * 8 * 8) + 512 = 16896
        self.fusion = nn.Sequential(
            nn.Linear(256 * 8 * 8 + 512, 2048),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(2048, output_dim)
        )

    def forward(self, img, meaning_vec):
        x1 = self.features(img)
        x1 = torch.flatten(x1, 1) # Flatten image features
        
        x2 = self.vector_fc(meaning_vec) # Process input vector
        
        # Combine them
        combined = torch.cat((x1, x2), dim=1)
        output = self.fusion(combined)
        return output



