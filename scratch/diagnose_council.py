import asyncio
from llm_council.council import run_council_with_fallback
from unittest.mock import patch

async def diagnose():
    mock_stage1 = [{"model": "a", "response": "A"}, {"model": "b", "response": "B"}]
    mock_stage2 = [{"model": "a", "ranking": "R", "parsed_ranking": {}}]
    mock_stage3 = {"model": "chair", "response": "Full synthesis"}
    
    with (
        patch("llm_council.council.stage1_collect_responses_with_status") as mock_s1,
        patch("llm_council.council.stage1_5_normalize_styles") as mock_s15,
        patch("llm_council.council.stage2_collect_rankings") as mock_s2,
        patch("llm_council.council.stage3_synthesize_final") as mock_s3,
        patch("llm_council.council.calculate_aggregate_rankings") as mock_agg,
        patch("llm_council.council._get_council_models", return_value=["a", "b"]),
    ):
        mock_s1.return_value = (mock_stage1, {}, {"a": {"status": "ok"}, "b": {"status": "ok"}})
        mock_s15.return_value = (mock_stage1, {})
        mock_s2.return_value = (mock_stage2, {"Response A": "a"}, {})
        mock_s3.return_value = (mock_stage3, {}, None)
        mock_agg.return_value = []

        result = await run_council_with_fallback("test")
        print(f"STATUS: {result['metadata']['status']}")
        print(f"SYNTHESIS: {result['synthesis']}")

if __name__ == "__main__":
    asyncio.run(diagnose())
