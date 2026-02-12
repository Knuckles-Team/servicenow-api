import pytest


def test_get_users(api_client):
    """Test retrieving users from sys_user table."""
    response = api_client.get_table(table="sys_user", sysparm_limit=5)
    assert response.result is not None
    assert isinstance(response.result, list)
    if response.result:
        user = response.result[0]
        assert hasattr(user, "sys_id") or "sys_id" in user


def test_get_current_user(api_client, servicenow_config):
    """Test retrieving specific user (admin) to verify connectivity."""
    username = servicenow_config["username"]
    response = api_client.get_table(
        table="sys_user", sysparm_query=f"user_name={username}", sysparm_limit=1
    )
    assert response.result is not None
    assert len(response.result) == 1
    user = response.result[0]
    if hasattr(user, "user_name"):
        assert user.user_name == username
    else:
        assert user["user_name"] == username
