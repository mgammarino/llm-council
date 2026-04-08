import asyncio
import os
import httpx
from llm_council.gateway.openrouter import OpenRouterGateway
from llm_council.gateway.types import GatewayRequest, CanonicalMessage

async def main():
    gateway = OpenRouterGateway()
    request = GatewayRequest(
        model="google/gemini-pro-1.5",
        messages=[CanonicalMessage(role="user", content="Hi")],
        timeout=30
    )
    
    # We need to reach into the private method to see the raw usage dict
    # or just look at the returned usage which is already mapped.
    # Actually, let's just make a raw request to OpenRouter to be sure.
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set")
        return

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": "hello"}]
            },
            timeout=30
        )
        data = response.json()
        print("Raw Usage:", json.dumps(data.get("usage", {}), indent=2))

if __name__ == "__main__":
    import json
    asyncio.run(main())
