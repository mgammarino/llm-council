# Implementation Plan - MCP Feature Parity Upgrade

## Goal
Expose advanced orchestration parameters (`model_count`, `bypass_cache`, `verdict_type`, `include_dissent`, `allow_preview`) to the MCP server. This brings the chat-based (MCP) interface into parity with the core library and CLI, allowing for more granular control over council sessions.

## User Review Required
> [!IMPORTANT]
> This change modifies the `create_tier_contract` signature in `tier_contract.py`, which is a core contract. While backward compatible, it shifts how tier definitions are instantiated.

## Proposed Changes

### [Core Orchestration]

#### [MODIFY] [tier_contract.py](file:///c:/git_projects/llm-council/src/llm_council/tier_contract.py)
- Update `create_tier_contract(tier, task_domain=None)` to `create_tier_contract(tier, task_domain=None, model_count=None, allow_preview=False)`.
- Pass these parameters to `_get_allowed_models`.
- Update `_get_allowed_models` to enforce the requested `count` and `allow_preview` flag during selection.

### [MCP Server]

#### [MODIFY] [mcp_server.py](file:///c:/git_projects/llm-council/src/llm_council/mcp_server.py)
- Update `start_council` tool arguments:
  - `model_count: int = 4`
  - `bypass_cache: bool = False`
  - `allow_preview: bool = False`
- Update `council_synthesize` tool arguments:
  - `verdict_type: str = "synthesis"` (Enum choice: `synthesis`, `binary`, `tie_breaker`)
  - `include_dissent: bool = True`
- Update docstrings with clear descriptions for AI discovery.

## Verification Plan

### Automated Tests
- **Selection Count Test**: Run a 2-model council via MCP and verify metadata shows `requested_models: 2`.
- **Verdict Type Test**: Run a `binary` council and verify output structure.
- **Cache Test**: Verify `bypass_cache` flag propagates to stage 1.

### Manual Verification
- Execute a sample query: "Ask the council with 2 models in binary mode if this logic is sound..."
