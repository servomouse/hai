import torch
from image_encoder import ImageMeaningEncoder


# 1. Re-instantiate the architecture
model = ImageMeaningEncoder()

# 2. Load the weights
model.load_state_dict(torch.load('model_weights.pth'))
model.eval() # Set to evaluation mode (turns off Dropout)

# 3. Use it
with torch.no_grad():
    # dummy_img shape: [1, 3, 512, 512], dummy_vec shape: [1, 1024]
    prediction = model(dummy_img, dummy_vec)
    print(prediction.shape) # Should be [1, 1024]