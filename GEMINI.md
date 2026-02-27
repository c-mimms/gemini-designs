# Designs Project Mandates

This file defines the core operating rules for any AI agent working within the `designs/` directory.

## Maintenance & Integrity
- **Redeploy on Change**: Any modification to files in `projects/`, `templates/`, or `scripts/` MUST be followed by a successful execution of `python3 scripts/build.py` and a deployment (via Terraform or AWS CLI).
- **Persistence**: All design documents must be stored as Markdown files in the `projects/` directory.
- **Version Control**: Every significant change or deployment MUST be committed to the repository with a descriptive message.

## Build System
- The build system uses `scripts/build.py` to generate a static site in `build_out/`.
- Titles for projects are automatically extracted from the first `# H1` header in the Markdown file.
- Do NOT commit the `build_out/` directory; it is ignored by design.
