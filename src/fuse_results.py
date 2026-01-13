import json

def fuse_results():
    # Load original results
    with open('data/final_results.json', 'r') as f:
        results = json.load(f)
        
    # Load verified results
    with open('data/verification_results.json', 'r') as f:
        verified_data = json.load(f)
        
    # Create lookup map
    verification_map = {str(item['id']): item for item in verified_data}
        
    # Override
    print("Fusing verified results...")
    
    updated_count = 0
    for q in results:
        qid = str(q['id'])
        if qid in verification_map:
            # Update fields
            q['selected_option'] = verification_map[qid]['selected_option']
            q['rationale'] = verification_map[qid]['rationale'] + " [HEURISTIC UPDATE]"
            q['research_notes'] = verification_map[qid].get('research_notes', q.get('research_notes'))
            
            updated_count += 1
            print(f"Updated Q{qid} to {q['selected_option']}")
            
    with open('data/final_results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Successfully fused {updated_count} results.")

if __name__ == "__main__":
    fuse_results()
