# Implementation Plan - API Cost Tracking

This plan outlines the changes required to capture, aggregate, and return the real-time monetary cost of API calls within the LLM Council. This enables users to monitor the financial impact of council deliberations.

## User Review Required

| Step | Phase | Status | Artifact/Evidence |
| :--- | :--- | :--- | :--- |
| 1 | Planning & Research | [x] Completed | [implementation_plan_api_cost_tracking_04082026.md](file:///c:/git_projects/llm-council/plan/implementation_plan_api_cost_tracking_04082026.md) |
| 2 | GitHub & Branch | [x] Completed | Issue #12 / `feature/api-cost-tracking` |
| 3 | Implementation | [ ] Pending | [Commit Hash] |
| 4 | Quality Gates (Ruff/Mypy) | [ ] Pending | [Lint Results] |
| 5 | Peer Verification (Pytest) | [ ] Pending | [Test Results] |
| 6 | Documentation | [ ] Pending | [Walkthrough Path] |
| 7 | Delivery & Merge | [ ] Pending | [PR Link] |


> [!IMPORTANT]
> This change introduces a new `total_cost` field to several internal data structures (`UsageInfo`, `GatewayResponse`) and the final response metadata. While backward compatible, it adds a dependency on upstream providers (specifically OpenRouter) providing this field in their responses.

## Proposed Changes

### [Component] Gateway Types

#### [MODIFY] [types.py](file:///c:/git_projects/llm-council/src/llm_council/gateway/types.py)
- Update `UsageInfo` dataclass to include `total_cost: float = 0.0`.

### [Component] Provider Implementations

#### [MODIFY] [openrouter.py](file:///c:/git_projects/llm-council/src/llm_council/openrouter.py)
- In `query_model_with_status`, extract `total_cost` from the OpenRouter response JSON `usage` object.
- Include `total_cost` in the returned `usage` dictionary.

#### [MODIFY] [gateway/openrouter.py](file:///c:/git_projects/llm-council/src/llm_council/gateway/openrouter.py)
- In `_query_openrouter`, extract `total_cost` from the JSON response.
- In `complete`, map `total_cost` to the `UsageInfo` object.

### [Component] Gateway Adapter

#### [MODIFY] [gateway_adapter.py](file:///c:/git_projects/llm-council/src/llm_council/gateway_adapter.py)
- Update `_gateway_response_to_dict` to include `total_cost` in the converted usage dictionary.
- Update `query_model`'s usage dictionary construction.

### [Component] Council Orchestration

#### [MODIFY] [council.py](file:///c:/git_projects/llm-council/src/llm_council/council.py)
- In `stage1_collect_responses` and `stage1_collect_responses_with_status`, initialize `total_usage` with `total_cost: 0.0`.
- Aggregate `total_cost` from each model response into the `total_usage` dictionary.
- Update `run_council_with_fallback`'s `run_council_pipeline` to propagate aggregated cost into the final `result` metadata or a new top-level field.
- Ensure all synthesis stages (Stage 1.5, Stage 2, Stage 3) also contribute their costs to the total.

## Open Questions

> [!NOTE]
> Should we display the cost formatted as USD (e.g., "$0.012") or just as a float? The recommendation is to return the float for programmatic use and potentially format it only in UI components.

## Verification Plan

### Automated Tests
- `uv run pytest tests/test_gateway_cost.py`: New test to verify cost extraction from mocked OpenRouter responses.
- `uv run pytest tests/test_council_cost_aggregation.py`: New test to verify total cost aggregation in a multi-model council run.

### Manual Verification
- Run a council query with a live OpenRouter key and inspect the returned dictionary to ensure `total_cost` is present and non-zero.
