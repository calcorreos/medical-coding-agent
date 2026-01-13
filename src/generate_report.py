import json
import os
from utils import load_json, parse_answer_key, logger

def generate_report(output_file="final_results.json", pdf_key="practice_test_answers (1) (3) (1).pdf"):
    results = load_json(output_file)
    if not results:
        print("No results found.")
        return

    answer_key = parse_answer_key(pdf_key)
    
    report = "# Medical Coding Practice Test Walkthrough\n\n"
    report += "**Batch Verification**: Q11-Q20\n"
    report += "**Date**: 2026-01-13\n\n"
    
    correct_count = 0
    total = 0
    
    for q in results:
        # Filter for the batch we just ran (roughly ID 11-20 if ids match, but results list is just what we ran)
        # We just process all in results for now.
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        
        # Grading
        correct_answer = answer_key.get(qid, "?")
        is_correct = (selected == correct_answer)
        if is_correct:
            correct_count += 1
        total += 1
        
        icon = "✅" if is_correct else "❌"
        
        report += f"## Question {qid} {icon}\n"
        report += f"**Question**: {q.get('question')}\n\n"
        report += f"**Selected**: {selected}\n"
        report += f"**Correct (Key)**: {correct_answer}\n\n"
        
        if not is_correct:
             report += f"**Self-Reflection**: {q.get('self_reflection', 'N/A')}\n\n"
             
        report += f"**Rationale**: {q.get('rationale')}\n\n"
        report += f"**Research Notes**:\n{q.get('research_notes')}\n\n"
        report += "---\n\n"

    score_pct = (correct_count / total * 100) if total > 0 else 0
    print(f"Generated Score: {correct_count}/{total} ({score_pct:.1f}%)")
    
    with open("walkthrough.md", "w") as f:
        f.write(report)

if __name__ == "__main__":
    generate_report()
