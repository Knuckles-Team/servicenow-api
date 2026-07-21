import uuid


def test_get_problems(api_client):
    """Test retrieving problems from ServiceNow."""
    response = api_client.get_problems(sysparm_limit=5)
    assert response.result is not None
    assert isinstance(response.result, list)
    if response.result:
        assert hasattr(response.result[0], "sys_id")


def test_get_problem(api_client):
    """Test retrieving a specific problem record."""
    response = api_client.get_problem(problem_id="prb_123")
    assert response.result is not None
    assert response.result.sys_id == "prb_123"


def test_create_problem(api_client):
    """Test creating a new problem."""
    short_description = f"Test Problem from Pytest {uuid.uuid4()}"
    description = "This is a test problem created by automated verification."

    data = {"short_description": short_description, "description": description}

    response = api_client.create_problem(data=data)
    assert response.result is not None
    assert response.result.short_description == short_description

    sys_id = response.result.sys_id
    get_response = api_client.get_problems(sysparm_query=f"sys_id={sys_id}")
    assert len(get_response.result) == 1
    assert get_response.result[0].sys_id == sys_id


def test_update_problem(api_client):
    """Test updating an existing problem record."""
    response = api_client.update_problem(
        problem_id="prb_123", data={"known_error": True}
    )
    assert response.result is not None
    assert response.result.sys_id == "prb_123"


def test_delete_problem(api_client):
    """Test deleting a problem record."""
    response = api_client.delete_problem(problem_id="prb_123")
    assert response.result is not None
