import pytest
import uuid


def test_get_incidents(api_client):
    """Test retrieving incidents from ServiceNow."""
    response = api_client.get_incidents(sysparm_limit=5)
    assert response.result is not None
    assert isinstance(response.result, list)
    # If there are incidents, check structure (optional, depends if instance has data)
    if response.result:
        assert hasattr(response.result[0], "sys_id")


def test_create_incident(api_client):
    """Test creating a new incident."""
    short_description = f"Test Incident from Pytest {uuid.uuid4()}"
    description = "This is a test incident created by automated verification."

    data = {"short_description": short_description, "description": description}

    response = api_client.create_incident(data=data)
    assert response.result is not None
    assert response.result.short_description == short_description

    # Optional: Verify it exists via get
    sys_id = response.result.sys_id
    get_response = api_client.get_incidents(sysparm_query=f"sys_id={sys_id}")
    assert len(get_response.result) == 1
    assert get_response.result[0].sys_id == sys_id
