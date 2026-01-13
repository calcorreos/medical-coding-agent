import os
import time
import asyncio
from google import genai
from utils import load_environment

async def test_request(client, i):
    print(f"Sending request {i}...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", # Trying the model we want to use
            contents="Say 'check' and nothing else."
        )
        print(f"Request {i} success: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"Request {i} failed: {e}")
        return False

async def main():
    load_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API key found.")
        return

    client = genai.Client(api_key=api_key)
    
    print("Starting burst test (10 requests in parallel)...")
    tasks = [test_request(client, i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(results)
    print(f"Success/Total: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("Verdict: HIGH limits confirmed (Paid Tier likely active).")
    else:
        print("Verdict: LOW limits detected (Free Tier or Model Limitation).")

if __name__ == "__main__":
    asyncio.run(main())
