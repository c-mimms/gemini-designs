# Design: Gemini Session Resumption

## Overview

This document outlines the design for leveraging the Gemini CLI's saved session feature to optimize interactions in multi-turn contexts (like Discord channels or DM threads). By storing a mapping of contexts to their respective Gemini session IDs, we can resume an inactive context without the need to fetch and re-ingest the entire message history. This significantly saves on token usage, latency, and processing overhead.

## Architecture & Features

### Core Components

*   **Context Manager:** A service responsible for tracking the active `session-id` for any given context (e.g., a Discord channel ID, conversation ID, or thread ID).
*   **Session Store:** A persistent datastore (such as SQLite) that maintains the mapping between our internal context IDs and the Gemini CLI session IDs.
*   **Message Router:** Intercepts incoming messages, looks up the corresponding session in the Session Store, and formulates the correct `gemini` CLI command.

### Session Lifecycle

1.  **Initialization:** When a message arrives in a new or expired context, a new Gemini session is initiated. The resulting `session-id` returned by the CLI is captured and stored in the Session Store against the context ID.
2.  **Resumption:** When subsequent messages arrive in that context, the Message Router retrieves the stored `session-id`. It then dispatches the message using the resume flag:
    ```bash
    gemini -r "<session-id>" "<new_message_content>"
    ```
3.  **Invalidation/Expiry:** If a session expires or becomes invalid on the Gemini backend, the CLI should gracefully handle the error. The Message Router must catch this failure, invalidate the `session-id` in the Session Store, and fallback to re-ingesting the recent message history to start a new session.
4.  **Context Switching:** The system naturally supports multiple concurrent conversations. Each context acts independently, with its own stored session state.

### Data Model

A simple key-value or relational model is sufficient for the Session Store.

*   `context_id` (String, Primary Key): The unique identifier for the conversation context (e.g., Discord Channel ID).
*   `gemini_session_id` (String): The session ID provided by the Gemini CLI.
*   `last_active_at` (Timestamp): Used to track session staleness and clean up inactive sessions.
*   `metadata` (JSON): Optional field for storing context-specific settings or instructions.

## Error Handling & Fallbacks

*   **Session Not Found:** If the CLI returns an error indicating the session ID is no longer valid, the system must automatically downgrade to a "cold start." It will fetch the `$N` most recent messages from the context, concatenate them, and start a new session, storing the new `session-id`.
*   **Concurrency:** If multiple messages arrive in the same context simultaneously, the system should queue them or manage locks to ensure they are appended to the Gemini session in the correct chronological order to maintain conversational coherence.

## Integration & Use Cases

### 1. Discord Bot Integration

The primary use case is the Discord bot. Each channel or direct message thread represents a context. The bot will use the stored `session-id` to respond faster and cheaper, avoiding the need to serialize the last 50 messages on every single user input.

### 2. Multi-Agent Workflows

In scenarios where a background task scheduler triggers an agent to perform work, the agent's progress can be maintained across execution boundaries by passing the `session-id` between runs.
