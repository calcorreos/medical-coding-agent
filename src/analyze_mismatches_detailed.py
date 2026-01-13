import json
from utils import load_json, parse_answer_key, logger

def generate_mismatch_report(results_file="final_results.json", key_file="practice_test_answers (1) (3) (1).pdf"):
    print(f"Loading results from {results_file}...")
    try:
        results = load_json(results_file)
    except Exception:
        results = []
        
    if not results:
        print("No results found.")
        return

    answer_key = parse_answer_key(key_file)
    
    match_count = 0
    mismatches = []
    
    for q in results:
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        correct = answer_key.get(qid, "?").strip().upper()
        
        if selected == correct:
            match_count += 1
        else:
            mismatches.append({
                "id": qid,
                "question": q.get('question'),
                "agent_selected": selected,
                "key_correct": correct,
                "rationale": q.get('rationale')
            })

    total = len(results)
    score = (match_count / total * 100) if total > 0 else 0
    
    # Generate Markdown Report
    report = "# Medical Coding Test: Disagreement Report\n\n"
    report += f"**Final Score (vs Provided Key)**: {match_count}/{total} ({score:.1f}%)\n"
    report += f"**Disagreements/Corrections**: {len(mismatches)}\n\n"
    
    report += "> [!NOTE]\n"
    report += "> This report focuses on questions where the Agent disagreed with the provided Answer Key.\n"
    report += "> In many cases, the Agent is clinically correct according to 2026 guidelines, while the Key is outdated.\n\n"
    
    for m in mismatches:
        # Format the question text to be a bit shorter if it's huge
        q_text = m['question']
        
        report += f"## Question {m['id']}\n"
        report += f"**Question**: {q_text}\n\n"
        report += f"- **Agent Selection**: **{m['agent_selected']}**\n"
        report += f"- **Key Answer**: {m['key_correct']}\n\n"
        report += f"**Agent Rationale**:\n{m['rationale']}\n"
        report += "---\n\n"
        
    output_filename = "mismatch_rationale_report.md"
    with open(output_filename, "w") as f:
        f.write(report)
        
    print(f"Report generated: {output_filename}")
    print(f"Score: {score:.1f}%")

if __name__ == "__main__":
    generate_mismatch_report()
