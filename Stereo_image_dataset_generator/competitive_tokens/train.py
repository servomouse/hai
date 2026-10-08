import os
import glob
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.utils import save_image

# Import components from arch.py
from arch import (
    RecursiveAutoencoder,
    LATENT_DIM,
    TOKEN_DIM,
    NUM_TOKENS,
    EOS_THRESHOLD,
)
from custom_loss import compute_progressive_residual_loss, compute_marginal_contribution_loss, compute_topk_dominance_loss

# Configuration & Constants
DATASET_PATH = "D:/Work/Projects/HAI/Stereo_image_dataset_generator/cropped_dataset/images_128"
SAMPLES_DIR = "./samples"
CHECKPOINT_PATH = "./checkpoint.pth"

NUM_IMAGES_TO_LOAD = 512
BATCH_SIZE = 16
EPOCHS = 1000
LEARNING_RATE = 1e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class InMemoryDataset(Dataset):
    """
    Loads up to `max_images` 128x128 PNG images directly into RAM.
    Normalizes images to range [-1, 1].
    """

    def __init__(self, folder_path: str, max_images: int = 512):
        super().__init__()
        self.images = []

        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]
                ),  # [0, 1] -> [-1, 1]
            ]
        )

        image_paths = sorted(glob.glob(os.path.join(folder_path, "*.png")))[
            :max_images
        ]
        if not image_paths:
            raise FileNotFoundError(
                f"No PNG images found in DATASET_PATH: {folder_path}"
            )

        print(f"Loading {len(image_paths)} images into RAM...")
        for path in image_paths:
            img = Image.open(path).convert("RGB")
            self.images.append(transform(img))

        # Stack into a single tensor in memory: Shape (N, 3, 128, 128)
        self.images = torch.stack(self.images)
        print(f"Loaded {self.images.shape[0]} images successfully.")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        return self.images[idx]


def get_errors_competitive(partial_images: list[torch.Tensor], input_image: torch.Tensor, loss_func=F.l1_loss,) -> list[torch.Tensor]:  # Do not modify!
    """
    Computes residual target loss per token decoding step.

    Args:
        partial_images: List of individual token decoder outputs [(B, 3, 128, 128), ...]
        input_image: Target ground truth image tensor (B, 3, 128, 128)

    Returns:
        errors: List of scalar loss tensors [loss_0, loss_1, ..., loss_N-1]
    """
    errors = []
    # Blank base image (zeros in [-1, 1] range represents mid-gray neutral base)
    reconstructed_image = torch.zeros_like(input_image)

    for i in range(len(partial_images)):
        # For the first token, limit the target residual to roughly 10% of the
        # remaining image details so it learns a coarse approximation instead of
        # reconstructing the full image immediately.
        residual = input_image - reconstructed_image.detach()
        if i == 0:
            target_residual = residual * 0.1
        else:
            target_residual = residual

        # Use per-pixel error so poorly reconstructed pixels contribute less
        # to the target while preserving the image tensor's shape.
        pixel_error = F.l1_loss(
            partial_images[i].detach(), target_residual, reduction="none"
        )
        weighted_target_residual = target_residual * torch.clamp(
            1.0 - pixel_error, min=0.0, max=1.0
        )

        step_loss = loss_func(partial_images[i], weighted_target_residual)
        # step_loss = ExponentialQualityLoss()(partial_images[i], target_residual)
        # step_loss = nn.MSELoss()(partial_images[i], target_residual)
        # step_loss = F.l1_loss(partial_images[i], target_residual)
        errors.append(step_loss)

        # Update cumulative reconstructed image for the next step's target calculation
        reconstructed_image = torch.clamp(
            reconstructed_image + partial_images[i], -1.0, 1.0
        )

    return errors


