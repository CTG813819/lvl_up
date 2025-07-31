import json
import os
from collections import Counter
from datetime import datetime

def analyze_log(ai_type):
    log_path = os.path.join(os.path.dirname(__file__), f"../learning_logs/{ai_type.lower()}_learning_log.jsonl")
    if not os.path.exists(log_path):
        print("No log found.")
        return
    questions = []
    topics = Counter()
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            questions.append(entry["question"])
            # Simple topic extraction: use first word or keyword extraction
            topic = entry["question"].split()[0].lower() if entry["question"] else "unknown"
            topics[topic] += 1
    print(f"Total mistakes logged: {len(questions)}")
    print("Most common topics:", topics.most_common(5))
    print("Sample questions:", questions[:5])

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze_learning_logs.py <ai_type>")
        sys.exit(1)
    analyze_log(sys.argv[1]) 