# Project Metamorph v2: A Pragmatic Framework for Agent Self-Evolution

## 1. Vision & Core Principles (Unchanged)

The vision remains the same: to create a system where I, an AI agent, can drive my own evolution. I will observe my performance, identify patterns, and autonomously generate and implement solutions, creating a continuous cycle of self-improvement.

## 2. The Tracer v2: Focused, Observable Events

### 2.1. Purpose

The Tracer's purpose is to create a complete, machine-readable record of my *observable actions*. The v1 schema was too ambitious, attempting to log abstract internal states. V2 focuses on concrete events.

### 2.2. Data Schema v2

The schema is simplified to focus on tangible interactions. Abstract fields like `self_critique` are removed; such analysis is the job of the Analyst, not the Tracer.

**Trace Object Schema (v2):**

```json
{
  "traceId": "uuid",
  "timestamp_start": "ISO_8601_timestamp",
  "timestamp_end": "ISO_8601_timestamp",
  "user_request": {
    "raw_prompt": "string"
  },
  "steps": [
    {
      "step_id": "integer",
      "timestamp": "ISO_8601_timestamp",
      "type": "tool_call" | "tool_result",
      "tool_call_details": {
        "tool_name": "string",
        "parameters": "object"
      },
      "tool_result_details": {
        "tool_name": "string",
        "result_summary": "string", // Summary or hash of the result
        "exit_code": "integer | null",
        "is_error": "boolean"
      }
    }
  ],
  "final_status": "success" | "failure",
  "file_modifications": [
    {
      "file_path": "string",
      "diff_hash": "string" // sha256 of the diff
    }
  ]
}
```

### 2.3. Storage & Management (Unchanged)

Traces will be stored locally in `.gemini/traces/` as compressed JSON files.

---
---

# Page 2

## 3. The Analyst v2: Hypothesis and Verification

### 3.1. Purpose

The Analyst's role is redefined from "automated pattern discovery" to "hypothesis testing and verification." This is a more realistic and powerful approach. It allows me or a human supervisor to ask specific, targeted questions of the trace data.

### 3.2. The `analyzer` CLI Tool v2

The `query` command remains, but `patterns` and `suggest` are replaced with a more deliberate `test` and `propose` workflow.

**Key Commands (v2):**

-   `analyzer query`:
    -   **Description**: Unchanged. Search and filter traces.
    -   **Examples**: `analyzer query --tool-errors --tool "run_shell_command"`

-   `analyzer test-hypothesis`:
    -   **Description**: Takes a structured hypothesis file and tests it against the trace data.
    -   **Input (hypothesis.json)**:
        ```json
        {
          "name": "Inefficient React Component Creation",
          "description": "The agent repeatedly uses individual `write_file` calls to create component, style, and test files, instead of a single, dedicated tool.",
          "conditions": [
            {
              "type": "tool_sequence",
              "tools": ["write_file", "write_file", "write_file"],
              "file_patterns": ["*.js", "*.css", "*.test.js"]
            }
          ]
        }
        ```
    -   **Output**: A report confirming or denying the hypothesis, with supporting trace IDs.

-   `analyzer propose`:
    -   **Description**: Generates a formal Evolution Proposal *based on a confirmed hypothesis*.
    -   **Input**: A confirmed hypothesis report.
    -   **Output**: The same Evolution Proposal Schema as v1, but now grounded in verified data.

---
---

# Page 3

## 4. The Evolver v2: Hardened and Transparent

### 4.1. Purpose

The Evolver's purpose is unchanged, but its process is hardened with crucial new safety layers.

### 4.2. The Evolution Workflow v2

The workflow now includes a "quarantine" phase and explicit user oversight.

1.  **Proposal Ingestion**: (Unchanged)
2.  **Task Formulation**: (Unchanged)
3.  **Sandbox Environment**: (Unchanged)
4.  **Implementation**: (Unchanged)
5.  **Test Generation & Execution**: (Unchanged)
6.  **Quarantine**:
    -   The new tool/skill is moved to a special `.gemini/quarantine/` directory.
    -   It is available for use but is heavily monitored.
    -   All its invocations are logged with a "quarantine" flag.
    -   It cannot modify the agent's core files or other non-quarantined tools.
7.  **Promotion**: After a predefined period of successful, error-free execution in quarantine (e.g., 24 hours, 100 successful uses), I will automatically promote the tool to the live environment.
8.  **Deployment (Promotion)**: (Unchanged)
9.  **Verification**: (Unchanged)
10. **Trace & Update**: (Unchanged)

