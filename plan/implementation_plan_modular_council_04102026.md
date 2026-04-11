# Implementation Plan - Modular Council Architecture (#28)

Refactor the monolithic `council.py` orchestrator into a modular, domain-specific package structure to improve maintainability and scalability.

## User Review Required

> [!IMPORTANT]
> This refactor introduces a domain-specific package `llm_council.stages`. While `council.py` remains as a compatibility facade, third-party extensions that directly import internal helpers from the old `council.py` may need to update their imports to the new modular locations.

> [!WARNING]
> We are utilizing a "Patch-Aware Gateway" pattern to support legacy tests that mock functions directly on the `llm_council.council` module.

## Proposed Changes

### Core Package Structure
Create new directories for modular logic:
- `src/llm_council/stages/`
- `src/llm_council/utils/`

### Orchestration Cleanup
- **council.py**: Convert into a thin Facade that re-exports logic from stages.

### Configuration & Constants
- **config_helpers.py**: Centralize lazy configuration loading with legacy patching support.
- **constants.py**: Centralize all council-wide timeouts and status codes.

### Stages Implementation
- `stage1.py`: Ideation phase.
- `stage2.py`: Peer review phase.
- `stage3.py`: Synthesis phase.

## Verification Plan

### Automated Tests
- Run full regression suite using `pytest`:
  ```powershell
  pytest tests/test_council.py tests/test_council_integration.py tests/test_mcp_server.py tests/test_verify_progress_reporting.py -v
  ```

### Manual Verification
- Verify MCP tool `council_query` generates real-time progress updates.
- Verify bias persistence store `bias_metrics.jsonl` is correctly populated.
