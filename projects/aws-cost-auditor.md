# New Design Idea: Automated AWS Cost Auditor

This is a conceptual design for a tool that automatically audits AWS resources and sends a report to Discord.

## Features
- **Daily Scans**: Auto-scan all regions for Public IPs and NAT Gateways.
- **Discord Integration**: Post summary reports to a dedicated channel.
- **One-Click Cleanup**: Provide links to CloudShell or Terraform commands to kill expensive resources.

## Architecture
1. **Lambda Function**: Triggered by EventBridge daily.
2. **DynamoDB**: Store historical cost data for trend analysis.
3. **IAM Role**: Minimal permissions (`ReadOnlyAccess` + `ce:GetCostAndUsage`).
