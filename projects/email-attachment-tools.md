# Design: Modular Email Attachment Handling

## 1. Philosophy & Goal

Following the UNIX philosophy of "do one thing and do it well," this document outlines a set of small, modular tools and modifications to handle email attachments. The goal is to create a clean, composable, and reusable workflow for processing attachments without creating large, monolithic tools.

This design avoids duplicating functionality that already exists in other tools (like `read_file`'s ability to parse PDFs) and instead focuses on creating the missing links in the chain.

## 2. Tool Modifications & Additions

### 2.1. Modification: `read_email.py`

The existing `read_email.py` script will be updated with one new optional flag.

-   **`--include-attachments`**:
    -   When this flag is present, the JSON output for each email will include a new array named `attachments`.
    -   Each object in the `attachments` array will contain metadata for a single attachment.
    -   This metadata will include:
        -   `attachment_id`: A unique identifier for the attachment within that email.
        -   `filename`: The name of the attachment file (e.g., "resume.pdf").
        -   `content_type`: The MIME type of the attachment (e.g., "application/pdf").
        -   `size`: The size of the attachment in bytes.
    -   **Crucially, this flag will NOT download the attachment content itself.** It only fetches the metadata.

#### Example JSON Output:

```json
[
  {
    "id": "12",
    "from": "Jacob Mimms <jacobmimms@gmail.com>",
    "subject": "stupid resume",
    "date": "Mon, 2 Mar 2026, 6:39 AM",
    "body": "...",
    "attachments": [
      {
        "attachment_id": "part1.2",
        "filename": "Jacob_Mimms_Resume.pdf",
        "content_type": "application/pdf",
        "size": 12345
      }
    ]
  }
]
```

### 2.2. New Tool: `save_attachment`

This is a new, standalone script that does one thing: saves a specific email attachment to the local filesystem.

-   **Name**: `save_attachment.py`
-   **Location**: `discord_bot/bin/save_attachment.py`
-   **Arguments**:
    -   `--email-id <id>`: The ID of the email containing the attachment (obtained from `read_email.py`).
    -   `--attachment-id <id>`: The unique ID of the attachment to download (obtained from `read_email.py --include-attachments`).
    -   `--output <path>`: The local file path where the attachment should be saved (e.g., `/tmp/resume.pdf`).
-   **Function**: The tool will connect to the email server, find the specified email and attachment, download the raw content, and write it to the file specified by the `--output` path.

## 3. The Composable Workflow

This design enables a clean, multi-step workflow that leverages both new and existing tools:

1.  **Discover**: An agent (or user) runs `python3 bin/read_email.py --json --include-attachments` to find the target email and get a list of its attachments.
2.  **Download**: The agent identifies the correct attachment from the metadata and uses the new tool to download it to a temporary location.
    -   `python3 bin/save_attachment.py --email-id 12 --attachment-id part1.2 --output /tmp/brother_resume.pdf`
3.  **Process**: The agent now has a local file. It can use the existing, powerful `read_file` tool to parse its content, regardless of whether it's a PDF, a text file, or an image.
    -   `read_file(file_path='/tmp/brother_resume.pdf')`

This approach is robust, flexible, and adheres to the principle of building simple parts that can be combined in powerful ways.
