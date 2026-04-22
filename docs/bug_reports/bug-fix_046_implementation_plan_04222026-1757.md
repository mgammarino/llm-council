# Implementation Plan: BUG-046 — Synthesis Resilience & Wiring (04222026-1757)

## First Principles
The system must be "Anti-Fragile." If a high-end model is restricted, the council should "downgrade" gracefully to preserve the user's progress rather than abandoning the session at the final yard line.

## Proposed Changes

### [Stages] src/llm_council/stages/stage2.py
- [MODIFY] Add `bypass_cache: bool = False` to `run_stage2` and `stage2_collect_rankings`.
- [MODIFY] Propagate to parallel query adapter.

### [Stages] src/llm_council/stages/stage3.py
- [MODIFY] Add `bypass_cache: bool = False` to `run_stage3`, `stage3_synthesize_final`, and `quick_synthesis`.
- [MODIFY] Implement ADR-039 Fallback: If the Chairman query returns a 403/402 status, retry once using a "QUICK" model (`gpt-4o-mini`).

### [Server] src/llm_council/mcp_server.py
- [MODIFY] Retrieve `bypass_cache` from `session` in `council_review` and `council_synthesize`.
- [MODIFY] Pass the flag to the orchestrators.

## Verification Plan
1. **Reproduction**: Mock a 403 error in `stage3_synthesize_final`.
2. **Success**: Verify that the function catches the error, retries with a fallback model, and returns a valid synthesis.
