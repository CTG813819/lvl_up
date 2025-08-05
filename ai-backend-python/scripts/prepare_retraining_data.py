import json
import os

def extract_qa_pairs(ai_type):
    log_path = os.path.join(os.path.dirname(__file__), f"../learning_logs/{ai_type.lower()}_learning_log.jsonl")
    qa_pairs = []
    if not os.path.exists(log_path):
        return qa_pairs
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            qa_pairs.append((entry["question"], entry["correct_answer"]))
    return qa_pairs

def save_for_finetuning(ai_type, output_path):
    qa_pairs = extract_qa_pairs(ai_type)
    with open(output_path, "w", encoding="utf-8") as f:
        for q, a in qa_pairs:
            f.write(json.dumps({"prompt": q, "completion": a}) + "\n")

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python prepare_retraining_data.py <ai_type> <output_path>")
        sys.exit(1)
    ai_type = sys.argv[1]
    output_path = sys.argv[2]
    save_for_finetuning(ai_type, output_path)
    print(f"Saved retraining data for {ai_type} to {output_path}") 