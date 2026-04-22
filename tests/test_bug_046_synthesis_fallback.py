import pytest
import asyncio
from unittest.mock import patch, MagicMock
from llm_council.stages.stage3 import stage3_synthesize_final, VerdictType

@pytest.mark.asyncio
async def test_bug_046_synthesis_fallback_verified():
    """
    BUG-046: Verify that Stage 3 now correctly falls back to a 'quick' model on 403.
    """
    # Mock the query_model to simulate 403 first, then success on fallback
    with patch("llm_council.stages.stage3.query_model") as mock_query:
        # 1. Primary Chairman returns None (restricted)
        # 2. Fallback Chairman returns success
        mock_query.side_effect = [
            None,
            {"content": "Consensus reached via fallback.", "usage": {"total_cost": 0.001}}
        ]
        
        result, usage, verdict = await stage3_synthesize_final(
            user_query="test query",
            stage1_results=[{"model": "m1", "response": "r1"}],
            stage2_results=[{"model": "m1", "ranking": "rank1"}],
            verdict_type=VerdictType.SYNTHESIS
        )
        
        assert "fallback" in result["response"]
        assert mock_query.call_count == 2
        print(f"\nVerified BUG-046 Success: Synthesis automatically shifted to fallback model.")

if __name__ == "__main__":
    asyncio.run(test_bug_046_synthesis_fallback_repro())
