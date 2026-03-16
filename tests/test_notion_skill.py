"""Functional tests for the dataflint-notion skill.

Each test exercises a pattern documented in SKILL.md against the live
Notion API.  Tests that create pages clean up after themselves via the
``cleanup_pages`` fixture.

Requires: NOTION_TOKEN env var.
Run:      pytest tests/ -v
"""

import pytest
from conftest import (
    ALL_DB_IDS,
    TASKS_DB,
    SPRINTS_DB,
    TEAM_MEMBERS,
    _get_data_source_id,
)


# ── Database accessibility ────────────────────────────────────────────


class TestDatabasesExist:
    """Every database ID in the skill must be reachable."""

    @pytest.mark.parametrize("name,db_id", ALL_DB_IDS.items())
    def test_database_accessible(self, notion, name, db_id):
        db = notion.databases.retrieve(database_id=db_id)
        assert db["id"].replace("-", "") == db_id.replace("-", "")


# ── Tasks schema ─────────────────────────────────────────────────────


class TestTasksSchema:
    """Properties referenced in SKILL.md must exist with the right types."""

    EXPECTED_PROPERTIES = {
        "Task name": "title",
        "Status": "status",
        "Priority": "select",
        "Category": "select",
        "Service": "multi_select",
        "Label": "multi_select",
        "Story Points": "number",
        "Estimates": "select",
        "Assignee": "people",
        "Epic": "relation",
        "Sprint": "relation",
        "Task ID": "unique_id",
        "Due": "date",
        "Environment": "select",
    }

    @pytest.fixture(scope="class")
    def tasks_schema(self, notion):
        ds_id = _get_data_source_id(notion, TASKS_DB)
        return notion.data_sources.retrieve(data_source_id=ds_id)

    @pytest.mark.parametrize(
        "prop_name,expected_type", EXPECTED_PROPERTIES.items()
    )
    def test_property_exists_with_type(self, tasks_schema, prop_name, expected_type):
        props = tasks_schema["properties"]
        assert prop_name in props, f"Property '{prop_name}' missing from Tasks DB"
        assert props[prop_name]["type"] == expected_type, (
            f"'{prop_name}' expected type '{expected_type}', "
            f"got '{props[prop_name]['type']}'"
        )

    def test_status_options(self, tasks_schema):
        status = tasks_schema["properties"]["Status"]["status"]
        option_names = {o["name"] for o in status["options"]}
        expected = {
            "Backlog", "Paused", "In progress", "Blocked", "In Review",
            "Review Request Changes", "Production Pending",
            "Done", "Deferred", "Duplicate", "Archived",
        }
        missing = expected - option_names
        assert not missing, f"Missing status options: {missing}"

    def test_priority_options(self, tasks_schema):
        options = tasks_schema["properties"]["Priority"]["select"]["options"]
        names = {o["name"] for o in options}
        expected = {"Low", "Medium", "High", "Critical"}
        missing = expected - names
        assert not missing, f"Missing priority options: {missing}"

    def test_estimates_options(self, tasks_schema):
        options = tasks_schema["properties"]["Estimates"]["select"]["options"]
        names = {o["name"] for o in options}
        expected = {"XS", "S", "M", "L", "XL"}
        missing = expected - names
        assert not missing, f"Missing estimates options: {missing}"

    def test_task_id_prefix(self, tasks_schema):
        uid = tasks_schema["properties"]["Task ID"]["unique_id"]
        assert uid["prefix"] == "DATAFLINT", (
            f"Task ID prefix is '{uid['prefix']}', expected 'DATAFLINT'"
        )


# ── Sprint schema & workflow ─────────────────────────────────────────


class TestSprintWorkflow:

    def test_current_sprint_exists(self, current_sprint):
        status = current_sprint["properties"]["Sprint status"]["status"]
        assert status["name"] == "Current"

    def test_sprint_has_name(self, current_sprint):
        title = current_sprint["properties"]["Sprint name"]["title"]
        assert len(title) > 0, "Current sprint has no name"

    def test_sprint_status_options(self, notion):
        ds_id = _get_data_source_id(notion, SPRINTS_DB)
        schema = notion.data_sources.retrieve(data_source_id=ds_id)
        options = schema["properties"]["Sprint status"]["status"]["options"]
        names = {o["name"] for o in options}
        expected = {"Current", "Next", "Future", "Last", "Past"}
        missing = expected - names
        assert not missing, f"Missing sprint status options: {missing}"


# ── Team member IDs ───────────────────────────────────────────────────


class TestTeamMembers:

    @pytest.mark.parametrize("name,user_id", TEAM_MEMBERS.items())
    def test_user_id_valid(self, notion, name, user_id):
        user = notion.users.retrieve(user_id=user_id)
        assert user["id"].replace("-", "") == user_id.replace("-", "")


# ── Create task ───────────────────────────────────────────────────────


