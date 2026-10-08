import torch
import torch.nn as nn
import torch.nn.functional as F

LATENT_DIM = 128
TOKEN_DIM = 16
NUM_TOKENS = 8
EOS_THRESHOLD = 0.5


class BaseEncoder(nn.Module):
    """
    CNN + Linear layers mapping a 128x128 image to an initial latent vector.
    Input:  (B, 3, 128, 128)
    Output: (B, LATENT_DIM)
    """

    def __init__(self, latent_dim: int = LATENT_DIM):
        super().__init__()
        self.conv = nn.Sequential(
            # 128x128 -> 64x64
            nn.Conv2d(3, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2, inplace=True),
            # 64x64 -> 32x32
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),
            # 32x32 -> 16x16
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            # 16x16 -> 8x8
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            # 8x8 -> 4x4
            nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, latent_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv(x)
        x = self.fc(x)
        return x


class SubtractTokenModule(nn.Module):
    """
    Sub-network connected in a sequential dependency chain:
      1. token    = token_head(vector)
      2. residual = residual_head(vector, token)
      3. eos      = eos_head(token, residual)
    """

    def __init__(self, latent_dim: int = LATENT_DIM, token_dim: int = TOKEN_DIM):
        super().__init__()

        # Step 1: Predict token directly from current latent vector
        self.token_head = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, token_dim),
        )

        # Step 2: Predict residual vector conditioned on input vector AND extracted token
        self.residual_mlp = nn.Sequential(
            nn.Linear(latent_dim + token_dim, latent_dim),
            nn.ReLU(inplace=True),
            nn.Linear(latent_dim, latent_dim),
        )

        # Step 3: Predict End-Of-Sequence probability based on extracted token AND resulting residual
        self.eos_head = nn.Sequential(
            nn.Linear(token_dim + latent_dim, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, vector: torch.Tensor):
        # 1. Extract token
        token = self.token_head(vector)

        # 2. Compute remaining residual
        combined_token = torch.cat([vector, token], dim=-1)
        residual = self.residual_mlp(combined_token)

        # 3. Estimate EOS probability
        combined_eos = torch.cat([token, residual], dim=-1)
        eos = self.eos_head(combined_eos)

        return token, eos, residual


class RecursiveTokenizer(nn.Module):
    """
    Recursively extracts tokens from the initial latent vector.
    """

    def __init__(
        self,
        latent_dim: int = LATENT_DIM,
        token_dim: int = TOKEN_DIM,
        max_tokens: int = NUM_TOKENS,
        eos_threshold: float = EOS_THRESHOLD,
    ):
        super().__init__()
        self.max_tokens = max_tokens
        self.eos_threshold = eos_threshold
        self.sub_token = SubtractTokenModule(latent_dim, token_dim)

    def forward(self, latent_vector: torch.Tensor):
        remainder = latent_vector
        tokens = []
        eos_probs = []

        for _ in range(self.max_tokens):
            t, eos, r = self.sub_token(remainder)
            tokens.append(t)
            eos_probs.append(eos)
            remainder = r

            # Ignore EOS for now
            # if not self.training and latent_vector.size(0) == 1:
            #     if eos.item() > self.eos_threshold:
            #         break

        return tokens, eos_probs


class Decoder(nn.Module):
    """
    Decodes a single token into a partial image.
    Input:  (B, TOKEN_DIM)
    Output: Partial Image (B, 3, 128, 128)
    """

    def __init__(self, token_dim: int = TOKEN_DIM):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(token_dim, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, 512 * 4 * 4),
            nn.ReLU(inplace=True),
        )

        self.deconv = nn.Sequential(
            # 4x4 -> 8x8
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            # 8x8 -> 16x16
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            # 16x16 -> 32x32
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            # 32x32 -> 64x64
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            # 64x64 -> 128x128
            nn.ConvTranspose2d(32, 3, kernel_size=4, stride=2, padding=1),
            nn.Tanh(),  # Normalized RGB range [-1, 1]
        )

    def forward(self, token: torch.Tensor) -> torch.Tensor:
        x = self.fc(token)
        x = x.view(-1, 512, 4, 4)
        part_image = self.deconv(x)
        return part_image


class RecursiveAutoencoder(nn.Module):
    """
    Full pipeline wrapping Encoder, Tokenizer, Decoder, and Combiner.
    """

    def __init__(self):
        super().__init__()
        self.base_encoder = BaseEncoder()
        self.tokenizer = RecursiveTokenizer()
        self.decoder = Decoder()

    def encode(self, image: torch.Tensor):
        latent_vector = self.base_encoder(image)
        tokens, eos_probs = self.tokenizer(latent_vector)
        return tokens, eos_probs

    def decode(self, tokens: list) -> list:
        part_images = [self.decoder(t) for t in tokens]
        return part_images

    def combine(self, part_images: list) -> torch.Tensor:
        reconstructed = torch.stack(part_images, dim=0).sum(dim=0)
        return torch.clamp(reconstructed, -1.0, 1.0)

    def forward(self, image: torch.Tensor):
        tokens, eos_probs = self.encode(image)
        part_images = self.decode(tokens)
        reconstruction = self.combine(part_images)
        return reconstruction, part_images, eos_probs


if __name__ == "__main__":
    dummy_image = torch.randn(2, 3, 128, 128)
    model = RecursiveAutoencoder()

    reconstructed_img, parts, eos = model(dummy_image)

    print("Input shape:         ", dummy_image.shape)
    print("Reconstructed shape: ", reconstructed_img.shape)
    print(f"Num partial images:   {len(parts)} (Each shape: {parts[0].shape})")
    print(f"EOS shape per step:   {eos[0].shape}")