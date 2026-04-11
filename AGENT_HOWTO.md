# AGENT_HOWTO: Using Repomix and Mem0

This guide explains how to use the Agent Setup (Repomix + Mem0) to provide high-fidelity context and persistent memory for AI-assisted coding in the `llm-council` project.

---

## 📘 How to Use the Setup

### 1. Repomix: Codebase Context
Repomix packs the entire codebase into a single file, allowing the agent to see all files at once.

*   **When to refresh**: After writing a large amount of new code or before starting a new session.
*   **Command**: `repomix`
*   **Output**: `repomix-output.md` (root directory).
*   **Usage**: In a new session, ask the agent: *"Read the project context in repomix-output.md."*

### 2. Mem0: Persistent Memory
Mem0 stores architectural decisions and "lessons learned" across sessions in a local-only database.

*   **When to refresh**: After a session where major architectural decisions were made.
*   **Registration**: Run `python memory_init.py` (seeds basic context) or ask the agent to store a fact.
*   **Recall**: Ask the agent to search memory for past decisions or technical context.

---

## 🕵️ How to Verify Agent Usage

You can verify the agent (Gemini/Claude) is utilizing this setup with these tests:

### 1. The Knowledge Item Test
Check if the agent acknowledges the **"Agent Tooling: Repomix + Mem0 Setup"** Knowledge Item in its initial project summary.

### 2. The "Blind File" Test
Ask the agent about a file that hasn't been opened in the current session:
*   **Prompt**: *"Describe the logic in src/llm_council/voting.py without opening it."*
*   **Pass**: If it provides a detailed description (retrieved from `repomix-output.md`).

### 3. The "Memory Retrieval" Test
Ask the agent to query the local database:
*   **Prompt**: *"Search our local memory for the project's tech stack."*
*   **Pass**: If it executes a Python command to query the Mem0 store and returns accurate facts.
