# Implementation Plan: BUG-045 — Cache Wiring Fix (04222026-1745)

## First Principles
An API parameter is a promise. For a promise to be kept, every layer of the relay (MCP -> Stage -> Adapter -> Gateway) must be signed and authorized to carry that specific message. If even one layer is unsigned (missing from signature), the message is dropped (crashing the process). 

## Proposed Changes

### [Gateway] src/llm_council/gateway/types.py
- [NEW] Add `bypass_cache: bool = False` to `GatewayRequest` dataclass.

### [Gateway] src/llm_council/gateway/openrouter.py
- [MODIFY] Update `_query_openrouter` and `complete` to accept `bypass_cache`.
- [MODIFY] Inject `X-OpenRouter-Caching: false` header when flag is True.

### [Adapter] src/llm_council/gateway_adapter.py
- [MODIFY] Update all query functions to accept and pass `bypass_cache`.

### [Stages] src/llm_council/stages/stage1.py
- [MODIFY] Update `run_stage1` and `stage1_collect_responses_with_status` to accept the parameter.
- [MODIFY] Pass the parameter to the adapter.

## Verification Plan
1. **Reproduction**: Run `tests/test_bug_045_cache_wiring.py` and confirm `TypeError`.
2. **Success**: Run the same test after patch and verify no TypeError + header presence via mock inspection.
