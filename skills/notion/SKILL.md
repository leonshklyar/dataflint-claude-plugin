---
name: dataflint-notion
description: Manage DataFlint's Notion workspace — create and query tasks, epics, sprints, and initiatives. Use when the user asks to create a task/ticket, check sprint status, look up epics, query the backlog, update task status, or interact with any DataFlint Notion database. Also use when the user mentions Notion, DATAFLINT-<number> task IDs, or sprint/epic planning.
---

# DataFlint Notion Workspace

Interact with DataFlint's Notion project management workspace using the Notion MCP tools.

## Database IDs

| Database    | ID                                     | Prefix     |
|-------------|----------------------------------------|------------|
| Tasks       | `62ae2b8f-746e-4f98-9b66-60e66381822f` | DATAFLINT- |
| Epics       | `1c3935be-7993-805b-bf10-e1190f8bd8b9` |            |
| Sprints     | `1c3935be-7993-806e-ab98-c5f92caaa4c0` |            |
| Initiatives | `1c3935be-7993-8097-ab61-de7f9a12e31b` |            |
| Product     | `1c8935be-7993-807a-a30d-d371d230024b` |            |

## Creating a Task

Use `create-page` with `parent_type: "database_id"` and `parent_id` set to the Tasks database ID.

Required properties:
```json
{
  "Task name": { "title": [{ "text": { "content": "Task title here" } }] },
  "Status": { "status": { "name": "Backlog" } }
}
```

Common optional properties to include when relevant:

```json
{
  "Priority": { "select": { "name": "High" } },
  "Category": { "select": { "name": "Develop" } },
  "Service": { "multi_select": [{ "name": "Dataflint API server" }] },
  "Label": { "multi_select": [{ "name": "bug" }] },
  "Story Points": { "number": 3 },
  "Estimates": { "select": { "name": "M" } },
  "Epic": { "relation": [{ "id": "<epic_page_id>" }] },
  "Assignee": { "people": [{ "id": "<user_id>" }] }
}
```

For the full schema including all property options, see [references/tasks-schema.md](references/tasks-schema.md).

## Querying Tasks

Use `query-database` with the Tasks database ID.

**By status:**
```json
{
  "property": "Status",
  "status": { "equals": "In progress" }
}
```

**By DATAFLINT ID (e.g. DATAFLINT-1234):**
```json
{
  "property": "Task ID",
  "unique_id": { "equals": 1234 }
}
```

**By assignee:**
```json
{
  "property": "Assignee",
  "people": { "contains": "<user_id>" }
}
```

**Current sprint tasks (combine filters):**
```json
{
  "and": [
    { "property": "Status", "status": { "does_not_equal": "Done" } },
    { "property": "Status", "status": { "does_not_equal": "Archived" } },
    { "property": "Sprint", "relation": { "contains": "<sprint_page_id>" } }
  ]
}
```

## Querying Epics

Use `query-database` with the Epics database ID.

**Active epics:**
```json
{
  "property": "Status",
  "status": { "equals": "In progress" }
}
```

## Querying Sprints

Use `query-database` with the Sprints database ID.

**Current sprint:** Query with sort by `Dates` descending, limit 1, filter `Sprint status` equals "Active".

## Updating a Task

Use `update-page` with the task's page ID. Find the page ID first by querying for the task.

**Change status:**
```json
{ "Status": { "status": { "name": "In progress" } } }
```

**Assign someone:**
```json
{ "Assignee": { "people": [{ "id": "<user_id>" }] } }
```

## Status Values

| Group       | Statuses                                                             |
|-------------|----------------------------------------------------------------------|
| To-do       | Backlog, Paused                                                      |
| In progress | In progress, Blocked, In Review, Review Request Changes, Production Pending |
| Complete    | Done, Deferred, Duplicate, Archived                                  |

## Priority Values

Low, Medium, High, Critical

## Category Values

Bug, Customers, Develop, Incident, Managment, Infra, Operations, Marketing, Support, dev, Notion, Feature, Research, Config

## Estimates (T-Shirt Sizing)

XS, S, M, L, XL

## Service Values

CI/CD, Open source, History server, DB, Dataflint API server, Databricks Ingestion Engine, EMR Ingestion Engine, Ingestion, SaaS Client, Local Env, Infra, EMR Loader, Landing Page, MCP Server, old webapp, IDE Extention, New Webapp, Engine, S3 Listing Ingestion, Dataflint Engine

## Additional Resources

- For full Tasks database schema with all property IDs and option IDs, see [references/tasks-schema.md](references/tasks-schema.md)
- For Epics database schema, see [references/epics-schema.md](references/epics-schema.md)
