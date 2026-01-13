import json
import difflib
from utils import load_json, parse_answer_key_content, logger

def audit_alignment(questions_file="questions.json", answer_key_file="practice_test_answers (1) (3) (1).pdf"):
    print("Loading questions...")
    try:
        with open(questions_file, 'r') as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: {questions_file} not found.")
        return

    print("Parsing answer key content...")
    key_content_map = parse_answer_key_content(answer_key_file)
    
    matches = []
    mismatches = []
    
    print("Comparing content...")
    for q in questions:
        qid = str(q.get('id'))
        user_text = q.get('question', '').strip()
        
        if qid in key_content_map:
            key_text = key_content_map[qid]
            
            # Fuzzy match
            # Compare first 100 chars to avoid minor OCR diffs / formatting
            s = difflib.SequenceMatcher(None, user_text[:100], key_text[:100])
            ratio = s.ratio()
            
            is_match = ratio > 0.8
            
            item = {
                "id": qid,
                "question_text": user_text,
                "key_text": key_text,
                "match_score": ratio
            }
            
            if is_match:
                matches.append(item)
            else:
                mismatches.append(item)
        else:
            mismatches.append({
                "id": qid,
                "question_text": user_text,
                "key_text": "MISSING FROM KEY",
                "match_score": 0.0
            })
            
    # Generate Report
    report = "# Answer Key Alignment Audit\n\n"
    report += "This document lists which questions in the Practice Test align with the provided Answer Key.\n\n"
    report += f"**Total Questions**: {len(questions)}\n"
    report += f"**Matches**: {len(matches)}\n"
    report += f"**Mismatches**: {len(mismatches)}\n\n"
    
    report += "## Matches (Valid for Grading in Audit Score)\n"
    report += "| # | Question Text (Snippet) |\n"
    report += "|---|---|\n"
    for m in matches:
        snippet = " ".join(m['question_text'].split()[:15]) + "..."
        report += f"| {m['id']} | {snippet} |\n"
        
    report += "\n## Mismatches (Excluded from Audit Score)\n"
    # report += "These questions have radically different text in the Answer Key.\n\n"
    for m in mismatches:
        report += f"### Question {m['id']}\n"
        report += f"- **Test PDF**: {m['question_text']}\n"
        report += f"- **Answer Key**: {m['key_text']}\n\n"
        
    with open("audit_match_report.md", "w") as f:
        f.write(report)
        
    print(f"Audit complete. Matches: {len(matches)}, Mismatches: {len(mismatches)}")
    print("Report saved to audit_match_report.md")

if __name__ == "__main__":
    audit_alignment()
