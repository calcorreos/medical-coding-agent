
import json
import os

def print_kv_summary():
    """Prints a key-value summary of results (Q#: Option)."""
    results_path = "data/final_results.json"
    
    if not os.path.exists(results_path):
        print("No results found.")
        return

    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
            
        # Sort by ID to ensure order
        results.sort(key=lambda x: int(x.get('id', 0)))
        
        print("\n=== FINAL ANSWER KEY SUMMARY ===")
        for q in results:
            print(f"Q{q.get('id')}: {q.get('selected_option')}")
        print("==============================\n")
        
    except Exception as e:
        print(f"Error reading results: {e}")

if __name__ == "__main__":
    print_kv_summary()
