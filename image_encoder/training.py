import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from image_encoder import ImageMeaningEncoder

class CustomVectorDataset(Dataset):
    def __init__(self, image_paths, input_vectors, target_vectors):
        self.image_paths = image_paths
        self.input_vectors = input_vectors
        self.target_vectors = target_vectors
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = Image.open(self.image_paths[idx]).convert('RGB')
        img = self.transform(img)
        in_vec = torch.tensor(self.input_vectors[idx], dtype=torch.float32)
        target = torch.tensor(self.target_vectors[idx], dtype=torch.float32)
        return img, in_vec, target

# --- Training Loop ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ImageMeaningEncoder().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
criterion = nn.MSELoss() # Assuming you want to match the vectors

# Example usage with dummy data:
# loader = DataLoader(dataset, batch_size=16, shuffle=True)
# for images, in_vecs, targets in loader:
#     optimizer.zero_grad()
#     outputs = model(images.to(device), in_vecs.to(device))
#     loss = criterion(outputs, targets.to(device))
#     loss.backward()
#     optimizer.step()

torch.save(model.state_dict(), 'model_weights.pth')
print("Model saved! Size is approx 150-200MB.")