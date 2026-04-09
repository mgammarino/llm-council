import pytest
from unittest.mock import AsyncMock, patch
from llm_council.council import run_council_with_fallback, VerdictType


@pytest.mark.anyio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_council_aggregates_total_cost(anyio_backend):
    if anyio_backend == "trio":
        pytest.xfail("run_council_with_fallback uses asyncio.wait_for/create_task — trio incompatible")
    # Mock all stages to return specific usage with costs
    # Stage 1
    mock_stage1 = (
        [{"model": "m1", "response": "r1"}],
        {"total_cost": 0.1, "total_tokens": 100},
        {"m1": {"status": "ok"}},
    )
    # Stage 1.5
    mock_stage1_5 = (
        [{"model": "m1", "response": "r1_norm"}],
        {"total_cost": 0.05, "total_tokens": 50},
    )
    # Stage 2
    mock_stage2 = ([], {}, {"total_cost": 0.2, "total_tokens": 200})
    # Stage 3
    mock_stage3 = ({"response": "final"}, {"total_cost": 0.15, "total_tokens": 150}, None)

    with (
        patch(
            "llm_council.council.stage1_collect_responses_with_status",
            AsyncMock(return_value=mock_stage1),
        ),
        patch(
            "llm_council.council.stage1_5_normalize_styles", AsyncMock(return_value=mock_stage1_5)
        ),
        patch("llm_council.council.stage2_collect_rankings", AsyncMock(return_value=mock_stage2)),
        patch("llm_council.council.stage3_synthesize_final", AsyncMock(return_value=mock_stage3)),
        patch("llm_council.council.persist_session_bias_data"),
        patch("llm_council.council._get_council_models", return_value=["m1"]),
        patch("llm_council.council.get_telemetry"),
        patch("llm_council.council.emit_layer_event"),
    ):
        result = await run_council_with_fallback("test query")

        # 0.1 (S1) + 0.05 (S1.5) + 0.2 (S2) + 0.15 (S3) = 0.5
        assert result["metadata"]["usage"]["total_cost"] == 0.5
        assert result["metadata"]["usage"]["stages"]["stage1"]["total_cost"] == 0.1
        assert result["metadata"]["usage"]["stages"]["stage3"]["total_cost"] == 0.15
