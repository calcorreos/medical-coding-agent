import os
from google import genai
from utils import load_environment

def list_models():
    load_environment()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    print("Listing models...")
    for model in client.models.list(config={"page_size": 100}):
        print(f"Model: {model.name}")
        print(f"  DisplayName: {model.display_name}")
        print(f"  SupportedActions: {model.supported_actions}")
        print("-" * 20)

if __name__ == "__main__":
    list_models()
