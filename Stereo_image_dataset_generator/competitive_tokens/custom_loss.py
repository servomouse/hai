import torch
import torch.nn as nn
import torch.nn.functional as F


class SoftGoodPixelPercentageLoss(nn.Module):
    def __init__(self, threshold: float = 0.05, sharpness: float = 50.0):
        """
        Args:
            threshold (tau): Max pixel value difference to be considered "good" (e.g., 0.05 out of 1.0).
            sharpness (k): How steep the differentiable step function is.
        """
        super().__init__()
        self.tau = threshold
        self.k = sharpness

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        abs_err = torch.abs(input - target)
        
        # Smooth proxy for: abs_err < threshold
        # Returns ~1.0 if err < tau, and ~0.0 if err > tau
        good_pixels_soft = torch.sigmoid(self.k * (self.tau - abs_err))
        
        # Maximize good pixels = minimize (1 - good_pixels)
        loss = 1.0 - good_pixels_soft.mean()
        return loss


class InvertedFocalLoss(nn.Module):
    def __init__(self, gamma: float = 2.0):
        """
        Args:
            gamma: Exponent for the quality weight. 
                   gamma = 0 reduces to standard L1 loss.
        """
        super().__init__()
        self.gamma = gamma

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        abs_err = torch.abs(input - target)
        # Quality score: 1.0 when error is 0, drops toward 0 as error reaches 1.0
        quality = torch.clamp(1.0 - abs_err, min=0.0, max=1.0)
        
        # Weight error by quality^gamma
        weighted_loss = (quality ** self.gamma) * abs_err
        return weighted_loss.mean()


class ExponentialQualityLoss(nn.Module):
    def __init__(self, gamma: float = 5.0, power: float = 1.0):
        """
        Args:
            gamma: Controls sensitivity. Higher values sharpen focus on very low-error pixels.
            power: 1.0 for L1-based exponential, 2.0 for L2-based exponential.
        """
        super().__init__()
        self.gamma = gamma
        self.power = power

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        abs_err = torch.abs(input - target)
        if self.power != 1.0:
            abs_err = abs_err ** self.power
        
        # Loss ranges between 0 (perfect) and 1 (large error)
        loss = 1.0 - torch.exp(-self.gamma * abs_err)
        return loss.mean()


def fixed_alpha_composite(partial_images, alpha=0.5):
    """
    Composites a sequence of token images using back-to-front fixed alpha blending.
    Args:
        partial_images: Tensor of shape (B, K, C, H, W)
        alpha: float, blending factor
    Returns:
        composite: Tensor of shape (B, C, H, W)
    """
    B, K, C, H, W = partial_images.shape
    composite = partial_images[:, 0]  # Initialize with first token
    
    for k in range(1, K):
        composite = alpha * partial_images[:, k] + (1 - alpha) * composite
        
    return composite


def compute_marginal_contribution_loss(partial_images, target_image, alpha=0.5, margin=0.01, penalty_weight=1.0):
    """
    Args:
        partial_images: (B, K, C, H, W) Decoded token representations.
        target_image: (B, C, H, W) Ground truth image.
        alpha: Fixed alpha blending weight.
        margin: Minimum expected improvement per token.
        penalty_weight: Weight for underperforming tokens.
    """
    B, K, C, H, W = partial_images.shape
    
    # 1. Full reconstruction error
    full_composite = fixed_alpha_composite(partial_images, alpha=alpha)
    loss_full = F.l1_loss(full_composite, target_image, reduction='none').mean(dim=[1, 2, 3])
    
    # 2. Leave-One-Out reconstruction errors
    marginal_penalties = 0.0
    for i in range(K):
        # Exclude token i
        tokens_loo = torch.cat([partial_images[:, :i], partial_images[:, i+1:]], dim=1)
        composite_loo = fixed_alpha_composite(tokens_loo, alpha=alpha)
        
        loss_loo = F.l1_loss(composite_loo, target_image, reduction='none').mean(dim=[1, 2, 3])
        
        # Utility = loss_loo - loss_full (how much error increases without token i)
        utility = loss_loo - loss_full
        
        # Penalize if utility < margin
        penalty = F.relu(margin - utility)
        marginal_penalties += penalty.mean()
        
    total_loss = loss_full.mean() + penalty_weight * (marginal_penalties / K)
    return total_loss


def compute_topk_dominance_loss(partial_images, target_image, alpha=0.5, top_k=3, temperature=0.1):
    """
    Forces individual tokens to specialize on regions where they best match the target.
    
    Args:
        partial_images: (B, K, C, H, W)
        target_image: (B, C, H, W)
        top_k: Number of dominant tokens to enforce specialization over.
        temperature: Softmax scaling factor for region attribution.
    """
    B, K, C, H, W = partial_images.shape
    
    # 1. Global composite loss
    full_composite = fixed_alpha_composite(partial_images, alpha=alpha)
    loss_recon = F.l1_loss(full_composite, target_image)
    
    # 2. Per-token pixel-wise absolute errors: (B, K, H, W)
    pixel_errors = torch.abs(partial_images - target_image.unsqueeze(1)).mean(dim=2)
    
    # 3. Soft dominance mask (tokens with smaller pixel errors get higher weight)
    # Negate errors so smaller error -> higher weight
    dominance_logits = -pixel_errors / temperature
    dominance_weights = F.softmax(dominance_logits, dim=1)  # (B, K, H, W)
    
    # 4. Zero out weights outside the Top-K contributors per pixel
    topk_vals, _ = torch.topk(dominance_weights, k=top_k, dim=1)
    kth_threshold = topk_vals[:, -1:, :, :]  # Cutoff threshold
    mask_topk = (dominance_weights >= kth_threshold).float()
    
    # Re-normalize weights among top-K
    filtered_weights = dominance_weights * mask_topk
    filtered_weights = filtered_weights / (filtered_weights.sum(dim=1, keepdim=True) + 1e-8)
    
    # 5. Specialized regional loss
    # Forces top contributors to fit their assigned pixel regions tightly
    weighted_pixel_errors = (filtered_weights * pixel_errors).sum(dim=1).mean()
    
    total_loss = loss_recon + weighted_pixel_errors
    return total_loss


def compute_progressive_residual_loss(partial_images, target_image, alpha=0.5, residual_decay=0.8):
    """
    Forces sequential tokens to target unexplained residuals from prior steps.
    
    Args:
        partial_images: (B, K, C, H, W)
        target_image: (B, C, H, W)
        residual_decay: Weight multiplier per subsequent step.
    """
    B, K, C, H, W = partial_images.shape
    
    cumulative_composite = partial_images[:, 0]
    total_loss = F.l1_loss(cumulative_composite, target_image)
    
    for k in range(1, K):
        # Unexplained target residual prior to adding token k
        residual_target = target_image - cumulative_composite
        
        # New token step contribution: partial_images[:, k] scaled by alpha
        token_step_contribution = alpha * partial_images[:, k]
        
        # Penalize discrepancy between token's output and required residual
        residual_loss = F.l1_loss(token_step_contribution, alpha * residual_target)
        
        # Update cumulative composite
        cumulative_composite = alpha * partial_images[:, k] + (1 - alpha) * cumulative_composite
        
        # Add progressive reconstruction error
        step_recon_loss = F.l1_loss(cumulative_composite, target_image)
        
        total_loss += (residual_decay ** k) * (step_recon_loss + residual_loss)
        
    return total_loss
