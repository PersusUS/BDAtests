Quiz Practice Application - Web Version
========================================

An intelligent quiz application with AI-powered question extraction and personalized explanations for wrong answers.

Features
--------
- Web-based modern interface
- AI extracts questions from .docx files automatically
- Randomized answer options to prevent memorization
- AI-generated explanations for incorrect answers
- Detailed quiz logs with learning insights
- Configurable number of questions per quiz

Requirements
------------
- Python 3.7+
- Flask
- Flask-CORS
- python-docx
- google-generativeai (for AI-powered features)
- python-dotenv (for environment variables)

Installation
------------
1. Install all required packages:
   pip install flask flask-cors python-docx google-generativeai python-dotenv

2. Setup your Gemini API key:
   - Get your API key from: https://makersuite.google.com/app/apikey
   - Copy .env.example to .env
   - Edit .env and replace 'your-api-key-here' with your actual key
   - IMPORTANT: Never commit .env file to Git (it's in .gitignore)

Building Questions Database
----------------------------
1. Place your .docx files with questions in the docs/ folder

2. Run the AI extraction:
   python build_questions_gemini.py
   
   This uses Gemini AI to:
   - Extract ALL questions from your documents accurately
   - Filter out questions with diagrams or external references
   - Reformat questions to be self-contained and clear
   - Skip incomplete or ambiguous questions
   
   The script will process all .docx files and create questions.json

Usage
-----
1. Start the Flask server:
   python app.py

2. Open your web browser and navigate to:
   http://localhost:5000

3. Click "Start Quiz" to begin

4. For each incorrect answer, you'll receive:
   - AI-generated explanation of why your answer was wrong
   - Clear explanation of why the correct answer is right
   - Key concepts to help you learn

Alternative: Double-click start_quiz.bat to automatically install dependencies and start the server.

Configuration
-------------
Edit quiz.py to customize the quiz behavior:

NUM_QUESTIONS: Number of questions per quiz (default: 20)
  Change this value to set how many questions appear in each quiz session.

Question Format in .docx files:
- Questions should be numbered (e.g., "1. Question text") or bold
- Options should be formatted as A., B., C., D.
- Answer should be marked as "Answer: X" or "Correct Answer: X" where X is A, B, C, or D

The application automatically:
- Extracts questions from all .docx files in the docs folder
- Filters out questions requiring diagrams or images
- Reformats questions to remove option letter references
- Shuffles answer options to prevent memorization
- Generates personalized explanations for wrong answers using AI
- Saves quiz results to the logs folder with timestamps

AI Features
-----------
The application uses Google's Gemini AI for:

1. Question Extraction (build_questions_gemini.py):
   - Intelligently parses .docx files
   - Filters questions needing visual aids
   - Reformats questions for clarity
   - Validates all questions are answerable

2. Learning Explanations (app.py):
   - Generates explanations for incorrect answers
   - Explains why correct answer is right
   - Explains why your answer was wrong
   - Teaches key concepts for better understanding

Files
-----
- quiz.py: Clean quiz logic (loads questions, shuffles, runs quiz)
- build_questions_gemini.py: AI-powered question extraction from .docx files
- app.py: Flask backend server with AI explanation generation
- quiz_web.html: Modern web interface with explanation display
- start_quiz.bat: Automated startup script
- .env.example: Template for environment variables
- .gitignore: Git ignore rules (protects .env and logs)
- docs/: Place your .docx files with questions here
- logs/: Quiz results with explanations saved here (ignored by Git)
- questions.json: Generated database of extracted questions

Troubleshooting
---------------
- If questions.json is empty: Check your .docx files format matches requirements
- If API errors occur: Verify your GEMINI_API_KEY is set correctly in .env
- If explanations don't appear: Ensure .env file is in the test directory
- If shuffle doesn't work: Clear browser cache or use incognito mode
