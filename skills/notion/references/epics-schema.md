# Epics Database Schema

Database ID: `1c3935be-7993-805b-bf10-e1190f8bd8b9`

## Properties

### Name (title)
- The epic title

### Owner (people)
- Epic owner

### Priority (select)
- Epic priority level

### Teams (multi_select)
- Options: Frontend, Backend, DevOps, Data, QA

### Target Quarter (select)
- Target delivery quarter

### Date (date)
- Epic date/timeline

### Status (status)
- Epic lifecycle status

### Awaiting Customer (multi_select)
- Customer dependencies

## Relations

### Tasks
- Links to: Tasks database (`62ae2b8f-746e-4f98-9b66-60e66381822f`)
- Shows all tasks under this epic

### Blocked By
- Self-referencing relation (epic dependencies)

### Product
- Links to: Product database (`1c8935be-7993-807a-a30d-d371d230024b`)

## Computed Fields (read-only)

### Progress Bar (formula)
- Visual emoji progress bar showing done/in-progress/blocked/remaining
- Format: `XX% 🟩🟩🟩🟨🟥⬜⬜⬜⬜⬜ [done/in-progress/blocked/total]`

### Epic Progress (rollup)
- Aggregated completion from linked tasks

### Story Points (rollup)
- Sum of story points from linked tasks

### Total Tasks Count (rollup)
- Count of linked tasks

### Title Score (AI) / Title QA (AI)
- AI-generated title quality assessments

# Sprints Database Schema

Database ID: `1c3935be-7993-806e-ab98-c5f92caaa4c0`

## Properties

### Sprint name (title)
- Sprint identifier

### Dates (date)
- Sprint start and end dates

### Sprint ID (number or text)
- Sprint number

### Sprint status (select)
- e.g., Active, Completed, Planned

### Sprint Goal (rich_text)
- Sprint objectives

## Relations

### Tasks
- Links to: Tasks database

## Computed Fields

### Story Points (rollup)
- Total story points in sprint

### Completed Story Points (rollup)
- Completed points

### Total tasks / Completed tasks (rollup)
- Task counts

# Initiatives Database Schema

Database ID: `1c3935be-7993-8097-ab61-de7f9a12e31b`

## Properties

### Name (title)
### Description (rich_text)
### Status (status)
### Priority (select)
### Owner (people)
### Timeline (date)
### Start Date (date)
### Classification (select)
### Success Metrics (rich_text)
### Goals (rich_text)

## Relations

### Epics
- Links to: Epics database
