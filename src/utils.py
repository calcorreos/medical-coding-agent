import os
import json
import logging
import re
from typing import List, Dict, Any
import fitz  # PyMuPDF

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MedicalCodingAgent")

def load_environment():
    """Load environment variables."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not found in environment variables. Functionality will be limited.")

def save_json(data: Any, filename: str):
    """Save data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    logger.info(f"Saved data to {filename}")

def load_json(filename: str) -> Any:
    """Load data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File {filename} not found.")
        return None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract full text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return ""

def parse_answer_key(pdf_path: str) -> Dict[str, str]:
    """
    Parses the answer key PDF to create a mapping of Question ID -> Correct Answer.
    Assumes a format where answers are listed clearly.
    This might need adjustment based on the actual PDF format.
    """
    text = extract_text_from_pdf(pdf_path)
    # Regex to find "1. ... Answer: A" pattern (allowing for newlines)
    # We look for the question number at the START OF A LINE, followed by non-digit characters,
    # then "Answer:" and the letter.
    # We use DOTALL to allow matching across lines, but we also want ^ to match start of line.
    matches = re.findall(r'(?m)^\s*(\d+)\..*?Answer:\s*([A-D])', text, re.DOTALL)
    
    if not matches:
        # Fallback: Try "1. A" simple format
        matches = re.findall(r'(?m)^\s*(\d+)\.\s*([A-D])', text)
        
    answer_key = {str(q_id): ans for q_id, ans in matches}
    
    # Clean up: If we have duplicate keys (e.g. from the Question section AND Answer section),
    # we want the one that actually had "Answer:" which acts as a filter in the first regex.
    # The first regex is specific enough that it likely only matches the Answer Key section
    # if the Question section doesn't have "Answer:" in it.
    
    logger.info(f"Parsed {len(answer_key)} answers from key.")
    return answer_key

def parse_answer_key_content(pdf_path: str) -> Dict[str, str]:
    """
    Parses the answer key PDF and returns a dictionary mapping
    Question ID -> Question Text (first 50 chars for fuzzy matching).
    """
    try:
        text = extract_text_from_pdf(pdf_path)
        content_map = {}
        
        # Regex to capture ID and the Question Text immediately following it
        # Pattern: "1. Question text here... Answer: A"
        # We capture up to the "Answer:" part or newline
        matches = re.findall(r"^(\d+)\.\s+(.*?)(?=\nAnswer:|\nExplanation:|\nMedical Coding Ace)", text, re.MULTILINE | re.DOTALL)
        
        for q_id, q_text in matches:
            # Clean up newlines and extra spaces
            clean_text = " ".join(q_text.strip().split())
            content_map[q_id] = clean_text
            
        logger.info(f"Parsed {len(content_map)} question texts from key.")
        return content_map
    except Exception as e:
        logger.error(f"Error parsing Answer Key Content: {e}")
        return {}
