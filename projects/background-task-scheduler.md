# Design: Background Task Scheduler

## Overview

This document outlines the design for a CLI-based background task scheduler. The system is intended to run on a local machine (macOS or a Linux VM), serving as a personal automation tool for scheduling and executing tasks. It is designed to be simple, reliable, and flexible.

## Core Components

*   **Scheduler Daemon:** A long-running process that manages the task queue, handles timing, and manages a worker pool for task execution.
*   **CLI (Command-Line Interface):** The primary interface for users to schedule, manage, and monitor tasks.
*   **Task Store:** A SQLite database used for persistent storage of task metadata, schedules, and execution history.
*   **Worker Pool:** A managed set of execution slots to prevent system overload from too many concurrent tasks.

## Architecture & Features

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
*   **Isolation:** Each task runs in its own shell environment to ensure that a crash in one task doesn't affect the daemon.

### Notifications
The system can be configured to send notifications on task completion or failure via:
*   Local system notifications (macOS/Linux).
*   Webhook callbacks to external services.
*   Logging to a centralized monitoring file.

## CLI Interface

The CLI provide comprehensive commands for automation management.

### Commands

*   `task schedule "<command>" --at "<time>"`: Schedule a one-time task.
    *   `--at`: Accepts natural language (e.g., "10:30pm", "tomorrow at 9am").
*   `task schedule "<command>" --every "<interval>"`: Schedule a recurring task.
    *   `--every`: Accepts intervals like "day", "hour", "30 minutes".
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
task schedule "gemini 'email chris@example.com with a reminder to call the doctor'" --at "tomorrow at 8am"
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

## Local Execution Environment

*   **Platform:** Optimized for macOS and Linux home lab environments.
*   **Persistence:** Task data is stored in `~/.tasks.db` (SQLite).
*   **Logging:** Detailed execution logs are stored in `~/.tasks.log`.
*   **Dependencies:** Built as a lightweight Python application or Go binary for easy installation.
