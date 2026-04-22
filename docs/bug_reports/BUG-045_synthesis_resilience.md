# Bug Report: BUG-046 — Synthesis Resilience & Wiring Parity

## 1. Discovery & Analysis
- **Issue**: `Error: Unable to generate final synthesis.`
- **Log Source**: Claude Desktop Tool Output
- **Root Cause**: 
    1. **Wiring**: Stage 2 and Stage 3 were excluded from the `bypass_cache` wiring pass in BUG-045.
    2. **Resilience**: The Chairman orchestration in `stage3.py` lacks the ADR-039 fallback logic. If the primary model is restricted (403), Stage 3 returns `None` instead of shifting to a "lite" model for the verdict.

## 2. Technical Impact
Users with account restrictions cannot complete a council session because the final synthesis step crashes/fails, even if the "Health Check" says the system is ready.

## 3. Verification Strategy
- **Reproduction**: Create `tests/test_bug_046_synthesis_fallback.py` that mocks a 403 failure for the Chairman and verifies that Stage 3 can still produce a verdict using a fallback model.
