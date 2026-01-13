import json

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def identify_regressions():
    # Load the "Gold Standard" subset (Questions we expect to get right)
    good_qs = load_json('good_questions.json')
    good_map = {str(q['id']): q['correct_option'] for q in good_qs}
    
    # Load the latest results
    results = load_json('final_results.json')
    results_map = {str(q['id']): q for q in results}
    
    missed_qs = []
    
    for qid, correct_ans in good_map.items():
        if qid in results_map:
            agent_ans = results_map[qid].get('selected_option', '').strip().upper()
            if agent_ans != correct_ans:
                missed_qs.append({
                    "id": qid,
                    "question": results_map[qid].get('question')[:100] + "...",
                    "expected": correct_ans,
                    "agent_got": agent_ans,
                    "rationale": results_map[qid].get('rationale')
                })
                
    print(f"Found {len(missed_qs)} regressions on valid questions.")
    
    report = "# Regressions on Valid Questions\n\n"
    for m in missed_qs:
        report += f"## Question {m['id']}\n"
        report += f"**Expected**: {m['expected']} | **Agent Got**: {m['agent_got']}\n"
        report += f"**Rationale**:\n{m['rationale']}\n\n"
        print(f"Q{m['id']}: Expected {m['expected']}, Agent got {m['agent_got']}")
        
    with open("regressions.md", "w") as f:
        f.write(report)

if __name__ == "__main__":
    identify_regressions()
