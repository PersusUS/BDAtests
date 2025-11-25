from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from quiz import load_questions, shuffle_options, JSON_OUTPUT, LOG_FOLDER, NUM_QUESTIONS

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)

@app.route('/api/start-quiz', methods=['GET'])
def start_quiz():
    """Initialize a new quiz session"""
    if not os.path.exists(JSON_OUTPUT):
        return jsonify({"error": "questions.json not found. Run build_questions_gemini.py first"}), 404
    
    all_questions = load_questions()
    num_questions = min(NUM_QUESTIONS, len(all_questions))
    selected = random.sample(all_questions, num_questions)
    
    # Shuffle options for each question
    quiz_data = []
    for q in selected:
        options, correct = shuffle_options(q["options"], q["answer"])
        quiz_data.append({
            "question": q["question"],
            "options": options,
            "correct_answer": correct,
            "original_answer": q["answer"]
        })
    
    response = jsonify({
        "questions": quiz_data,
        "total": len(quiz_data)
    })
    # Prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and get results with AI explanations"""
    data = request.json
    answers = data.get('answers', [])
    questions = data.get('questions', [])
    
    results = []
    correct_count = 0
    
    for i, q in enumerate(questions):
        user_answer = answers[i] if i < len(answers) else None
        is_correct = user_answer == q['correct_answer'] if user_answer else False
        
        if is_correct:
            correct_count += 1
        
        user_answer_text = q['options'][ord(user_answer) - 65] if user_answer and user_answer in 'ABCD' else "Not answered"
        correct_answer_text = q['options'][ord(q['correct_answer']) - 65]
        
        # Generate explanation for incorrect answers
        explanation = ""
        if not is_correct and GEMINI_API_KEY:
            explanation = generate_explanation(q["question"], user_answer_text, correct_answer_text, q["options"])
        
        results.append({
            "question": q["question"],
            "all_options": q["options"],
            "user_answer_letter": user_answer or "None",
            "user_answer_text": user_answer_text,
            "correct_answer_letter": q["correct_answer"],
            "correct_answer_text": correct_answer_text,
            "is_correct": is_correct,
            "explanation": explanation
        })
    
    # Save log
    os.makedirs(LOG_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_FOLDER, f"quiz_log_{timestamp}.json")
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        "results": results,
        "correct_count": correct_count,
        "total": len(questions),
        "percentage": (correct_count / len(questions) * 100) if len(questions) > 0 else 0,
        "log_file": log_file
    })

def generate_explanation(question, user_answer, correct_answer, all_options):
    """Generate explanation using Gemini AI"""
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        
        prompt = f"""You are a helpful tutor explaining why a student got a question wrong.

Question: {question}

All options were:
{chr(10).join([f'- {opt}' for opt in all_options])}

Student answered: {user_answer}
Correct answer: {correct_answer}

Provide a clear, concise explanation (2-3 sentences) that:
1. Explains why the correct answer is right
2. Explains why the student's answer was wrong (if not "Not answered")
3. Teaches the key concept so they understand for next time

Keep it educational and encouraging, not condescending."""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Unable to generate explanation: {str(e)}"

@app.route('/')
def serve():
    return send_file('quiz_web.html')

@app.route('/quiz_web.html')
def serve_quiz():
    return send_file('quiz_web.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
