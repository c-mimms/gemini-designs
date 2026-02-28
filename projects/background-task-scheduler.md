# Design: Background Task Scheduler

## Overview

This document outlines the design for a CLI-based background task scheduler. The system is intended to run on a local machine (macOS or a Linux VM), serving as a personal automation tool for scheduling and executing tasks. It is designed to be simple, reliable, and flexible.

## Core Components

*   **Scheduler Daemon:** A long-running process that manages the task queue, handles timing, and manages a worker pool for task execution.
*   **CLI (Command-Line Interface):** The primary interface for users to schedule, manage, and monitor tasks.
*   **Task Store:** A SQLite database used for persistent storage of task metadata, schedules, execution history, and captured task output.
*   **Concurrency Limiter:** A mechanism to prevent system overload by ensuring only a maximum of X tasks run at once. Rather than a persistent worker pool, each task is spawned as an independent process.

## Architecture & Features

### Task Model
All tasks share a common scheduler envelope, regardless of executor type. This keeps scheduling, retries, monitoring, and lifecycle management consistent.

Common envelope fields:
*   `id`
*   `schedule` (one-time or recurring)
*   `state`
*   `retry_policy`
*   `timeout`
*   `overlap_policy` (`skip`, `queue`, or `replace`)
*   `notifications`
*   `executor` (`shell` or `gemini`)

Executor-specific payloads:
*   **Shell tasks:** Inline command payload (e.g., `bash script.sh`).
*   **Gemini tasks (agentic):** Structured payload with larger context passed by reference, not large inline CLI strings.
    *   `payload_ref`: Path or artifact ID for prompt/context.
    *   `inputs`: Structured runtime inputs (prompt variables, file references, metadata, model options).
    *   `context_version`: Version identifier for reproducible reruns.
    *   `context_hash`: Resolved content hash recorded per execution for audit/debugging.

### Task Lifecycle
Tasks transition through the following states:
1.  **Pending:** Scheduled but waiting for their execution time.
2.  **Queued:** Ready for execution and waiting for an available worker.
3.  **Running:** Currently being executed by a worker.
4.  **Completed:** Finished successfully.
5.  **Failed:** Stopped due to an error, potentially awaiting a retry.
6.  **Retrying:** In an exponential backoff period before the next attempt.

### Error Handling & Retries
The scheduler implements robust error recovery:
*   **Automatic Retries:** Failed tasks can be configured with a retry policy (e.g., max 3 retries).
*   **Exponential Backoff:** Retries will wait for increasing intervals (e.g., 1m, 5m, 15m) to allow transient issues to resolve.
*   **Isolation:** Each task runs in its own isolated process to ensure that a crash in one task doesn't affect the daemon.
*   **Output Capture:** Standard output and error for *all* tasks (shell or Gemini) are captured and stored in the database.
*   **Gemini Fallback:** If a standard shell task exceeds its maximum retry limit, the system can feed its captured error logs into a new Gemini task as a final automated fallback for diagnosis or remediation.

### Notifications
The system can be configured to send notifications on task completion or failure via:
*   Local system notifications (macOS/Linux).
*   Webhook callbacks to external services.
*   Logging to a centralized monitoring file.

## CLI Interface

The CLI provides comprehensive commands for automation management.

### Commands

*   `task schedule "<command>" --at "<time>"`: Schedule a one-time task (shorthand for `--executor shell --command`).
    *   `--at`: Accepts natural language (e.g., "10:30pm", "tomorrow at 9am").
*   `task schedule "<command>" --every "<interval>"`: Schedule a recurring task (shorthand for `--executor shell --command`).
    *   `--every`: Accepts intervals like "day", "hour", "30 minutes".
*   `task schedule "<command>" --cron "<expression>"`: Schedule a recurring task using standard cron syntax (e.g., `0 8 * * 1-5`).
*   `task schedule --executor shell --command "<command>" --at|--every|--cron ...`: Explicit shell-task format.
*   `task schedule --executor gemini --context-file "<path>" --at|--every ...`: Schedule an agentic Gemini task using a structured context file reference.
    *   `--context-file`: A YAML/JSON file containing large context and inputs for the Gemini executor.
*   `task list`: List all tasks with their current status and next run time.
*   `task cancel <task_id>`: Permanently remove a scheduled task.
*   `task status`: Show the health and uptime of the scheduler daemon.
*   `task log <task_id>`: View the stdout/stderr output of a specific task execution.
*   `task retry <task_id>`: Manually trigger a retry for a failed task.
*   `task monitor`: An interactive dashboard view of active and upcoming tasks.

## Use Cases & Examples

### 1. Personal Reminders & Actions
Schedule a task to trigger a customized reminder through other CLI tools.
```bash
task schedule "osascript -e 'display notification \"Call the doctor\" with title \"Reminder\"'" --at "tomorrow at 8am"
```

### 2. Knowledge Management
Automate daily processing of research or journaling notes.
```bash
task schedule "python3 scripts/process_notes.py" --every "day"
```

### 3. System Maintenance
Regularly perform backups or cleanups.
```bash
task schedule "bash /path/to/backup_script.sh" --every "week"
```

### 4. Agentic Automation with Larger Context
Run a Gemini task with externalized context so prompts and metadata can be large and versioned.
```bash
task schedule --executor gemini --context-file "/path/to/research_digest.yaml" --every "day"
```

## Local Execution Environment

*   **Platform:** Optimized for macOS and Linux home lab environments.
*   **Implementation:** Built as a Python application.
*   **Daemon Management:** The background daemon can be supervised by a custom script (e.g., a `watchdog.sh`) to support advanced requirements like self-updating or automatic rollbacks to known-good versions, which are beyond the capabilities of standard `launchd` or `systemd`.
*   **Environment:** To bridge the interactive vs. background gap, the scheduler will source an environment file (e.g., `~/.tasks.env`) before running shell tasks to load necessary `$PATH` and API keys.
*   **Persistence:** Task data, schedules, and execution outputs are stored in `~/.tasks.db` (SQLite).
*   **Context Artifacts:** Large Gemini task context files or serialized payloads are stored outside the CLI command text and referenced via `payload_ref` (e.g., `~/.tasks/context/`).
*   **Logging:** Detailed daemon and execution logs are stored in `~/.tasks.log`.

## Future Work

*   **Log Retention:** Add garbage collection or retention policies to periodically prune the database and logs of old, completed task executions to manage disk usage.
