import pytest


def test_get_users(api_client):
    """Test retrieving users from sys_user table."""
    # sys_user is the default user table
    response = api_client.get_table(table="sys_user", sysparm_limit=5)
    assert response.result is not None
    assert isinstance(response.result, list)
    if response.result:
        # Check for typical user fields
        user = response.result[0]
        # Pydantic models might return dicts or objects depending on implementation
        # But based on other tests, it seems to return objects (pydantic models)
        # However, get_table likely returns a generic Pydantic model or dict.
        # Let's handle both or minimal check.
        # Incident test checked 'sys_id' attribute.
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
    # Check if attribute or key
    if hasattr(user, "user_name"):
        assert user.user_name == username
    else:
        assert user["user_name"] == username
