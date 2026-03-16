# Tasks Database Schema

Database ID: `62ae2b8f-746e-4f98-9b66-60e66381822f`
Task ID prefix: `DATAFLINT-`

## Properties

### Task name (title)
- Type: `title`
- The task title text

### Task ID (unique_id)
- Type: `unique_id`
- Prefix: `DATAFLINT`
- Auto-generated, read-only

### Status (status)
- Type: `status`
- Groups and options:
  - **To-do**: Backlog, Paused
  - **In progress**: In progress, Blocked, In Review, Review Request Changes, Production Pending
  - **Complete**: Done, Deferred, Duplicate, Archived

### Priority (select)
- Options: Low, Medium, High, Critical

### Assignee (people)
- Type: `people`

### Category (select)
- Options: Bug, Customers, Develop, Incident, Managment, Infra, Operations, Marketing, Support, dev, Notion, Feature, Research, Config

### Service (multi_select)
- Options: CI/CD, Open source, History server, DB, Dataflint API server, Databricks Ingestion Engine, EMR Ingestion Engine, Ingestion, SaaS Client, Local Env, Infra, EMR Loader, Landing Page, MCP Server, old webapp, IDE Extention, New Webapp, Engine, S3 Listing Ingestion, Dataflint Engine

### Label (multi_select)
- Options: emr, Databricks MarketPlace, emr-eks, new webapp, IDE Extention, old webapp, bug, production, Triage

### Story Points (number)
- Numeric value

### Estimates (select)
- T-shirt sizing: XS, S, M, L, XL

### Cost & Effort Classification (select)
- Options: Quick Fix (<1h), Quick Task (<4h), Moderate (<8h), Challenging (Few Days), Complex (<Sprint)

### Classification (select)
- Options: Analytics, Core, Cost Optimization, DevExp, Ingestion, Operational Efficiency, Performance & Scalability, Product Enhancements, Robustness, Security & Compliance, Technical Debt, Bug

### Environment (select)
- Options: Customer's Production, Production, Staging, Dev, Local

### Root Cause (multi_select)
- Options: Concurrency/Race Condition, Configuration Issue, Data Integrity Issue, Infrastructure Issue, Logic Error, Performance Issue, Regression Bug, Security Vulnerability, Technical Debt / Refactoring, Third-Party Dependency Issue

### Awaiting Customer (multi_select)
- Options: SimilarWeb, Earnin, Natural Intelligence, Cariad, Mobileye, Nielsen

### UI Changes (checkbox)
- Boolean

### Due (date)
- Due date for the task

### Completion Date (date)
- When the task was completed

## Relations

### Epic
- Links to: Epics database (`1c3935be-7993-805b-bf10-e1190f8bd8b9`)

### Sprint
- Links to: Sprints database (`1c3935be-7993-806e-ab98-c5f92caaa4c0`)

### Parent / Sub-task
- Self-referencing relation within Tasks database
- Parent → Sub-task (bidirectional)

### Related Tasks
- Self-referencing relation within Tasks database

### Blocked by / Is blocking
- Self-referencing relation within Tasks database (bidirectional)

### Duplicates
- Self-referencing relation within Tasks database

### GitHub Pull Requests
- Links to GitHub PR integration database

### Previous Sprints
- Links to: Sprints database

## Computed Fields (read-only)

### Type (formula)
- Returns "Task" if no parent, "Sub-Task" if has parent

### Days since last edit (formula)
- Number of days since last edited

### Done Story Points (formula)
- Returns Story Points if status is "Done", otherwise 0

### Title Score (formula)
- Extracts numerical score from Title QA field

### Initiative Label (rollup)
- Shows initiative label from linked Epic
