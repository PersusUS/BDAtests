import os
import json
import random
from datetime import datetime

# === CONFIGURATION ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_OUTPUT = os.path.join(SCRIPT_DIR, "questions.json")
LOG_FOLDER = os.path.join(SCRIPT_DIR, "logs")
NUM_QUESTIONS = 20  # Number of questions per quiz

# === CORE FUNCTIONS ===
def load_questions():
    """Load questions from JSON file"""
    if not os.path.exists(JSON_OUTPUT):
        raise FileNotFoundError(f"questions.json not found. Run build_questions.py first.")
    
    with open(JSON_OUTPUT, "r", encoding="utf-8") as f:
        return json.load(f)

def shuffle_options(options, answer):
    """Shuffle answer options and return new order with correct answer"""
    correct_index = ord(answer) - 65
    correct_option = options[correct_index]
    
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)
    
    new_answer_index = shuffled_options.index(correct_option)
    new_answer = chr(65 + new_answer_index)
    
    return shuffled_options, new_answer

def run_quiz():
    """Run command-line quiz"""
    os.makedirs(LOG_FOLDER, exist_ok=True)
    questions = load_questions()
    num_questions = min(NUM_QUESTIONS, len(questions))
    selected = random.sample(questions, num_questions)
    log = []

    print("=== QUIZ START ===")
    for idx, q in enumerate(selected, 1):
        options, correct = shuffle_options(q["options"], q["answer"])
        print(f"\n{idx}. {q['question']}")
        for i, opt in enumerate(options):
            print(f"{chr(65 + i)}. {opt}")

        user = input("Your answer: ").strip().upper()
        is_correct = user == correct
        
        user_option_text = options[ord(user) - 65] if user in 'ABCD' and ord(user) - 65 < len(options) else "Invalid"
        correct_option_text = options[ord(correct) - 65]
        
        log.append({
            "question": q["question"],
            "all_options": options,
            "user_answer_letter": user,
            "user_answer_text": user_option_text,
            "correct_answer_letter": correct,
            "correct_answer_text": correct_option_text,
            "is_correct": is_correct
        })

    # Summary
    correct_count = sum(entry["is_correct"] for entry in log)
    print(f"\n=== RESULTS: {correct_count}/{num_questions} correct ===")
    for idx, entry in enumerate(log, 1):
        status = "✓" if entry["is_correct"] else "✗"
        print(f"\n{status} Q{idx}: {entry['question']}")
        print(f"   Your answer: {entry['user_answer_letter']}. {entry['user_answer_text']}")
        print(f"   Correct answer: {entry['correct_answer_letter']}. {entry['correct_answer_text']}")

    # Save log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_FOLDER, f"quiz_log_{timestamp}.json")
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"\nLog saved to {log_file}")

if __name__ == "__main__":
    try:
        run_quiz()
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please run: python build_questions.py")
