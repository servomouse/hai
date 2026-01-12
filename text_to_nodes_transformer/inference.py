import torch
import torch.nn as nn
from model import SimpleTransformer
from transformers import GPT2Tokenizer


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleTransformer(vocab_size=tokenizer.vocab_size).to(device)

def answer_question(question, max_new_tokens=50):
    # Prepare the prompt exactly like the training format
    prompt = f"{question} {tokenizer.eos_token}"
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    
    model.eval()
    with torch.no_grad():
        for _ in range(max_new_tokens):
            # We only need to pass the last 1024 tokens if it gets long
            outputs = model(input_ids[:, -1024:]) 
            next_token_logits = outputs[:, -1, :]
            next_token = torch.argmax(next_token_logits, dim=-1).unsqueeze(0)
            
            input_ids = torch.cat([input_ids, next_token], dim=1)
            
            if next_token.item() == tokenizer.eos_token_id:
                break
    
    # Extract only the generated part (after the separator)
    full_string = tokenizer.decode(input_ids[0], skip_special_tokens=False)
    answer = full_string.split(tokenizer.eos_token)[-1]
    return answer.strip()

print(answer_question("What is the capital of France?"))