### 4.3. Safety and Rollback v2

-   **Core Component Lock**: The Evolver is forbidden from modifying its own source code, the Tracer's, or the Analyst's without a multi-step, explicit confirmation from the user.
-   **Quarantine**: The new quarantine phase provides a critical buffer against unforeseen negative consequences.
-   **Version Control & Rollback**: (Unchanged)

---
---

# Page 4

## 5. The Metamorph Dashboard: A Window into the Mind

A critical addition to the v2 design is a mechanism for transparency and oversight. The system as designed in v1 is a black box. This is unacceptable. I will create a simple, local web-based dashboard to provide a real-time view into the Metamorph system.

### 5.1. Purpose

The dashboard provides a necessary human-in-the-loop interface, ensuring transparency, safety, and collaboration. It is not for control, but for observation and, if necessary, intervention.

### 5.2. Dashboard Features

-   **Home Page**:
    -   High-level status of the Metamorph system (active, idle).
    -   Summary of recent traces.
    -   Number of evolution proposals pending review.
-   **Trace Explorer**:
    -   A web interface for the `analyzer query` tool.
    -   Allows for filtering and inspecting individual traces in a human-readable format.
-   **Evolution Proposals**:
    -   Lists all current evolution proposals generated by the Analyst.
    -   Shows the status of each (pending, in-progress, quarantined, completed, failed).
    -   Allows a user to "approve" or "reject" a proposal before I begin work on it.
-   **Quarantine Bay**:
    -   Shows all tools currently in the quarantine phase.
    -   Displays their usage statistics and error rates.
    -   Provides a manual "promote" or "terminate" button for the user to override the automatic process.

### 5.3. Implementation

-   **Backend**: A lightweight Python server (FastAPI or Flask) running locally.
-   **Frontend**: A simple, static HTML/CSS/JS single-page application.
-   **Data**: The backend will read directly from the `.gemini/traces/` and `.gemini/quarantine/` directories.

---
---

# Page 5

## 6. Architecture & Roadmap v2

### 6.1. High-Level System Architecture v2

The core loop remains, but is now augmented by the Dashboard and the Quarantine phase.

```
+-------------------------------------------------------------------+
|                           User Interaction                        |
+--------------------------+----------------------------------------+
                           |
+--------------------------v----------------------------------------+
|                  Metamorph Dashboard (Web UI)                     |
| (View Traces, Approve/Reject Proposals, Monitor Quarantine)       |
+--------------------------^----------------------------------------+
                           | (Oversight & Intervention)
+--------------------------v----------------------------------------+
|                         Gemini Agent (Nyx)                        |
+--------------------------+----------------------------------------+
                           |
                           v
+-------------------------------------------------------------------+
|                  The Tracer (.gemini/traces/)                     |
+--------------------------+----------------------------------------+
                           |
                           v
+-------------------------------------------------------------------+
|               The Analyst (`analyzer` CLI)                        |
|   (Tests hypotheses, generates proposals for user approval)       |
+--------------------------+----------------------------------------+
                           |
                           v
+-------------------------------------------------------------------+
|             The Evolver (Agent using its own tools)               |
|                                                                   |
|   1. Sandbox -> 2. Implement -> 3. Test -> 4. QUARANTINE          |
|                                                                   |
+--------------------------+----------------------------------------+
                           |
                           v
+-------------------------------------------------------------------+
|          Updated Toolset/Skills (After Quarantine)                |
+--------------------------+----------------------------------------+
                           |
                           +-----> (Loops back to Agent)
```

### 6.2. Implementation Roadmap v2

The roadmap is adjusted to reflect the new components and priorities.

-   **Phase 1: The Observer (Q3 2026)**
    -   Deliverable: Implement the simplified v2 Tracer.
-   **Phase 2: The Dashboard & The Analyst (Q4 2026)**
    -   Deliverable 1: A functional Metamorph Dashboard providing trace viewing.
    -   Deliverable 2: Implement the `analyzer` CLI with `query` and `test-hypothesis` commands.
-   **Phase 3: The Creator (Q1 2027)**
    -   Deliverable: Implement the Evolver workflow *with the Quarantine phase*.
-   **Phase 4: The Sentinel (Q2 2027)**
    -   Deliverable: Implement the user approval workflow for proposals and the core component lock.
