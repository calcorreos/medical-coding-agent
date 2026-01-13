import json
import sys

def load_data():
    with open('final_results.json', 'r') as f:
        results = json.load(f)
    
    # We need the key's answers too. Assuming they are in good_questions.json OR we parse them again
    # Actually, final_results.json doesn't have the KEY's answer if it wasn't a 'good match'.
    # We need to re-parse the key or use a mapping. 
    # Let's rely on the fact that 'analyze_heuristic_results.py' did this comparison.
    # For simplicity, we'll reload the key parsing logic here.
    
    # Simplification: specific logic to load key answers (mocked or re-implemented)
    # Since I don't want to duplicate the PDF parsing code here, I will assume 
    # the user audit file 'audit_match_report.json' (if it exists) or similar has reliable key data.
    # Better yet, I will use the 'mismatch_report_audit.md' or similar previous artifacts to get the key?
    # No, let's just re-implement a lightweight key loader if possible or use the previously generated report.
    pass

# Refined approach: The user wants to see the mismatches.
# analyze_heuristic_results.py already identified them.
# Let's Modify verify_fix.py or similar to just dump the data structure with Key vs Agent.

def main():
    print("Loading Mismatch Report Data...")
    
    # Load all questions
    with open('questions.json', 'r') as f:
        questions = {str(q['id']): q for q in json.load(f)}
        
    # Load agent results
    with open('final_results.json', 'r') as f:
        agent_results = {str(q['id']): q for q in json.load(f)}
        
    # Load the Key (we'll just use the hardcoded mapping from previous steps if available, 
    # or quick-parse the key again? Or just ask the user? 
    # actually, analyze_heuristic_results.py parsed the key. Let's see if we can import that.)
    
    from analyze_heuristic_results import parse_answer_key_content
    key_answers = parse_answer_key_content("answer_key.pdf") # This might be slow/complex.
    
    # Filter for mismatches
    mismatches = []
    for qid, q_data in questions.items():
        agent_ans = agent_results.get(qid, {}).get('selected_option', '').strip().upper()
        key_ans = key_answers.get(qid, '').strip().upper()
        
        if agent_ans and key_ans and agent_ans != key_ans:
            mismatches.append({
                "id": qid,
                "question": q_data.get('question'),
                "options": q_data.get('options'),
                "agent_ans": agent_ans,
                "key_ans": key_ans,
                "rationale": agent_results.get(qid, {}).get('rationale')
            })
            
    print(f"\nFound {len(mismatches)} mismatches.\n")
    
    for i, m in enumerate(mismatches):
        print(f"[{i+1}/{len(mismatches)}] --- Question {m['id']} ---")
        print(f"Q: {m['question']}")
        print(f"Options: {m['options']}")
        print(f"KEY Says: {m['key_ans']}")
        print(f"AGENT Says: {m['agent_ans']}")
        print(f"\nAGENT Rationale:\n{m['rationale']}\n")
        
        choice = input("Action: (n)ext, (o)verride agent, (f)lag for review, (q)uit: ").lower().strip()
        
        if choice == 'q':
            break
        elif choice == 'o':
            new_ans = input("Enter correct answer (A/B/C/D): ").upper()
            note = input("Enter note/rationale for override: ")
            # In a real app, this would save the override.
            print(f"Recorded override: {new_ans} - {note}")
        elif choice == 'f':
            print("Flagged.")
        print("-" * 60)

if __name__ == "__main__":
    # Ensure dependencies
    try:
        import fitz
    except ImportError:
        print("Please run in environment with PyMuPDF installed.")
        # sys.exit(1) # Don't exit, maybe we can run without key parsing if needed? No, need key.
    
    main()
