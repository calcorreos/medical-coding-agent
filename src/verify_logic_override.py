
import json
import os
from agents import ExpertAgent, EvaluatorAgent, ParserAgent
from utils import logger

def verify_logic_override():
    # Only verify key questions for the logic override (The "Known Legacy Traps")
    target_ids = ["17", "43", "46", "47", "57", "59", "62", "65"] 
    # Q17: Mucocele (Mucocele vs FB)
    # Q43: Nosebleed (Anatomy)
    # Q46: Osteoarthritis (Specificity)
    # Q47: Sinusitis (Anatomy/Pathogen)
    # Q57: Thigh Abscess (Anatomy)
    # Q59: Hematoma (Anatomy)
    # Q62: Wart (Pathology)
    # Q65: Knee Anesthesia (Specificity)

    # Mock Data (since we don't want to re-parse everything if not needed, but reading from input is safer)
    
    agent_mode = os.environ.get("AGENT_MODE", "STANDARD")
    print(f"Running Logic Override Verification in Mode: {agent_mode}")

    # Initialize Agents
    expert = ExpertAgent()
    evaluator = EvaluatorAgent()
    parser = ParserAgent()

    # Read Questions (cached or parse)
    questions = []
    try:
        with open("data/questions.json", "r") as f:
            questions = json.load(f)
    except FileNotFoundError:
        print("Questions file not found. Please ensure data/questions.json exists.")
        return

    results = []
    
    for q in questions:
        if str(q['id']) in target_ids:
            print(f"\nProcessing Q{q['id']}...")
            
            # 1. Research
            notes = expert.research(q)
            
            # 2. Evaluate
            result = evaluator.evaluate(q, notes)
            result['id'] = q['id']
            # Add Question Text for reference in report
            result['question_text'] = q['question']
            results.append(result)
            
            print(f"Selected: {result.get('selected_option')}")
            # print(f"Rationale: {result.get('rationale')}")
            
            # Check for Mandatory Rationale
            if "Clinical Superiority" in result.get('rationale', '') or "Legacy Key" in result.get('rationale', ''):
                 print("✅ Mandatory Rationale Detect: PASS")
            else:
                 print("⚠️ Mandatory Rationale Detect: FAIL")

    # Save Results
    with open("data/logic_override_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nResults saved to data/logic_override_results.json")

if __name__ == "__main__":
    verify_logic_override()
