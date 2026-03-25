import json
import os
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
        
    def levenshtein(self, s1, s2):
        """Calculates the edit distance between two strings."""
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def get_superposition(self, word, history=[]):
        word = word.lower()
        context_key = " ".join(history[-2:]).lower() if len(history) >= 2 else None
        
        # 1. Find candidates within a "Sanity Distance" (e.g., max 2-3 edits)
        candidates = []
        max_edit_dist = 2 if len(word) < 5 else 3
        
        for v in self.vocabulary:
            dist = self.levenshtein(word, v)
            if dist <= max_edit_dist:
                # Convert distance to a similarity score (0.0 to 1.0)
                score = 1 - (dist / max(len(word), len(v)))
                candidates.append({"word": v, "lex_score": score})

        # 2. Logic for "True Unknown" (Groot Case)
        # If no one is close, or the word is just a brand new entity
        if not candidates:
            return [{"word": word, "probability": 1.0, "status": "novel_atom"}]

        # 3. Apply Contextual Weighting
        results = []
        for cand in candidates:
            context_weight = 0.1 # Baseline for existing word
            if context_key in self.context_map:
                followers = self.context_map[context_key]
                # If this word actually appears in this context, boost it!
                if cand["word"] in followers:
                    context_weight = followers[cand["word"]] / sum(followers.values())
            
            # Final Superposition Score
            final_score = cand["lex_score"] * (1 + context_weight)
            results.append({"word": cand["word"], "score": final_score})

        # 4. Normalization
        total = sum(r["score"] for r in results)
        return sorted(
            [{"word": r["word"], "probability": round(r["score"] / total, 3)} for r in results],
            key=lambda x: x["probability"], reverse=True
        )

# --- Usage Example ---
wg = PersistentWordGraph()

# If it's the first time running, train it
if not wg.vocabulary:
    wg.train("The rule does not apply to this case", save_after=True)
    wg.train("He likes to eat a red apple every morning", save_after=True)

# Try a query
tasks = [
    "does not aplly (apply)".split(),
    "a red aplly (apple)".split(),
    "I am Groot (Groot)".split(),
]
for t in tasks:
    res = wg.get_superposition(t[2], history=t[:2])
    print(f"Best match for '{t[2]}' after '{' '.join(t[:2])}':")
    print(f"\t {res}")
    print(f"\t correct answer: {t[3]}")
wg.get_superposition("Groot", history=["I", "am"])