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

# Configuration & Constants
DATASET_PATH = "D:/Work/Projects/HAI/Stereo_image_dataset_generator/cropped_dataset/images_128"
SAMPLES_DIR = "./samples"
CHECKPOINT_PATH = "./checkpoint.pth"

NUM_IMAGES_TO_LOAD = 512
BATCH_SIZE = 16
EPOCHS = 100
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


def get_errors(
    partial_images: list[torch.Tensor], input_image: torch.Tensor
) -> list[torch.Tensor]:
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
        # Target for step i is whatever input details haven't been reconstructed yet
        target_residual = input_image - reconstructed_image.detach()

        # Loss evaluates how accurately partial_images[i] predicts target_residual
        # Using L1 loss (or L2/MSE) per pixel
        step_loss = F.l1_loss(partial_images[i], target_residual)
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
        total_step_errors = [0.0] * NUM_TOKENS
        total_eos_loss = 0.0

        for batch in dataloader:
            batch = batch.to(DEVICE)

            optimizer.zero_grad()

            tokens, eos_probs = model.encode(batch)
            part_images = model.decode(tokens)

            step_errors = get_errors(part_images, batch)

            # Calculate EOS loss
            eos_loss = compute_eos_loss(eos_probs)

            for step_error in step_errors:
                step_error.backward(retain_graph=True)
            (0.1 * eos_loss).backward()
            optimizer.step()

            for index, step_error in enumerate(step_errors):
                total_step_errors[index] += step_error.item()
            total_eos_loss += eos_loss.item()

        avg_step_errors = [
            step_total / len(dataloader) for step_total in total_step_errors
        ]
        avg_eos_loss = total_eos_loss / len(dataloader)
        formatted_errors = ", ".join(
            f"{error:.6f}" for error in avg_step_errors
        )
        print(
            f"Epoch [{epoch}/{EPOCHS}] - Step errors: [{formatted_errors}] "
            f"- EOS loss: {avg_eos_loss:.6f}"
        )

        # Save Checkpoint
        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "step_errors": avg_step_errors,
                "eos_loss": avg_eos_loss,
            },
            CHECKPOINT_PATH,
        )

        # Save Sample Visualizations
        save_sample_grid(model, sample_batch, epoch)


if __name__ == "__main__":
    train()