def get_errors_masked(partial_images: list[torch.Tensor], input_image: torch.Tensor, loss_func) -> list[torch.Tensor]: # Do not modify!
    """
    Computes masked target loss for each token's image region.

    Args:
        partial_images: List of individual token decoder outputs [(B, 3, 128, 128), ...]
        input_image: Target ground truth image tensor (B, 3, 128, 128)

    Returns:
        errors: List of scalar loss tensors [loss_0, loss_1, ..., loss_N-1]
    """
    regions = [
        (0, 0, 64, 64),
        (32, 0, 96, 64),
        (64, 0, 128, 64),
        (0, 32, 64, 96),
        (64, 32, 128, 96),
        (0, 64, 64, 128),
        (32, 64, 96, 128),
        (64, 64, 128, 128),
    ]
    errors = []
    # Blank base image (zeros in [-1, 1] range represents mid-gray neutral base)
    reconstructed_image = torch.zeros_like(input_image)
    for i in range(len(partial_images)):
        target_residual = input_image - reconstructed_image.detach()
        x_start, y_start, x_end, y_end = regions[i]
        mask = torch.zeros_like(input_image)
        mask[..., y_start:y_end, x_start:x_end] = 1
        masked_input = target_residual * mask

        step_loss = loss_func(partial_images[i], masked_input)
        errors.append(step_loss)

        # Update cumulative reconstructed image for the next step's target calculation
        reconstructed_image = torch.clamp(
            reconstructed_image + partial_images[i], -1.0, 1.0
        )

    return errors


def get_errors_prop(partial_images: list[torch.Tensor], input_image: torch.Tensor, loss_func) -> list[torch.Tensor]:
    num_tokens = len(partial_images)

    # Stack along a new dimension (Tokens, Batch, Channels, Height, Width)
    stacked_partials = torch.stack(partial_images, dim=0)  # Shape: [N, B, C, H, W]

    # Absolute contribution of each token per pixel
    abs_contributions = torch.abs(stacked_partials)  # Shape: [N, B, C, H, W]

    # Find the top-3 contributing tokens along the token dimension (dim=0)
    # top_indices shape: [3, B, C, H, W]
    _, top_indices = torch.topk(abs_contributions, k=min(3, num_tokens), dim=0)

    # Create a mask for each token: check if token ID (0..N-1) appears anywhere in top_indices [3, B, C, H, W]
    # token_ids shape: [N, 1, 1, 1, 1, 1] vs top_indices shape: [1, 3, B, C, H, W]
    token_ids = torch.arange(num_tokens, device=input_image.device).view(-1, 1, 1, 1, 1, 1)
    expanded_top = top_indices.unsqueeze(0)  # Shape: [1, 3, B, C, H, W]

    # Match along the top-k dimension (dim=1 in expanded_top), resulting in [N, B, C, H, W]
    is_top3_mask = (token_ids == expanded_top).any(dim=1)

    # Zero out contributions outside top-3
    top3_contributions = torch.where(is_top3_mask, abs_contributions, 0.0)

    # Sum contributions of top 3 for normalization
    top3_sum = top3_contributions.sum(dim=0, keepdim=True)  # Shape: [1, B, C, H, W]

    # Calculate proportional weights (avoiding division by zero)
    weights = torch.where(top3_sum > 1e-8, top3_contributions / top3_sum, 0.0)

    # Distribute input target image proportionally to each token
    targets = weights * input_image.unsqueeze(0)  # Shape: [N, B, C, H, W]

    # Compute loss per token
    errors = [loss_func(partial_images[i], targets[i]) for i in range(num_tokens)]

    return errors


