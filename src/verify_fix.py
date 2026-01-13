import json
from agents import configure_genai, ExpertAgent, EvaluatorAgent, logger

def verify_fix(target_ids=['17', '32', '41', '46', '47', '50', '62', '64']):
    configure_genai()
    
    # Load questions
    with open("data/questions.json", "r") as f:
        all_qs = json.load(f)
        
    targets = [q for q in all_qs if str(q['id']) in target_ids]
    
    expert = ExpertAgent()
    evaluator = EvaluatorAgent()
    
    results = []
    
    for q in targets:
        print(f"\nProcessing Q{q['id']}...")
        research = expert.research(q)
        q['research_notes'] = research # Embed research
        answer = evaluator.evaluate(q, research)
        
        results.append({
            "id": q['id'],
            "question": q['question'],
            "options": q['options'],
            "research_notes": research,
            "selected_option": answer.get('selected_option'),
            "rationale": answer.get('rationale')
        })
        print(f"Result Q{q['id']}: {answer.get('selected_option')}")
        
    print("\n--- Saving Verification Results ---")
    with open("data/verification_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Saved to data/verification_results.json")

if __name__ == "__main__":
    verify_fix()