class TestCreateTask:
    """Verify the create-task JSON format from SKILL.md works end-to-end."""

    def test_create_minimal_task(self, notion, cleanup_pages):
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] Minimal task"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
            },
        )
        cleanup_pages.append(page["id"])

        assert page["properties"]["Status"]["status"]["name"] == "Backlog"
        title_text = page["properties"]["Task name"]["title"][0]["plain_text"]
        assert title_text == "[TEST] Minimal task"

    def test_create_task_with_sprint(self, notion, current_sprint, cleanup_pages):
        sprint_id = current_sprint["id"]
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] Sprint-assigned task"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
                "Sprint": {"relation": [{"id": sprint_id}]},
            },
        )
        cleanup_pages.append(page["id"])

        sprint_rel = page["properties"]["Sprint"]["relation"]
        sprint_ids = [r["id"] for r in sprint_rel]
        assert sprint_id in sprint_ids, "Task not linked to current sprint"

    def test_create_task_with_all_optional_fields(
        self, notion, current_sprint, cleanup_pages
    ):
        leon_id = TEAM_MEMBERS["Leon Shklyar"]
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] Full task"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
                "Sprint": {"relation": [{"id": current_sprint["id"]}]},
                "Priority": {"select": {"name": "High"}},
                "Category": {"select": {"name": "Develop"}},
                "Service": {"multi_select": [{"name": "Dataflint API server"}]},
                "Label": {"multi_select": [{"name": "bug"}]},
                "Story Points": {"number": 3},
                "Estimates": {"select": {"name": "M"}},
                "Assignee": {"people": [{"id": leon_id}]},
            },
        )
        cleanup_pages.append(page["id"])

        props = page["properties"]
        assert props["Priority"]["select"]["name"] == "High"
        assert props["Category"]["select"]["name"] == "Develop"
        assert props["Story Points"]["number"] == 3
        assert props["Estimates"]["select"]["name"] == "M"
        services = [s["name"] for s in props["Service"]["multi_select"]]
        assert "Dataflint API server" in services
        labels = [l["name"] for l in props["Label"]["multi_select"]]
        assert "bug" in labels
        assignees = [a["id"] for a in props["Assignee"]["people"]]
        assert leon_id in assignees


# ── Query tasks ───────────────────────────────────────────────────────


class TestQueryTasks:

    def test_query_by_status(self, notion, tasks_ds_id):
        results = notion.data_sources.query(
            data_source_id=tasks_ds_id,
            filter={"property": "Status", "status": {"equals": "In progress"}},
            page_size=1,
        )
        assert "results" in results

    def test_query_by_dataflint_id(self, notion, tasks_ds_id, cleanup_pages):
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] ID lookup"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
            },
        )
        cleanup_pages.append(page["id"])

        task_id_num = page["properties"]["Task ID"]["unique_id"]["number"]

        results = notion.data_sources.query(
            data_source_id=tasks_ds_id,
            filter={
                "property": "Task ID",
                "unique_id": {"equals": task_id_num},
            },
        )["results"]
        assert len(results) == 1
        assert results[0]["id"] == page["id"]

    def test_query_by_assignee(self, notion, tasks_ds_id):
        leon_id = TEAM_MEMBERS["Leon Shklyar"]
        results = notion.data_sources.query(
            data_source_id=tasks_ds_id,
            filter={
                "property": "Assignee",
                "people": {"contains": leon_id},
            },
            page_size=1,
        )
        assert "results" in results

    def test_query_current_sprint_tasks(self, notion, tasks_ds_id, current_sprint):
        sprint_id = current_sprint["id"]
        results = notion.data_sources.query(
            data_source_id=tasks_ds_id,
            filter={
                "and": [
                    {"property": "Sprint", "relation": {"contains": sprint_id}},
                    {"property": "Status", "status": {"does_not_equal": "Done"}},
                    {"property": "Status", "status": {"does_not_equal": "Archived"}},
                ]
            },
            page_size=5,
        )
        assert "results" in results
        for task in results["results"]:
            status = task["properties"]["Status"]["status"]["name"]
            assert status not in ("Done", "Archived")

    def test_my_tickets_in_current_sprint(self, notion, tasks_ds_id, current_sprint):
        """End-to-end: the 'my tickets in current sprint' workflow from SKILL.md."""
        leon_id = TEAM_MEMBERS["Leon Shklyar"]
        sprint_id = current_sprint["id"]

        results = notion.data_sources.query(
            data_source_id=tasks_ds_id,
            filter={
                "and": [
                    {"property": "Sprint", "relation": {"contains": sprint_id}},
                    {"property": "Assignee", "people": {"contains": leon_id}},
                    {"property": "Status", "status": {"does_not_equal": "Done"}},
                    {"property": "Status", "status": {"does_not_equal": "Archived"}},
                    {"property": "Status", "status": {"does_not_equal": "Deferred"}},
                ]
            },
        )
        assert "results" in results
        for task in results["results"]:
            status = task["properties"]["Status"]["status"]["name"]
            assert status not in ("Done", "Archived", "Deferred")


# ── Update task ───────────────────────────────────────────────────────


class TestUpdateTask:

    def test_update_status(self, notion, cleanup_pages):
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] Status update"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
            },
        )
        cleanup_pages.append(page["id"])

        updated = notion.pages.update(
            page_id=page["id"],
            properties={"Status": {"status": {"name": "In progress"}}},
        )
        assert updated["properties"]["Status"]["status"]["name"] == "In progress"

    def test_update_assignee(self, notion, cleanup_pages):
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] Assign update"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
            },
        )
        cleanup_pages.append(page["id"])

        leon_id = TEAM_MEMBERS["Leon Shklyar"]
        updated = notion.pages.update(
            page_id=page["id"],
            properties={"Assignee": {"people": [{"id": leon_id}]}},
        )
        assignees = [a["id"] for a in updated["properties"]["Assignee"]["people"]]
        assert leon_id in assignees

    def test_move_to_sprint(self, notion, current_sprint, cleanup_pages):
        page = notion.pages.create(
            parent={"database_id": TASKS_DB},
            properties={
                "Task name": {
                    "title": [{"text": {"content": "[TEST] Sprint move"}}]
                },
                "Status": {"status": {"name": "Backlog"}},
            },
        )
        cleanup_pages.append(page["id"])

        sprint_id = current_sprint["id"]
        updated = notion.pages.update(
            page_id=page["id"],
            properties={"Sprint": {"relation": [{"id": sprint_id}]}},
        )
        sprint_ids = [r["id"] for r in updated["properties"]["Sprint"]["relation"]]
        assert sprint_id in sprint_ids
