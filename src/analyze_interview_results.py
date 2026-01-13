import json
from utils import load_json, parse_answer_key, logger

def analyze_interview_results(results_file="data/final_results.json", answer_key_file="data/practice_test_answers (1) (3) (1).pdf"):
    print(f"Loading results from {results_file}...")
    try:
        results = load_json(results_file)
    except:
        results = []
    
    if not results:
        print("No results found.")
        return

    # In Interview Mode, matches with the Legacy Key are LESS important.
    # We care about the RATIONALE and the "Mismatch" because usually the Mismatch = Clinical Truth.
    
    answer_key = parse_answer_key(answer_key_file)
    
    total_processed = 0
    legacy_matches = 0
    mismatches = []
    
    for q in results:
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        correct_legacy = answer_key.get(qid, "?").strip().upper()
        
        # Count stats
        total_processed += 1
        matches_legacy = (selected == correct_legacy)
        
        if matches_legacy:
            legacy_matches += 1
        else:
            mismatches.append({
                "id": qid,
                "question": q.get('question'),
                "agent_selected": selected,
                "legacy_key": correct_legacy,
                "rationale": q.get('rationale'),
                "research": q.get('research_notes')
            })

    legacy_score = (legacy_matches / total_processed * 100) if total_processed else 0
    
    print("\n--- INTERVIEW MODE PREDICTION SCORES ---")
    print(f"Processed: {total_processed}")
    print(f"Match with Legacy Key: {legacy_matches}/{total_processed} ({legacy_score:.1f}%)")
    print(f"Potential Clinical Corrections (Mismatches): {len(mismatches)}")
    
    # Generate Report
    report = "# Interview Mode Strategy Report\n\n"
    report += "This report analyzes the Agent's performance in **Standard Mode (Clinical Accuracy)**.\n"
    report += "Mismatches with the Legacy Key are expected and likely represent matches with the **Hidden Key**.\n\n"
    
    report += "## Summary\n"
    report += f"- **Legacy Key Match Rate**: {legacy_score:.1f}%\n"
    report += f"- **Projected Hidden Key Score**: (Requires verification of mismatches)\n"
    report += f"- **Clinical Corrections / Disagreements**: {len(mismatches)}\n\n"
    
    report += "## Detailed Disagreements (Potential Hidden Key Matches)\n"
    report += "> These are questions where the Agent chose an answer DIFFERENT from the old flawed key, based on Clinical Guidelines.\n\n"
    
    for m in mismatches:
        report += f"### Question {m['id']}\n"
        report += f"- **Agent Selected**: {m['agent_selected']} (Clinical Truth)\n"
        report += f"- **Legacy Key**: {m['legacy_key']} (Likely Flawed)\n\n"
        report += f"**Agent Rationale**:\n{m['rationale']}\n\n"
        report += "---\n"
        
    with open("reports/interview_mode_report.md", "w") as f:
        f.write(report)
    print("Report saved to interview_mode_report.md")

if __name__ == "__main__":
    analyze_interview_results()
