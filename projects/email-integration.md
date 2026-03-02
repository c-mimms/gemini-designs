# Design: Email Integration CLI

## Overview

This document outlines the design for an email integration for the `discord_bot` ecosystem. The integration will be implemented as a standalone CLI tool that leverages the existing SMTP configuration in the bot's `.env` file. This allows the bot, or other system components, to send email notifications, alerts, or summaries via standard shell commands.

## Core Components

### `send_email.py`

The primary component for sending emails.

*   **SMTP Integration**: Uses `smtplib` to connect to a mail server.
*   **Environment Aware**: Automatically loads configuration from the `discord_bot/.env` file.
*   **Flexible CLI**: Supports specifying recipient, subject, and body via command-line arguments, piped input, or file input (`--file`).
*   **HTML Support**: Optional flag (`--html`) to send emails as HTML.

### `read_email.py`

A new component for reading emails via IMAP.

*   **IMAP Integration**: Uses `imaplib` to connect to an IMAP server (e.g., Gmail).
*   **Unseen Filter**: Option to fetch only unread messages (`--unseen`).
*   **JSON Output**: Supports `--json` flag for machine-readable output, ideal for AI agents.
*   **Body Extraction**: Automatically extracts plain text and HTML bodies from multipart messages.

## Technical Architecture

### Environment Configuration
The tools will look for the following variables in `.env`:
*   `SMTP_HOST`: The SMTP server address.
*   `SMTP_PORT`: The SMTP server port.
*   `IMAP_HOST`: The IMAP server address.
*   `IMAP_PORT`: The IMAP server port.
*   `SMTP_USER`: The email address (used for both SMTP and IMAP).
*   `SMTP_PASS`: The password or app-specific password.

### CLI Interfaces

**Sending:**
```bash
python3 bin/send_email.py --to recipient@example.com --subject "Report" --file path/to/report.html --html
```

**Reading:**
```bash
python3 bin/read_email.py --limit 5 --json
```

## Use Cases

1.  **Bot Notifications**: The `discord_bot` can trigger email alerts.
2.  **System Alerts**: Background tasks can notify the user of completion or failure.
3.  **Newsletter/Digest Reading**: Agents can read incoming newsletters or reports and summarize them for the user in Discord.
4.  **Rich Reporting**: Automated scripts can generate complex HTML reports and send them using the tool.
