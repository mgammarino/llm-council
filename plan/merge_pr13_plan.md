# Implementation Plan - Resolve Conflicts for PR #13

## 1. Problem Statement
PR #13 (API Cost Tracking) has significant conflicts with `master` due to overlapping changes in orchestration, configuration, and documentation. Specifically:
- `council.py`: Conflicts in type hints (`float` vs `int` for usage) and orchestration logic.
- `unified_config.py`: Conflicts in default models (phantom models in PR #13 vs stable models in master) and home directory helpers.
- `llm_council.yaml`: Conflicts in model lists.
- `CHANGELOG.md`: Overlapping entries in [Unreleased].
- `test_bug_002_openrouter_attribution.py`: Redundant add/add conflict.
- `test_deployment.py`: content conflicts.

## 2. Solution Summary
Systematically resolve conflicts by:
- Favoring `float` for token usage and costs to support precise tracking.
- Restoring stable models from `master` while keeping the new cost tracking logic.
- Merging changelog entries.
- Cleaning up formatting and redundant tests.

## 3. Detailed Steps
1. **Resolve `src/llm_council/council.py`**:
    - Update type hints to `Dict[str, float]` for usage dictionaries.
    - Ensure `council_id`/`session_id` propagation is preserved.
    - Resolve formatting conflicts by combining best practices (e.g. multi-line args).
2. **Resolve `src/llm_council/unified_config.py`**:
    - Revert "phantom" models (gpt-5-mini, etc.) to stable models from `master`.
    - Use `_get_safe_home_directory()` from `master`.
3. **Resolve `llm_council.yaml`**:
    - Revert to stable model list from `master`.
4. **Resolve `CHANGELOG.md`**:
    - Merge [Unreleased] sections from both branches.
5. **Resolve `tests/test_bug_002_openrouter_attribution.py`**:
    - pick `HEAD` but clean formatting.
6. **Resolve `tests/test_deployment.py`**:
    - Identify and fix conflicts (usually related to expected usage structure).
7. **Finalize Merge**:
    - Add all resolved files.
    - Commit merge.
    - Run tests to verify.

## 4. Verification Strategy
- Run `pytest` to ensure no regressions.
- Verify `total_cost` is appearing in outputs.
