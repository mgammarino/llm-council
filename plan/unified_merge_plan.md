# Unified Modular Council Integration

Unify the modular orchestration structure from Issue #28 with the functional MCP status improvements from Issue #26. This requires merging the structural refactor first and then manually porting the new logic into the modular stages to avoid data loss from massive `council.py` conflicts.

## User Review Required

> [!IMPORTANT]
> **Merge Conflict Strategy**: A direct `git merge` will fail significantly on `council.py`. I will use a "Structure-First" approach:
> 1. Merge `#28` (Modularization) first as the target architecture.
> 2. Manually port the "ADVERSARIAL CRITIQUE" and progress logic from `#26` into the new `stages/` modules.
> 3. Preserve the **Patch-Aware Gateway** in `council.py` to keep legacy tests passing.

> [!WARNING]
> **Terminology Shift**: "Devil's Advocate" is being deprecated in favor of "ADVERSARIAL CRITIQUE" per Issue #26. This will be standardized across all modular stages.

## Proposed Changes

### Phase 1: Structural Alignment

#### [MOD] [master](file:///c:/git_projects/llm-council)
Merge `feature/modular-council-28` into `master`. 
- Validates the new `stages/` package.
- Reduces `council.py` to a 200-line facade.

### Phase 2: Functional Porting (Issue #26)

#### [MOD] [mcp_server.py](file:///c:/git_projects/llm-council/src/llm_council/mcp_server.py)
Merge logic from `feature/mcp-status-updates-26`:
- Enhanced tool progress reporting.
- Improved session store integration for 3-stage persistence.

#### [MOD] [council.py](file:///c:/git_projects/llm-council/src/llm_council/council.py)
Update the facade to support the Issue #26 features:
- Standardize `run_full_council` signature to match the legacy 4-tuple expectation while calling modular stages internally.
- Implement the `PatchDetectionAudit` more robustly within the facade.

#### [NEW] [stages/stage1.py](file:///c:/git_projects/llm-council/src/llm_council/stages/stage1.py) (Modified)
Inject Stage 1B (Adversarial) enhancements from Issue #26:
- Rename "Devil's Advocate" -> "ADVERSARIAL CRITIQUE" in logs and status events.
- Implement session-persistent bias data propagation.

### Phase 3: Modernizing the Suite

#### [MOD] [tests](file:///c:/git_projects/llm-council/tests)
Update existing tests to reflect the new architecture:
- Update `tests/test_verify_progress_reporting.py` to expect "ADVERSARIAL CRITIQUE" status updates.
- Create `tests/test_council_patch_audit.py` to explicitly verify the Patch-Aware Gateway.

## Open Questions

- **Branch Cleanup**: Should I delete the feature branches after a successful merge and verification?
- **Legacy Support**: Do we need to preserve the `stage1_collect_responses` naming in the facade indefinitely, or can we mark it as Deprecated?

## Verification Plan

### Automated Tests
- `pytest tests/test_council_integration.py` (Verify facade compatibility)
- `pytest tests/test_verify_progress_reporting.py` (Verify MCP status logic)
- `pytest tests/test_mcp_server.py` (Verify server stability)

### Manual Verification
- Check `git diff` to ensure no logic from Issue #26 was lost during modularization.
- Verify "ADVERSARIAL CRITIQUE" appears in CLI/MCP logs.
