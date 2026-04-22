import json
from unittest.mock import AsyncMock, patch

import pytest
from llm_council.mcp_server import start_council, council_review, council_synthesize
from llm_council.verdict import VerdictType

@pytest.mark.asyncio
async def test_start_council_parity_params():
    """Test start_council passes all new parity parameters to internal functions."""
    query = "test query"
    
    # Mocking internal orchestrator and session store
    with patch("llm_council.mcp_server.run_stage1") as mock_stage1, \
         patch("llm_council.mcp_server.create_session") as mock_create_session, \
         patch("llm_council.mcp_server.create_tier_contract") as mock_create_contract:
        
        mock_stage1.return_value = {"stage1_results": [], "requested_models": 2, "usage": {}}
        mock_create_session.return_value = "session-123"
        
        await start_council(
            query=query,
            confidence="quick",
            model_count=2,
            bypass_cache=True,
            allow_preview=True
        )
        
        # Verify TierContract creation got the new params
        mock_create_contract.assert_called_once_with(
            "quick", 
            model_count=2, 
            allow_preview=True
        )
        
        # Verify run_stage1 got the cache bypass
        mock_stage1.assert_called_once()
        kwargs = mock_stage1.call_args.kwargs
        assert kwargs["bypass_cache"] is True
        
        # Verify session persistence got all params
        mock_create_session.assert_called_once()
        s_kwargs = mock_create_session.call_args.kwargs
        assert s_kwargs["model_count"] == 2
        assert s_kwargs["allow_preview"] is True

@pytest.mark.asyncio
async def test_council_review_preserves_params():
    """Test council_review re-uses persisted parity params when recreating contracts."""
    session_id = "session-123"
    mock_session = {
        "query": "test query",
        "tier": "quick",
        "model_count": 2,
        "allow_preview": True,
        "stage": "stage1_complete",
        "stage1": {"stage1_results": [], "usage": {}}
    }
    
    with patch("llm_council.mcp_server.load_session", return_value=mock_session), \
         patch("llm_council.mcp_server.run_stage2") as mock_stage2, \
         patch("llm_council.mcp_server.save_session"), \
         patch("llm_council.mcp_server.create_tier_contract") as mock_create_contract:
        
        mock_stage2.return_value = {"aggregate_rankings": [], "usage": {}}
        
        await council_review(session_id=session_id)
        
        # Verify contract recreation in Tier 2 respects Tier 1 settings
        mock_create_contract.assert_called_once_with(
            "quick",
            model_count=2,
            allow_preview=True
        )

@pytest.mark.asyncio
async def test_council_synthesize_verdict_params():
    """Test council_synthesize handles verdict_type and dissent flags."""
    session_id = "session-123"
    mock_session = {
        "query": "test query",
        "tier": "balanced",
        "stage": "stage2_complete",
        "stage1": {"usage": {}, "stage1_results": []},
        "stage2": {
            "usage": {}, 
            "stage2_results": [], 
            "aggregate_rankings": [],
            "label_to_model": {}
        }
    }
    
    with patch("llm_council.mcp_server.load_session", return_value=mock_session), \
         patch("llm_council.mcp_server.run_stage3") as mock_stage3, \
         patch("llm_council.mcp_server.create_tier_contract"), \
         patch("llm_council.mcp_server.close_session"):
        
        mock_stage3.return_value = {
            "chairman_result": {"response": "Synthesized verdict"}, 
            "usage": {}
        }
        
        await council_synthesize(
            session_id=session_id,
            verdict_type="binary",
            include_dissent=False
        )
        
        # Verify run_stage3 received the correct enum and flag
        mock_stage3.assert_called_once()
        kwargs = mock_stage3.call_args.kwargs
        assert kwargs["verdict_type"] == VerdictType.BINARY
        assert kwargs["include_dissent"] is False
