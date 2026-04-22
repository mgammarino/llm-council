# Implementation Plan: Harden /ask Mode Protocol

This plan details the modernization of the `/ask` workflow to ensure strict adherence to the "Sovereign Context" (Repomix) pillar. By adding mandatory first steps and a required reporting header, we shift the workflow from a "guideline" to a "procedural protocol."

## User Review Required

> [!IMPORTANT]
> This change modifies a **global workflow** used for all research tasks. It will force a specific tool-call sequence (ls/repomix) at the start of every `/ask` session.

## Proposed Changes

### Global Workflows

#### [MODIFY] [ask.md](file:///C:/Users/carte/.gemini/antigravity/global_workflows/ask.md)
- Add **🛑 MANDATORY INITIALIZATION (Step 1)** block.
- Add **📋 Reporting Protocol** requirement to the Structured Response section.
- Upgrade Core Guidelines with **CRITICAL/REQUIREMENT** keywords.
- Add **🎨 Artifact Guidance** for the final reporting phase.

## Detailed Workflow Updates

### 1. Mandatory Initialization
Insert after the "Usage" section and before "Core Guidelines":
```markdown
# 🛑 MANDATORY INITIALIZATION (Step 1)
Before conducting ANY research or reading specific source files, you MUST verify the state of the Sovereign Context:
1. **Check for Context**: Run `ls repomix-output.md`.
2. **Handle Missing Context**: If the file is missing, RUN `repomix` immediately.
3. **Handle Stale Context**: If the file is older than 24 hours (check LastWriteTime), notify the user and ask if you should run `repomix` to refresh.
4. **Load Registry**: Once verified, read the first 100 lines of `repomix-output.md` to map the current architecture and ADR index.
```

### 2. Reporting Protocol
Update the "Structured Response" section to include a mandatory metadata block:
```markdown
### Required Response Metadata
Every `/ask` response MUST begin with this exact metadata block for auditability:
- **Context Source**: [repomix-output.md | Direct Exploration]
- **Context Timestamp**: [Current timestamp from ls]
- **ADRs Consulted**: [List ADR numbers or "None"]
- **Memory Search**: [Run/Skipped/Failed]
```

## Verification Plan

### Manual Verification
1. Invoke `/ask` with a new question about the codebase.
2. Verify that I (the assistant) perform `ls repomix-output.md` as the very first tool call.
3. Verify that the final response includes the required "Context Metadata" header.
4. Verify that the response explicitly links code findings to ADRs found in the `repomix-output.md`.
