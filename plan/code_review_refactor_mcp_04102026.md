# Code Review & Refactor Plan: MCP Parity & Reliability

Review of staged changes for Issue #26 (3-stage MCP flow persistence and telemetry).

## User Review Required

> [!IMPORTANT]
> The refactor extracts progress reporting logic into a unified helper `_get_progress_callback` in `mcp_server.py`. This uses `asyncio.create_task` in production to avoid pipe-blocking deadlocks (ADR-012). Ensure this fire-and-forget behavior is acceptable for your production environment.

## Proposed Changes

### [llm_council]

#### [MODIFY] [council.py](file:///c:/git_projects/llm-council/src/llm_council/council.py)
- Fix indentation logic in `run_stage2` dictionary call (Line 744).
- Verify `persist_session_bias_data` is correctly integrated in both modular and monolithic paths.

#### [MODIFY] [mcp_server.py](file:///c:/git_projects/llm-council/src/llm_council/mcp_server.py)
- No additional changes needed; refactor to `_get_progress_callback` is clean and adheres to SOLID principles.

## Open Questions
- None. The implementation aligns with established ADRs (ADR-012, ADR-027, ADR-032).

## Verification Plan

### Automated Tests
- `pytest tests/test_mcp_server.py`
- `pytest tests/test_mcp_tier_integration.py`
- `pytest tests/test_dissent_integration.py`

### Manual Verification
- Verify progress reporting visibility in an MCP inspector/client if available.
- Check `persist_session_bias_data` output (local logs/files) after a successful deliberation.
