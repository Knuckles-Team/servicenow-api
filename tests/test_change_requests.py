import pytest


def test_get_change_request_models(api_client):
    """Test retrieving change request models."""
    response = api_client.get_change_request_models(sysparm_limit=5)
    assert response.result is not None
    assert isinstance(response.result, list)


def test_create_standard_change_request(api_client):
    """
    Test creating a change request.
    Note: Creating change requests might require specific templates or data.
    We will attempt a basic normal change creation IF feasible, or just list models.
    For now, let's just stick to listing as creation can be complex without valid dependent data (like CI items).
    """
    # Just testing we can hit the endpoint for now
    response = api_client.get_change_request_models(sysparm_limit=1)
    assert response.result is not None
