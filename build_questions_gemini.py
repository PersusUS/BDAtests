import os
import json
import google.generativeai as genai
from docx import Document
from dotenv import load_dotenv

# === CONFIGURATION ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCX_FOLDER = os.path.join(SCRIPT_DIR, "docs")
JSON_OUTPUT = os.path.join(SCRIPT_DIR, "questions.json")

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your-api-key-here":
    print("="*60)
    print("ERROR: GEMINI_API_KEY not set")
    print("="*60)
    print("\n1. Get your API key from:")
    print("   https://makersuite.google.com/app/apikey")
    print("\n2. Create a .env file in this directory with:")
    print("   GEMINI_API_KEY=your-actual-key-here")
    print("\n   Or copy .env.example to .env and edit it")
    print("="*60)
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_docx(file_path):
    """Extract all text from a docx file"""
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return "\n".join(text)

def extract_questions_with_gemini(text, filename):
    """Use Gemini to extract questions from text"""
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    prompt = f"""Extract and REFORMAT quiz questions from the following text to make them self-contained and clear.

CRITICAL FILTERING RULES:
- SKIP questions that reference diagrams, images, figures, charts, or tables not included in text
- SKIP questions with "refer to the diagram", "see figure", "as shown in", "the image shows"
- SKIP questions where the answer cannot be determined from the text alone
- SKIP incomplete questions or questions missing answer options

CRITICAL REFORMATTING RULES:
- If a question or answer mentions "A and B", "both A and C", "options 1 and 3", etc., REWRITE it to use the actual content of those options
  Example: "Both A and B are correct" → "Both Authentication and Authorization are correct"
- If correct answer explanation says "options A and C", merge them into one clear statement
- Remove any references to option letters (A, B, C, D) in the question text or correct answer explanation
- Make questions completely standalone - no cross-references to other questions
- Ensure all pronouns and references are clear without external context

For each VALID question, return:
1. The question text (keep the number if present, make it clear and self-contained)
2. All answer options (A, B, C, D) - rewritten to be clear and independent
3. The correct answer letter (A, B, C, or D - must be exactly ONE letter)

Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "1. What are the main security mechanisms in web applications?",
    "options": ["Authentication and Authorization", "Encryption only", "Firewalls only", "None of the above"],
    "answer": "A"
  }}
]

VALIDATION RULES:
- Each question must be answerable without external references
- Options must be exactly 4 distinct choices in order A, B, C, D
- Answer must be a single letter: A, B, C, or D (not "A and B", not "both", just one letter)
- If original answer is "A and B are correct", combine them into option A and make that the answer
- Question text should NOT contain option letters like "option A" or "choice B"
- Return ONLY the JSON array, no other text
- If no valid questions found, return empty array: []

Text to process:
{text}"""

    try:
        print(f"  Processing with Gemini...")
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        questions = json.loads(response_text)
        print(f"  ✓ Extracted {len(questions)} questions")
        return questions
        
    except json.JSONDecodeError as e:
        print(f"  ✗ Error parsing JSON from Gemini response: {e}")
        print(f"  Response was: {response_text[:200]}...")
        return []
    except Exception as e:
        print(f"  ✗ Error with Gemini API: {e}")
        return []

def build_json_from_docs_with_gemini():
    """Build questions.json using Gemini to extract questions"""
    print("Building questions.json using Gemini AI...\n")
    
    all_questions = []
    
    for filename in os.listdir(DOCX_FOLDER):
        if filename.endswith(".docx"):
            print(f"Processing {filename}...")
            path = os.path.join(DOCX_FOLDER, filename)
            
            # Extract text from docx
            text = extract_text_from_docx(path)
            
            if not text:
                print(f"  ⚠ No text found in {filename}")
                continue
            
            # Use Gemini to extract questions
            questions = extract_questions_with_gemini(text, filename)
            all_questions.extend(questions)
            print()
    
    # Save to JSON
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Total questions extracted: {len(all_questions)}")
    print(f"✓ Saved to: {JSON_OUTPUT}")
    print(f"{'='*60}")

if __name__ == "__main__":
    build_json_from_docs_with_gemini()
