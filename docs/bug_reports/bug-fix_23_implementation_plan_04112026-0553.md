# Bug Fix 023 Implementation Plan: Resolving Synthesis Failures

## First Principles Analysis
A council deliberation consists of three sequential stages. The third stage (Synthesis) relies on a "Chairman" model to summarize the previous two stages.
1.  **Truth 1**: A model request will fail if the identifier is not supported by the gateway provider.
2.  **Truth 2**: A model request will fail if the timeout is shorter than the time required for the model to generate a response.
3.  **Synthesis Complexity**: Synthesis is the most token-intensive operation in the pipeline because it must ingest the entire conversation history (Stage 1 and 2), requiring higher timeouts and very stable models.

## Proposed Changes
### 1. Model Identifier Hardening
Update the hardcoded defaults in `unified_config.py` and `tier_contract.py` to use:
- `google/gemini-2.0-flash-001` (Default Chairman)
- `openai/gpt-4o` (High-tier Aggregator)
- `anthropic/claude-3.7-sonnet` (Reasoning-tier Aggregator)

### 2. Timeout Restoration
- Increase default `per_model_timeout` in `run_stage3` from 30s to 90s.
- Update `mcp_server.py` to explicitly pass the tier's `per_model_timeout_ms` to `run_stage3`.

## Verification Plan
1.  Run `uv run pytest tests/test_council_integration.py` to ensure core orchestration remains intact.
2.  Run the `scratch/debug_chairman.py` script to confirm stable model selection.
