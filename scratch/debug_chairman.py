import asyncio
from llm_council.config_helpers import _get_chairman_model
from llm_council.unified_config import get_config

async def main():
    print(f"Chairman from config_helpers: {_get_chairman_model()}")
    print(f"Chairman from unified_config: {get_config().council.chairman}")

if __name__ == "__main__":
    asyncio.run(main())