def get_errors_composite(partial_images: list[torch.Tensor], input_image: torch.Tensor, loss_func) -> list[torch.Tensor]:
    """
    Computes each token's change in reconstruction loss when that token is removed.

    Args:
        partial_images: List of individual token decoder outputs [(B, 3, 128, 128), ...]
        input_image: Target ground truth image tensor (B, 3, 128, 128)

    Returns:
        errors: List of scalar loss changes [error_0, error_1, ..., error_N-1]
    """
    if not partial_images:
        return []

    opacity = 0.5

    def composite(images: list[torch.Tensor]) -> torch.Tensor:
        reconstructed_image = torch.zeros_like(input_image)
        for image in images:
            reconstructed_image = (
                opacity * image + (1.0 - opacity) * reconstructed_image
            )
        return reconstructed_image

    total_error = loss_func(composite(partial_images), input_image)
    dropout_index = torch.randint(len(partial_images), ()).item()
    errors = []

    for i in range(len(partial_images)):
        if i == dropout_index:
            errors.append(total_error * 0.0)
            continue

        without_image = partial_images[:i] + partial_images[i + 1 :]
        excluded_error = loss_func(composite(without_image), input_image)
        errors.append(excluded_error - total_error)

    return errors


def get_errors_simple(partial_images: list[torch.Tensor], input_image: torch.Tensor, loss_func) -> list[torch.Tensor]: # Do not modify!
    """
    Computes residual target loss per token decoding step.

    Args:
        partial_images: List of individual token decoder outputs [(B, 3, 128, 128), ...]
        input_image: Target ground truth image tensor (B, 3, 128, 128)

    Returns:
        errors: List of scalar loss tensors [loss_0, loss_1, ..., loss_N-1]
    """
    errors = []
    # Blank base image (zeros in [-1, 1] range represents mid-gray neutral base)
    reconstructed_image = torch.zeros_like(input_image)

    for i in range(len(partial_images)):
        # For the first token, limit the target residual to roughly 10% of the
        # remaining image details so it learns a coarse approximation instead of
        # reconstructing the full image immediately.
        residual = input_image - reconstructed_image.detach()
        if i == 0:
            target_residual = residual * 0.1
        else:
            target_residual = residual

        # Loss evaluates how accurately partial_images[i] predicts target_residual
        # Using L1 loss (or L2/MSE) per pixel
        step_loss = loss_func(partial_images[i], target_residual)
        # step_loss = ExponentialQualityLoss()(partial_images[i], target_residual)
        # step_loss = nn.MSELoss()(partial_images[i], target_residual)
        # step_loss = F.l1_loss(partial_images[i], target_residual)
        errors.append(step_loss)

        # Update cumulative reconstructed image for the next step's target calculation
        reconstructed_image = torch.clamp(
            reconstructed_image + partial_images[i], -1.0, 1.0
        )

    return errors


def compute_eos_loss(eos_probs: list) -> torch.Tensor:
    """
    Targets 0.0 for intermediate steps and 1.0 at the final NUM_TOKENS step.
    """
    num_steps = len(eos_probs)
    total_bce = 0.0
    for i, eos_pred in enumerate(eos_probs):
        target_val = 1.0 if (i == num_steps - 1) else 0.0
        target = torch.full_like(eos_pred, target_val)
        total_bce = total_bce + F.binary_cross_entropy(eos_pred, target)

    return total_bce / num_steps


@torch.no_grad()
def save_sample_grid(
    model: nn.Module,
    sample_batch: torch.Tensor,
    epoch: int,
    output_dir: str = SAMPLES_DIR,
):
    """
    Generates partial and combined images for the first 3 samples, concatenates
    them into a single visual comparison grid, and saves to folder.
    Format per row: [Target | Part_1 | Part_2 | ... | Part_N | Reconstructed]
    """
    os.makedirs(output_dir, exist_ok=True)
    model.eval()

    sample_batch = sample_batch.to(DEVICE)  # Shape (3, 3, 128, 128)
    tokens, eos_probs = model.encode(sample_batch)
    part_images = model.decode(tokens)  # List of N tensors, each (3, 3, 128, 128)

    rows = []
    for i in range(sample_batch.size(0)):
        target_img = sample_batch[i : i + 1]  # (1, 3, 128, 128)
        row_parts = [target_img]

        accumulated = torch.zeros_like(target_img)
        for part in part_images:
            p_img = part[i : i + 1]
            accumulated = torch.clamp(accumulated + p_img, -1.0, 1.0)
            row_parts.append(p_img)

        row_parts.append(accumulated)
        # Concatenate horizontally: [Target, Part1, Part2, ..., Combined]
        full_row = torch.cat(row_parts, dim=3)
        rows.append(full_row)

    # Concatenate vertically for all 3 sample images
    grid = torch.cat(rows, dim=2)  # Shape (1, 3, 3*128, (N+2)*128)

    # De-normalize from [-1, 1] back to [0, 1] for saving
    grid = (grid * 0.5 + 0.5).clamp(0.0, 1.0)

    save_path = os.path.join(output_dir, f"sample_epoch_{epoch:03d}.png")
    save_image(grid, save_path)
    print(f"Saved sample visualization to: {save_path}")


