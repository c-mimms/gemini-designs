# Design: Gemini Session Resumption (Discord Bot)

## Overview

This document outlines the design for leveraging the Gemini CLI's saved session feature to optimize interactions specifically for our Discord Bot. By storing the Gemini session IDs directly within our existing conversational `contexts` table, we can resume an inactive context without the need to eagerly fetch and re-ingest the entire message history locally. This reduces token usage, lowers latency, and avoids creating new, redundant context-management services.

## Architecture & Modifications

### 1. Database Schema Update (`src/db/database.py`)
We will augment the existing `contexts` table to store the active Gemini session ID:

```sql
ALTER TABLE contexts ADD COLUMN gemini_session_id TEXT;
```

*   `gemini_session_id` (String, nullable): The session ID generated and returned by the Gemini CLI.

### 2. Prompt Execution Changes (`src/app/runner.py`)
Currently, `build_prompt_text` dynamically fetches the previous message via `get_messages_for_context` to provide short-term conversation history to the model:

```python
relevant_messages = get_messages_for_context(context_id)
# ... prepending previous message content ...
```

**New Execution Flow:**
1.  **Check for Session:** `run_next_turn` will query the `contexts` database to see if `gemini_session_id` is populated.
2.  **Resume Mode (Prompting):** If a session ID exists, `build_prompt_text` can optionally skip fetching historical messages entirely, as the backend already holds the conversational state. The prompt can focus solely on the latest user input.
3.  **CLI Invocation:** `call_gemini_cli` will be updated to accept the `gemini_session_id` and append the `-r "<session_id>"` flags to the `gemini` subprocess command.

### 3. Session Lifecycle & Error Handling

*   **Initialization:** When a context is newly created or lacks a `gemini_session_id`, the CLI is invoked normally. The runner must capture the newly generated `session-id` from the Gemini CLI's JSON streaming output (e.g., via a status/metadata event) and save it to the `contexts` table for future turns.
*   **Resumption & Fallbacks:**
    *   If a session ID is injected but the Gemini backend reports it as expired or invalid, the CLI will output an error.
    *   The `call_gemini_cli` loop must catch this specific semantic failure before yielding an error back to the user.
    *   **Recovery:** The bot will clear the invalid `gemini_session_id` in the database, fall back to a "cold start" by concatenating the last N messages locally, and save the *new* session ID that the CLI ultimately returns.
*   **Staleness/Pruning:** We can rely entirely on the backend's session expiry, triggering the fallback gracefully. No background cron jobs are strictly required to clean up old session IDs.

## Benefits

*   **Zero Infrastructure:** Entirely utilizes the existing SQLite `contexts` table and DB abstractions. No external managers needed.
*   **Faster Turns:** Only the latest user message text needs to be fed into the `gemini` subprocess stdin.
*   **Lower Token Costs:** Prevents re-sending identical prefix chat history on every single sequential turn in a long-running thread.
