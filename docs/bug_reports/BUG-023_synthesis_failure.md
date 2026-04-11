# Bug Report: BUG-023 Synthesis Failure

## Issue Description
Chain deliberation fails at Stage 3 (Synthesis) with the error "Unable to generate final synthesis."

## Root Cause Analysis
1.  **Invalid Model Defaults**: The system defaulted the `CHAIRMAN_MODEL` to `google/gemini-3.1-pro-preview` and certain tier aggregators to `openai/gpt-5.4`. These models are currently not available on OpenRouter, resulting in HTTP 402/404 errors.
2.  **Synthesis Timeout Regression**: Stage 3 was incorrectly defaulting to a 30-second timeout. Large council deliberatons (summarizing multiple model outputs) frequently exceed 30 seconds, causing the chairman request to be aborted.

## Verification Strategy (Proving the Fix)
1.  **Configuration Check**: Verify that `_get_chairman_model()` returns a currently available stable model (e.g., `gemini-2.0-flash-001`).
2.  **Timeout Check**: Verify that `run_stage3` and `mcp_server.py` pass a 90-second timeout for synthesis requests.
3.  **End-to-End Simulation**: Run a council session with a complex query and confirm Stage 3 completes successfully.

## Affected Components
- `src/llm_council/unified_config.py` (Default model identifiers)
- `src/llm_council/tier_contract.py` (Tier aggregation models)
- `src/llm_council/stages/stage3.py` (Default timeout)
- `src/llm_council/mcp_server.py` (Timeout propagation)
