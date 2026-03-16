---
name: dataflint-notion
description: Manage DataFlint's Notion workspace — create and query tasks, epics, sprints, and initiatives. Use when the user asks to create a task/ticket, check sprint status, look up epics, query the backlog, update task status, find "my tickets", or interact with any DataFlint Notion database. Also use when the user mentions Notion, DATAFLINT-<number> task IDs, sprint/epic planning, or asks about current sprint.
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

## Team Members

| Name              | Email                | User ID                                |
|-------------------|----------------------|----------------------------------------|
| Leon Shklyar      | leon@dataflint.io    | `1d8d872b-594c-8149-b9a0-0002b380e75a` |
| Ariel Krinitsi    | ariel@dataflint.io   | `172d872b-594c-818c-8a7e-00022746b3d3` |
| Maxim Kirilov     | maxim@dataflint.io   | `267d872b-594c-8151-b106-0002694c3bf2` |
| Meni Shmueli      | meni@dataflint.io    | `9cb10362-fe75-4c22-a51f-f88b32c3a0b4` |
| Avi Minsky        | avi@dataflint.io     | `31ad872b-594c-8124-b64d-0002342613ce` |
| Orel Jaraian      | orel@dataflint.io    | `1c6d872b-594c-8120-ba63-0002891a04af` |
| Daniel Aronovich  | daniel@dataflint.io  | `cfe7a615-c58b-49c8-ace9-6b91c16ad1b9` |
| Geffen Fridman    | geffen@dataflint.io  | `1a0d872b-594c-81df-b10f-00024a8f3f3b` |
| Andrei Michlin    | andrei@dataflint.io  | `21ed872b-594c-8126-9d60-000274d65566` |
| Natalie Miller    | natalie@dataflint.io | `12ed872b-594c-8153-94f7-0002ecf9dd3e` |
| yuval nachshon    | yuval@dataflint.io   | `31ad872b-594c-81e4-a576-0002f7f11f3a` |
| marais kruger     | marais@dataflint.io  | `21ed872b-594c-81ae-9503-0002153515f6` |

When the user says "my tickets" or "assigned to me", match their identity by git config email, OS username, or ask. Default to Leon Shklyar if the OS user is `leon.sh`.

## Finding the Current Sprint

Query the Sprints database filtering by `Sprint status` equals `"Current"`:

```json
filter: { "property": "Sprint status", "status": { "equals": "Current" } }
```

This returns the active sprint page. Extract its `id` to use in task queries and task creation.

### Sprint Status Values

| Status  | Meaning                    |
|---------|----------------------------|
| Current | Active sprint              |
| Next    | Upcoming planned sprint    |
| Future  | Further out planned sprint |
| Last    | Most recently completed    |
| Past    | Older completed sprints    |

## Creating a Task

Use `create-page` with `parent_type: "database_id"` and `parent_id` set to the Tasks database ID.

**Always assign the current sprint** unless the user explicitly says otherwise. First find the current sprint page ID (see above), then include it in the Sprint relation.

Required properties:
```json
{
  "Task name": { "title": [{ "text": { "content": "Task title here" } }] },
  "Status": { "status": { "name": "Backlog" } },
  "Sprint": { "relation": [{ "id": "<current_sprint_page_id>" }] }
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

## "My Tickets in Current Sprint"

This is a two-step workflow:

1. **Find current sprint** — query Sprints database with filter `Sprint status` equals `"Current"`, extract the sprint page ID.

2. **Query tasks** — query Tasks database with combined filter:

```json
{
  "and": [
    { "property": "Sprint", "relation": { "contains": "<current_sprint_page_id>" } },
    { "property": "Assignee", "people": { "contains": "<user_id>" } },
    { "property": "Status", "status": { "does_not_equal": "Done" } },
    { "property": "Status", "status": { "does_not_equal": "Archived" } },
    { "property": "Status", "status": { "does_not_equal": "Deferred" } }
  ]
}
```

Present results grouped by status: In progress first, then Blocked, In Review, Backlog.

## All Current Sprint Tasks

Same two-step workflow but without the Assignee filter:

```json
{
  "and": [
    { "property": "Sprint", "relation": { "contains": "<current_sprint_page_id>" } },
    { "property": "Status", "status": { "does_not_equal": "Done" } },
    { "property": "Status", "status": { "does_not_equal": "Archived" } }
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

**Move to current sprint:**
```json
{ "Sprint": { "relation": [{ "id": "<current_sprint_page_id>" }] } }
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
