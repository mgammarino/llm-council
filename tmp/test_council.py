import asyncio
import json
from llm_council.council import run_full_council

async def main():
    print("Asking the council...")
    # Bypass cache so it does a fresh run and aggregates costs
    _, _, final_response, metadata = await run_full_council(
        user_query="What is the difference between latency and throughput?",
        bypass_cache=True
    )
    
    print("\n--- FINAL ANSWER ---")
    print(final_response["response"])
    print("\n--- RAW METADATA (WITH COSTS) ---")
    print(json.dumps(metadata, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
