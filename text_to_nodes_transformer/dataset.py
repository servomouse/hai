import torch
from torch.utils.data import Dataset
from torch.nn.utils.rnn import pad_sequence
from transformers import GPT2Tokenizer


# Initialize standard tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token # GPT2 doesn't have a default pad token

class PairedDataset(Dataset):
    def __init__(self, data_pairs, tokenizer, max_len=1024):
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.pairs = data_pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        in_text, out_text = self.pairs[idx]
        
        # We format it as: [SOS] Input [SEP] Output [EOS]
        # Using gpt2 tokens: <|endoftext|> acts as both SOS and SEP usually
        full_text = f"{in_text} {self.tokenizer.eos_token} {out_text}"
        
        tokens = self.tokenizer.encode(
            full_text, 
            truncation=True, 
            max_length=self.max_len, 
            add_special_tokens=True
        )
        
        # For training: x is tokens 0 to n-1, y is tokens 1 to n
        tensors = torch.tensor(tokens, dtype=torch.long)
        x = tensors[:-1]
        y = tensors[1:]
        
        return x, y

def collate_fn(batch):
    """
    Since sentences have different lengths, we must pad them to 
    match the longest item in the current batch.
    """
    xs, ys = zip(*batch)
    xs_padded = pad_sequence(xs, batch_first=True, padding_value=tokenizer.eos_token_id)
    ys_padded = pad_sequence(ys, batch_first=True, padding_value=-100) # -100 is ignored by CrossEntropy
    return xs_padded, ys_padded
