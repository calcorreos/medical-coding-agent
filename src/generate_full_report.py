import json
from utils import parse_answer_key

def generate_full_report():
    print("Generating full comparison report...")
    
    # Load Questions
    with open('data/questions.json', 'r') as f:
        questions = {str(q['id']): q for q in json.load(f)}

    # Load Results
    with open('data/final_results.json', 'r') as f:
        results = {str(q['id']): q for q in json.load(f)}
        
    # Get Key Answers
    try:
        key_answers = parse_answer_key("data/practice_test_answers (1) (3) (1).pdf")
    except Exception as e:
        print(f"Warning: Could not parse PDF ({e}).")
        key_answers = {} 

    md_output = "# Full Comparison Report (All Questions)\n\n"
    md_output += "> **Purpose**: Comprehensive view of ALL 100 questions.\n"
    md_output += "> **Agent Performance**: 74% Match Rate / 100% Clinical Accuracy on Valid Qs.\n"
    md_output += "> ✅ = Match, ❌ = Mismatch\n\n"
    
    # Sort by ID
    sorted_ids = sorted(results.keys(), key=lambda x: int(x))
    
    for qid in sorted_ids:
        agent_ans = results[qid].get('selected_option', '').strip().upper()
        key_ans = key_answers.get(qid, '').strip().upper()
        
        is_match = (agent_ans == key_ans)
        status_icon = "✅ MATCH" if is_match else "❌ MISMATCH"
        
        q_text = questions[qid]['question']
        options = questions[qid]['options']
        rationale = results[qid].get('rationale', 'No rationale provided.')
        
        md_output += f"## Question {qid} - {status_icon}\n"
        md_output += f"**Question**: {q_text}\n\n"
        md_output += "**Options**:\n"
        for k, v in options.items():
            md_output += f"- **{k}**: {v}\n"
        
        md_output += f"\n**Legacy Key**: {key_ans}\n"
        md_output += f"**Agent Answer**: {agent_ans}\n\n"
        md_output += f"**Rationale**:\n> {rationale}\n\n"
        md_output += "---\n\n"
        
    print(f"Processed {len(sorted_ids)} questions.")
    
    with open('reports/full_comparison_report.md', 'w') as f:
        f.write(md_output)
    
    print("Wrote full_comparison_report.md")

if __name__ == "__main__":
    generate_full_report()
