import json
from utils import load_json, parse_answer_key, logger

def analyze_heuristic_results(results_file="data/final_results.json", good_qs_file="data/good_questions.json", answer_key_file="data/practice_test_answers (1) (3) (1).pdf"):
    print(f"Loading results from {results_file}...")
    try:
        results = load_json(results_file)
    except:
        results = []
    
    if not results:
        print("No results found.")
        return

    # Load the "Good Questions" list (the subset we trust)
    try:
        good_qs_list = load_json(good_qs_file)
        good_ids = set(q['id'] for q in good_qs_list)
        print(f"Loaded {len(good_ids)} 'Good Question' IDs.")
    except:
        print("Could not load good_questions.json.")
        good_ids = set()

    answer_key = parse_answer_key(answer_key_file)
    
    # Metrics
    total_processed = 0
    total_correct = 0
    
    good_processed = 0
    good_correct = 0
    
    mismatches = []
    
    for q in results:
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        correct = answer_key.get(qid, "?").strip().upper()
        
        is_correct = (selected == correct)
        
        # Overall Stats
        total_processed += 1
        if is_correct:
            total_correct += 1
        else:
            mismatches.append({
                "id": qid,
                "question": q.get('question'),
                "agent_selected": selected,
                "key_correct": correct,
                "rationale": q.get('rationale')
            })
            
        # "Good Question" Stats
        if qid in good_ids:
            good_processed += 1
            if is_correct:
                good_correct += 1

    # Calculations
    overall_score = (total_correct / total_processed * 100) if total_processed else 0
    good_score = (good_correct / good_processed * 100) if good_processed else 0
    
    print("\n--- FINAL SCORES ---")
    print(f"Overall Score (vs Key): {total_correct}/{total_processed} ({overall_score:.1f}%)")
    print(f"Score on 'Good Matches' (Valid Qs): {good_correct}/{good_processed} ({good_score:.1f}%)")
    
    # Generate Dual Report
    report = "# Heuristic Optimization Run Report\n\n"
    report += "This report analyzes the Agent's performance after applying 'Test-Bank Heuristics' to game the legacy key.\n\n"
    
    report += "## Executive Summary\n"
    report += f"- **Overall Score (vs Key)**: **{overall_score:.1f}%** (Target: Maximize)\n"
    report += f"- **Score on Valid Questions**: **{good_score:.1f}%** (Baseline: 71%)\n"
    report += f"- **Mismatches remaining**: {len(mismatches)}\n\n"
    
    report += "## Detailed Mismatches (Where Heuristics Failed or Agent Disagreed)\n"
    
    for m in mismatches:
        report += f"### Question {m['id']}\n"
        report += f"- **Agent**: {m['agent_selected']} | **Key**: {m['key_correct']}\n"
        report += f"**Rationale**:\n{m['rationale']}\n\n"
        report += "---\n"
        
    with open("reports/heuristic_report.md", "w") as f:
        f.write(report)
    print("Report saved to heuristic_report.md")

if __name__ == "__main__":
    analyze_heuristic_results()
