import os
import pytest
from notion_client import Client


TASKS_DB = "62ae2b8f-746e-4f98-9b66-60e66381822f"
EPICS_DB = "1c3935be-7993-805b-bf10-e1190f8bd8b9"
SPRINTS_DB = "1c3935be-7993-806e-ab98-c5f92caaa4c0"
INITIATIVES_DB = "1c3935be-7993-8097-ab61-de7f9a12e31b"
PRODUCT_DB = "1c8935be-7993-807a-a30d-d371d230024b"

ALL_DB_IDS = {
    "Tasks": TASKS_DB,
    "Epics": EPICS_DB,
    "Sprints": SPRINTS_DB,
    "Initiatives": INITIATIVES_DB,
    "Product": PRODUCT_DB,
}

TEAM_MEMBERS = {
    "Leon Shklyar": "1d8d872b-594c-8149-b9a0-0002b380e75a",
    "Ariel Krinitsi": "172d872b-594c-818c-8a7e-00022746b3d3",
    "Maxim Kirilov": "267d872b-594c-8151-b106-0002694c3bf2",
    "Meni Shmueli": "9cb10362-fe75-4c22-a51f-f88b32c3a0b4",
    "Avi Minsky": "31ad872b-594c-8124-b64d-0002342613ce",
    "Orel Jaraian": "1c6d872b-594c-8120-ba63-0002891a04af",
    "Daniel Aronovich": "cfe7a615-c58b-49c8-ace9-6b91c16ad1b9",
    "Geffen Fridman": "1a0d872b-594c-81df-b10f-00024a8f3f3b",
    "Andrei Michlin": "21ed872b-594c-8126-9d60-000274d65566",
    "Natalie Miller": "12ed872b-594c-8153-94f7-0002ecf9dd3e",
    "yuval nachshon": "31ad872b-594c-81e4-a576-0002f7f11f3a",
    "marais kruger": "21ed872b-594c-81ae-9503-0002153515f6",
}


@pytest.fixture(scope="session")
def notion():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        pytest.skip("NOTION_TOKEN not set")
    return Client(auth=token)


def _get_data_source_id(notion, database_id):
    """Resolve a database_id to its data_source_id (notion-client v3)."""
    db = notion.databases.retrieve(database_id=database_id)
    return db["data_sources"][0]["id"]


@pytest.fixture(scope="session")
def tasks_ds_id(notion):
    return _get_data_source_id(notion, TASKS_DB)


@pytest.fixture(scope="session")
def sprints_ds_id(notion):
    return _get_data_source_id(notion, SPRINTS_DB)


@pytest.fixture(scope="session")
def current_sprint(notion, sprints_ds_id):
    """Find the current sprint once for all tests."""
    results = notion.data_sources.query(
        data_source_id=sprints_ds_id,
        filter={"property": "Sprint status", "status": {"equals": "Current"}},
    )["results"]
    assert len(results) >= 1, "No sprint with status 'Current' found"
    return results[0]


@pytest.fixture
def cleanup_pages(notion):
    """Collect page IDs during a test, archive them all on teardown."""
    page_ids = []
    yield page_ids
    for pid in page_ids:
        try:
            notion.pages.update(page_id=pid, archived=True)
        except Exception:
            pass
