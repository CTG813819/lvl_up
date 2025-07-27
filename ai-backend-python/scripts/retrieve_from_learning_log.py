import json
import os
from difflib import SequenceMatcher

def load_learning_log(ai_type):
    log_path = os.path.join(os.path.dirname(__file__), f"../learning_logs/{ai_type.lower()}_learning_log.jsonl")
    if not os.path.exists(log_path):
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def find_best_match(prompt, log, threshold=0.7):
    best = None
    best_score = 0
    for entry in log:
        score = SequenceMatcher(None, prompt, entry["question"]).ratio()
        if score > best_score:
            best_score = score
            best = entry
    return best if best_score >= threshold else None

def retrieve_answer(ai_type, prompt):
    log = load_learning_log(ai_type)
    match = find_best_match(prompt, log)
    if match:
        return match["correct_answer"]
    return None

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python retrieve_from_learning_log.py <ai_type> <prompt>")
        sys.exit(1)
    ai_type = sys.argv[1]
    prompt = sys.argv[2]
    answer = retrieve_answer(ai_type, prompt)
    if answer:
        print(f"Found similar Q&A. Suggested answer: {answer}")
    else:
        print("No similar question found in learning log.") 