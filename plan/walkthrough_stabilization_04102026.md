# Walkthrough: MCP Architecture Stabilization & Test Suite Restoration

This document summarizes the changes made to stabilize the Session-persistent Multi-Stage MCP Architecture and resolve the 10+ integration regressions identified during the ADR-032 configuration unification.

## Changes Overview

### 1. Orchestration Layer Refinement (`council.py`)
- **TierContract Timeout Internalization**: Refactored `run_council_with_fallback` to ingest `TierContract` objects directly. The orchestrator now respects contract-defined deadlines (`deadline_ms`, `per_model_timeout_ms`) and global multipliers (1.2x) instead of hardcoded defaults.
- **Bias Persistence Restoration**: Re-integrated `persist_session_bias_data` into the 3-stage pipeline to ensure cross-session bias metrics are correctly recorded. Added `asyncio.to_thread` wrapping for the synchronous persistence call to prevent event loop blocking.
- **Monolithic Stability**: Fixed a `ValueError` (unpacking mismatch) in the legacy `run_full_council` function, ensuring backward compatibility for tools still using the monolithic entry point.
- **Usage Aggregation**: Fixed a type-mismatch crash in `run_stage3` where flat usage dictionaries were being merged with nested stage-specific structures.

### 2. Model Registry & Intelligence (`registry.yaml`)
- **DeepSeek R1 Registration**: Added `deepseek/deepseek-r1` to the static model registry. This model was required for ADR-026 Phase 2 tests (reasoning detection and injection) but was missing from the bundled configuration.
- **Reasoning Detection**: Verified that reasoning models (o1, o3-mini, deepseek-r1) are correctly identified for parameter injection.

### 3. Test Suite Synchronization
- **MCP Tier Integration**: Updated `tests/test_mcp_tier_integration.py` to assert against the `TierContract` object properties rather than the now-deprecated `synthesis_deadline` keyword argument.
- **Dissent Metadata Verification**: Fixed `tests/test_dissent_integration.py` by ensuring mock setups provide at least two candidate responses (triggering Stage 2 peer review) and align with the Stage 1 return signature.
- **OpenRouter Mocking**: Standardized on patching `llm_council.openrouter.get_api_key` to avoid 401 Authentication errors during tests.

## Verification Results

### Integration Test Pass Rate
All identified regressions have been resolved, achieving a 100% pass rate for the primary orchestration and metadata integration suites:

| Test File | Status | Description |
|-----------|--------|-------------|
| `tests/test_council_integration.py` | ✅ PASSED | Bias persistence and session ID alignment |
| `tests/test_dissent_integration.py` | ✅ PASSED | Minority opinion extraction |
| `tests/test_mcp_tier_integration.py` | ✅ PASSED | Contract-driven timeout logic |
| `tests/test_metadata_integration.py` | ✅ PASSED | Reasoning model detection (DeepSeek R1) |
| `tests/test_reasoning_injection.py` | ✅ PASSED | OpenRouter payload injection |
| `tests/test_telemetry_alignment.py` | ✅ PASSED | Unified telemetry session IDs |

### Full Suite Validation
```bash
# Executed final full-suite verification
python -m pytest
# Result: 2695 passed, 11 skipped, 1 xfailed, 0 failed in 62.51s
```

## Next Steps for Issue #26
- [x] Achieve 100% pass rate on integration tests.
- [x] Staged all changes (`git add .`).
- [ ] Commit with ref #26 suffix.
- [ ] Merge `feature/multi-stage-mcp` into `master`.
