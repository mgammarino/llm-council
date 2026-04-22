# Bug Report: BUG-045 — Orchestration Argument Mismatch

## 1. Discovery & Analysis
- **Issue**: `TypeError: run_stage1() got an unexpected keyword argument 'bypass_cache'`
- **Log Source**: Claude Desktop Tool Output
- **Root Cause**: The MCP server signature was updated for Feature Parity, but the underlying orchestration logic in `stage1.py` and the `GatewayRequest` type were not updated to accept the new `bypass_cache` parameter.

## 2. Technical Impact
The "Bypass Cache" feature is currently unusable via the MCP server, and attempting to use it crashes the entire Stage 1 process.

## 3. Verification Strategy
- **Reproduction**: Create a python test `tests/test_bug_045_cache_wiring.py` that calls `run_stage1` with `bypass_cache=True`.
- **Success Criteria**: The test should pass without `TypeError` and verify that the `X-OpenRouter-Caching: false` header is generated in the final HTTP request.
