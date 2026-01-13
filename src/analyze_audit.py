import json
from utils import load_json, parse_answer_key, logger

def analyze_audit(results_file="final_results.json", key_file="practice_test_answers (1) (3) (1).pdf"):
    print(f"Loading results from {results_file}...")
    results = load_json(results_file)
    if not results:
        print("No results found.")
        return

    answer_key = parse_answer_key(key_file)
    
    good_questions = []
    bad_questions = []
    
    match_count = 0
    
    for q in results:
        qid = str(q.get('id'))
        selected = q.get('selected_option', '').strip().upper()
        correct = answer_key.get(qid, "?").strip().upper()
        
        # Check agreement
        if selected == correct:
            match_count += 1
            good_questions.append({
                "id": qid,
                "question": q.get('question'),
                "options": q.get('options'),
                "correct_option": correct,
                "rationale": q.get('rationale')
            })
        else:
            bad_questions.append({
                "id": qid,
                "question": q.get('question'),
                "agent_selected": selected,
                "key_correct": correct,
                "rationale": q.get('rationale')
            })
            
    print(f"\nAnalysis Complete:")
    print(f"Total Processed: {len(results)}")
    print(f"Agreed Matches (Good Data): {match_count}")
    print(f"Disagreements (Potential Bad Key/Agent Error): {len(bad_questions)}")
    
    # Save Good Questions
    with open("good_questions.json", "w") as f:
        json.dump(good_questions, f, indent=2)
    print("Saved 'good_questions.json'")
    
    # Save Disagreements for Review
    with open("disagreement_analysis.json", "w") as f:
        json.dump(bad_questions, f, indent=2)
    print("Saved 'disagreement_analysis.json'")
    
    # Suggest Next Steps
    accuracy = (match_count / len(results) * 100) if results else 0
    print(f"Current Agreement Rate: {accuracy:.1f}%")

if __name__ == "__main__":
    analyze_audit()
