import pytest
from unittest.mock import AsyncMock, patch
from llm_council.stages.stage3 import run_stage3
from llm_council.verdict import VerdictType

@pytest.mark.asyncio
async def test_stage3_timeout_propagation():
    """Verify that Stage 3 uses the provided per_model_timeout."""
    mock_stage1 = {"stage1_results": [], "usage": {}}
    mock_stage2 = {"stage2_results": [], "aggregate_rankings": [], "usage": {}}
    
    with patch("llm_council.stages.stage3.stage3_synthesize_final", new_callable=AsyncMock) as mock_synth:
        mock_synth.return_value = ({"response": "ok"}, {}, None)
        
        # Test with explicit timeout
        await run_stage3(
            "query", 
            mock_stage1, 
            mock_stage2, 
            per_model_timeout=45
        )
        
        # Check if the mock was called with the correct timeout
        args, kwargs = mock_synth.call_args
        assert kwargs["timeout"] == 45

@pytest.mark.asyncio
async def test_stage3_default_timeout_is_90():
    """Verify that Stage 3 default timeout is now 90s (Bug Fix #34)."""
    mock_stage1 = {"stage1_results": [], "usage": {}}
    mock_stage2 = {"stage2_results": [], "aggregate_rankings": [], "usage": {}}
    
    with patch("llm_council.stages.stage3.stage3_synthesize_final", new_callable=AsyncMock) as mock_synth:
        mock_synth.return_value = ({"response": "ok"}, {}, None)
        
        await run_stage3("query", mock_stage1, mock_stage2)
        
        args, kwargs = mock_synth.call_args
        assert kwargs["timeout"] == 90
