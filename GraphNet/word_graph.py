import json
import os
import difflib
from collections import defaultdict

class PersistentWordGraph:
    def __init__(self, storage_file="wordgraph.json"):
        self.storage_file = storage_file
        self.vocabulary = set()
        # Context: { "word1 word2": { "target": count } }
        # Using a space-separated string as a key because JSON doesn't support tuple keys
        self.context_map = defaultdict(lambda: defaultdict(int))
        
        self.load_graph()

    def train(self, text, save_after=False):
        """Teaches the graph and optionally saves it."""
        words = text.lower().split()
        self.vocabulary.update(words)
        for i in range(len(words) - 2):
            context_key = f"{words[i]} {words[i+1]}"
            target = words[i+2]
            self.context_map[context_key][target] += 1
        
        if save_after:
            self.save_graph()

    def save_graph(self):
        """Dumps the current state to a JSON file."""
        data = {
            "vocabulary": list(self.vocabulary),
            "context_map": {k: dict(v) for k, v in self.context_map.items()}
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Graph saved to {self.storage_file}")

    def load_graph(self):
        """Loads data if file exists, otherwise starts fresh."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vocabulary = set(data.get("vocabulary", []))
                    # Reconstruct the nested defaultdict
                    raw_map = data.get("context_map", {})
                    for context, targets in raw_map.items():
                        self.context_map[context].update(targets)
                print(f"Loaded {len(self.vocabulary)} words from {self.storage_file}")
            except (json.JSONDecodeError, KeyError):
                print("Existing file corrupted or incompatible. Starting fresh.")
        else:
            print("No existing graph found. Initializing empty.")

    def get_superposition(self, word, history=[]):
        word = word.lower()
        similar_candidates = difflib.get_close_matches(word, self.vocabulary, n=5, cutoff=0.5)
        
        if not similar_candidates:
            return [{"word": word, "prob": 1.0, "note": "new"}]

        # Prepare context key from history
        context_key = " ".join(history[-2:]).lower() if len(history) >= 2 else None
        
        results = []
        for cand in similar_candidates:
            # 1. Lexical Similarity (The "Looks like" factor)
            lex_score = difflib.SequenceMatcher(None, word, cand).ratio()
            
            # 2. Contextual Weight (The "Fits here" factor)
            context_score = 1.0
            if context_key and context_key in self.context_map:
                followers = self.context_map[context_key]
                total = sum(followers.values())
                # Laplacian smoothing (+0.1) prevents zero-division and complete exclusion
                context_score = (followers.get(cand, 0) + 0.1) / (total + 0.1)
            
            results.append({"word": cand, "score": lex_score * context_score})

        # Normalize probabilities to sum to 1.0
        total_score = sum(r["score"] for r in results)
        for r in results:
            r["probability"] = round(r["score"] / total_score, 3)
            del r["score"]

        return sorted(results, key=lambda x: x["probability"], reverse=True)

# --- Usage Example ---
wg = PersistentWordGraph()

# If it's the first time running, train it
if not wg.vocabulary:
    wg.train("The rule does not apply to this case", save_after=True)
    wg.train("He likes to eat a red apple every morning", save_after=True)

# Try a query
res = wg.get_superposition("aplly", history=["does", "not"])
print(f"Best match for 'aplly' after 'does not': {res[0]}")