def train():
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    # 1. Dataset & DataLoader
    dataset = InMemoryDataset(
        DATASET_PATH, max_images=NUM_IMAGES_TO_LOAD
    )
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Fixed 3 images for consistent logging across epochs
    sample_batch = dataset.images[:3]

    # 2. Model & Optimizer
    model = RecursiveAutoencoder().to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    
    start_epoch = 1

    # 3. Checkpoint Loading
    if os.path.exists(CHECKPOINT_PATH):
        print(f"Found checkpoint at {CHECKPOINT_PATH}. Loading...")
        checkpoint = torch.load(CHECKPOINT_PATH, map_location=DEVICE)
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        start_epoch = checkpoint["epoch"] + 1
        print(f"Resuming training from epoch {start_epoch}.")
    else:
        print("No checkpoint found. Starting fresh training.")

    # 4. Training Loop
    for epoch in range(start_epoch, EPOCHS + 1):
        model.train()
        total_progressive_loss = 0.0
        total_eos_loss = 0.0

        for batch in dataloader:
            batch = batch.to(DEVICE)

            optimizer.zero_grad()

            tokens, eos_probs = model.encode(batch)
            part_images = model.decode(tokens)

            stacked_part_images = torch.stack(part_images, dim=1)
            # progressive_loss = compute_marginal_contribution_loss(stacked_part_images, batch)
            progressive_loss = compute_topk_dominance_loss(stacked_part_images, batch)
            # progressive_loss = compute_progressive_residual_loss(stacked_part_images, batch)
            progressive_loss.backward()
            optimizer.step()

            total_progressive_loss += progressive_loss.item()

        avg_progressive_loss = total_progressive_loss / len(dataloader)
        # avg_eos_loss = total_eos_loss / len(dataloader)
        print(
            f"Epoch [{epoch}/{EPOCHS}] - Progressive residual loss: "
            f"{avg_progressive_loss:.6f} "
            # f"- EOS loss: {avg_eos_loss:.6f}"
        )

        # Save Checkpoint
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "progressive_residual_loss": avg_progressive_loss,
                # "eos_loss": avg_eos_loss,
            },
            CHECKPOINT_PATH,
        )

        # Save Sample Visualizations
        save_sample_grid(model, sample_batch, epoch)


if __name__ == "__main__":
    train()
    # train_single()


# def get_tokens(image):
#     latent_vector = primary_encoder(image) # Simple CNN + linear

#     tokens = []
#     reminder = latent_vector
#     for _ in range(MAX_NUM_TOKENS):
#         t = token_head(reminder)
#         r = reminder_head(reminder, t)
#         # eos = eos_head(r)   # Not implemented yet
#         tokens.append(t)
#         reminder = r
#         if eos > EOS_THRESHOLD:
#             break
#     return tokens

# def decode_tokens(tokens):
#     reconstructed_images = []
#     for t in tokens:
#         # Decoder decodes each token into a full-sized image
#         # On the later stage, the images are combined together
#         # usiing alpha compositing
#         reconstructed_images.append(decoder(t))
#     return reconstructed_images
