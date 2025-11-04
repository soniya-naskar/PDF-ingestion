import json
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:8000/ask"
EVAL_PATH = Path(__file__).resolve().parent / "qa_eval.json"

def run_evaluation():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    correct = 0
    total = len(qa_pairs)
    print(f"🔍 Running evaluation on {total} questions via /ask endpoint...\n")

    for qa in qa_pairs:
        payload = {
            "question": qa["question"],
            "top_k": 3
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answers", [""])[0] if "answers" in data else ""
            else:
                print(f"⚠️ Error: {response.status_code} for Q{qa['id']}")
                answer = ""
        except Exception as e:
            print(f"⚠️ Exception for Q{qa['id']}: {e}")
            answer = ""

        expected = qa["expected_answer"]
        match = expected.lower().split()[0] in answer.lower() if answer else False
        correct += int(match)

        print(f"Q{qa['id']}: {qa['question']}")
        print(f"🟩 Expected: {expected}")
        print(f"🟦 Got: {answer}\n{'-'*70}")

    accuracy = round(correct / total * 100, 2)
    print(f"\n✅ Evaluation complete — Accuracy: {accuracy}% ({correct}/{total} correct)")

if __name__ == "__main__":
    run_evaluation()
