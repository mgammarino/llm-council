import pytest
import asyncio
from unittest.mock import patch, MagicMock
from llm_council.stages.stage1 import run_stage1

@pytest.mark.asyncio
async def test_bypass_cache_wiring_verified():
    """
    BUG-045: Verify that run_stage1() now accepts bypass_cache=True and propagates it.
    """
    # Mock the orchestration wrapper in stage1 to verify propagation
    with patch("llm_council.stages.stage1.query_models_with_progress") as mock_query:
        # Mocking the response to simulate Stage 1 completion
        mock_query.return_value = {}
        
        await run_stage1(
            user_query="test query",
            bypass_cache=True,
            council_models=["test/model"]
        )
        
        # Verify it was called with the flag
        args, kwargs = mock_query.call_args
        assert kwargs.get("bypass_cache") is True
        print(f"\nVerified BUG-045: bypass_cache correctly propagated to adapter.")

if __name__ == "__main__":
    asyncio.run(test_bug_045_repro())
