import torch
import torch.nn as nn
from model import SimpleTransformer
from dataset import PairedDataset
from transformers import GPT2Tokenizer
from torch.utils.data import DataLoader


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleTransformer(vocab_size=tokenizer.vocab_size).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
criterion = nn.CrossEntropyLoss()

dataset = PairedDataset(size=50)
dataloader = DataLoader(dataset, batch_size=2)

model.train()
for epoch in range(1):
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        
        optimizer.zero_grad()
        logits = model(x)
        
        # Reshape for CrossEntropy: (Batch * Seq, Vocab)
        loss = criterion(logits.view(-1, logits.size(-1)), y.view(-1))
        loss.backward()
        optimizer.step()
        print(f"Loss: {loss.item():.4f}")

# 3. Save
torch.save(model.state_dict(), "small_transformer.pt")

# 4. Restore
model.load_state_dict(torch.load("small_transformer.pt"))
model.eval()