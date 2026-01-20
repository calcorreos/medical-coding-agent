
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
        
        
        # Print to Terminal
        print("\n=== FINAL ANSWER KEY SUMMARY ===")
        for q in results:
            print(f"Q{q.get('id')}: {q.get('selected_option')}")
        print("==============================\n")

        # Export to CSV for Submission
        with open("submission_key.csv", "w") as f:
            f.write("Question,Answer\n")
            for q in results:
                f.write(f"{q.get('id')},{q.get('selected_option')}\n")
        print("Saved answer key to submission_key.csv")
        
    except Exception as e:
        print(f"Error reading results: {e}")

if __name__ == "__main__":
    print_kv_summary()

