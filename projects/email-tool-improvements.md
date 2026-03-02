# Design: Unified Email Tool Attachment Handling

## 1. Philosophy & Goal

This design revises the approach to handling email attachments. Based on user feedback, the goal is to create a single, comprehensive email tool that can both read emails and save their attachments, without overstepping its bounds by parsing the file content itself.

This approach consolidates email-related logic into one place, `read_email.py`, while still adhering to the UNIX philosophy by handing off the saved file to other specialized tools (like `read_file`) for processing.

## 2. Tool Modifications: `read_email.py`

The `read_email.py` script will be significantly enhanced to become the single tool for all email reading and attachment-handling operations.

### 2.1. New Flags and Functionality

-   **`--id <email_id>`**:
    -   **Purpose**: To target a *single* email for an operation, such as reading its full body or saving its attachments.
    -   **Behavior**: When used, the script will fetch only the email corresponding to the given ID. This is a prerequisite for saving attachments.

-   **`--save-attachments <directory_path>`**:
    -   **Purpose**: To download all attachments from a specified email.
    -   **Behavior**: This flag **must** be used in conjunction with the `--id` flag. The script will find the specified email, iterate through all its attachments, and save each one into the provided directory path.
    -   **Output**: When this flag is used, the script's standard output will be a simple, machine-readable list of the absolute file paths of the attachments it just saved. This allows for easy composition with other tools.

### 2.2. Deprecated Flags

- The `--unseen` flag is less useful in a scriptable context and will be removed in favor of more direct targeting with `--limit` and `--id`.

## 3. The New Composable Workflow

This consolidated tool enables a more intuitive two-step workflow:

1.  **Discover**: An agent (or user) runs `python3 bin/read_email.py --limit 10 --json` to list recent emails and find the `id` of the target email.
2.  **Download & Process**:
    -   The agent runs the same tool again, but this time with the `id` and `save-attachments` flags to download the files.
        -   `python3 bin/read_email.py --id 12 --save-attachments /tmp/email_attachments`
    -   The command's output will be `/tmp/email_attachments/Jacob_Mimms_Resume.pdf`.
    -   The agent can now immediately use the `read_file` tool on this path to parse the resume content.
        -   `read_file(file_path='/tmp/email_attachments/Jacob_Mimms_Resume.pdf')`

## 4. `send_email.py` Improvements

To round out the unified tool, `send_email.py` will also be improved.

-   **`--attach <file_path>`**:
    -   **Purpose**: To attach a local file to an outgoing email.
    -   **Behavior**: This flag can be used multiple times to attach several files. The script will automatically determine the correct MIME type and encode the file for sending.

## 5. Conclusion

This revised design creates a more powerful and intuitive email tool. It consolidates related functionality into a single script, `read_email.py` for all reading and `send_email.py` for all sending, while respecting the boundaries of its responsibility. It downloads attachments but wisely leaves the parsing of those files to other, better-suited tools.
