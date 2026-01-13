
from utils import extract_text_from_pdf, parse_answer_key
import os

pdf_path = "practice_test_answers (1) (3) (1).pdf"

if os.path.exists(pdf_path):
    print(f"Reading {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    print("--- RAW TEXT START ---")
    print(text[:500]) # First 500 chars
    print("--- ... ---")
    print(text[-500:]) # Last 500 chars
    print("--- RAW TEXT END ---")
    
    answers = parse_answer_key(pdf_path)
    print("\nParsed Answers:")
    print(answers)
    print(f"Total Parsed: {len(answers)}")
else:
    print("File not found.")
