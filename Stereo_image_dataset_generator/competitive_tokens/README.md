# Competitive Tokens Autoencoder

This module implements a recursive autoencoder that represents an image as a sequence of latent tokens. Each token is decoded independently into a partial image, and the partial images are summed to form the reconstruction.

## Architecture

```text
RGB image (B, 3, 128, 128)
        |
        v
BaseEncoder
  CNN: 128 -> 64 -> 32 -> 16 -> 8 -> 4
  Fully connected: 8192 -> 512 -> 128
        |
        v
RecursiveTokenizer
  Repeatedly extracts a 32-dimensional token and updates the 128-dimensional remainder
        |
        +--> token 1 --> Decoder --> partial image 1 (B, 3, 128, 128)
        +--> token 2 --> Decoder --> partial image 2 (B, 3, 128, 128)
        +--> ...
        +--> token 10 --> Decoder --> partial image 10 (B, 3, 128, 128)
                                 |
                                 v
                     Sum partial images, clamp to [-1, 1]
```

### Image encoder

`BaseEncoder` accepts RGB images with shape `(B, 3, 128, 128)`. Five stride-2 convolution blocks reduce the spatial dimensions from 128x128 to 4x4, with channel widths 32, 64, 128, 256, and 512. Each block uses batch normalization and LeakyReLU. The flattened features pass through fully connected layers of sizes 8192 -> 512 -> 128, producing one 128-dimensional latent vector per image.

### Recursive tokenizer

`RecursiveTokenizer` starts with the encoder's latent vector as its remainder. At each step, `SubtractTokenModule`:

1. Predicts a 32-dimensional token from the current remainder.
2. Concatenates the token with the remainder and predicts a latent residual update. The next remainder is the current remainder minus this update.
3. Predicts an end-of-sequence (EOS) probability from the token and updated remainder. A sigmoid keeps this probability in `[0, 1]`.

The tokenizer emits at most 10 tokens. During training it always runs all 10 steps. In evaluation mode, early termination is enabled only for a batch of one: token generation stops after a step whose EOS probability is greater than `0.5`. Other evaluation batch sizes run the full 10 steps.

### Token decoder

`Decoder` maps each 32-dimensional token through fully connected layers to a 512-channel 4x4 feature map. Five transposed-convolution blocks upsample it through 8x8, 16x16, 32x32, 64x64, and 128x128. The final layer produces a three-channel partial image, with `tanh` outputs in `[-1, 1]`.

The same decoder is shared across all tokens. Each token therefore produces one partial image with shape `(B, 3, 128, 128)`.

### Combining partial images

`RecursiveAutoencoder.combine` sums the partial images across token steps and clamps each output value to `[-1, 1]`. The result has shape `(B, 3, 128, 128)`.

## Main API

- `encode(image)` returns `(tokens, eos_probs)`.
- `decode(tokens)` returns one partial image per token.
- `combine(part_images)` returns the clamped reconstruction.
- `forward(image)` returns `(reconstruction, part_images, eos_probs)`.

## Default dimensions

| Setting | Default |
| --- | ---: |
| Input image | 3 x 128 x 128 |
| Latent dimension | 128 |
| Token dimension | 32 |
| Maximum tokens | 10 |
| EOS threshold | 0.5 |
