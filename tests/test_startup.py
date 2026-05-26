def test_server_startup():
    """
    CONCEPT:OS-5.0: Agent OS Kernel & XDG Paths
    Validates that the server module can start successfully and lazy loads attributes.
    """
    import servicenow_api

    # Assert basic package exposure and structures
    assert hasattr(servicenow_api, "Api")
    assert servicenow_api.Api is not None

    # Assert dynamic lazy attributes are retrievable
    assert hasattr(servicenow_api, "_MCP_AVAILABLE")
    assert hasattr(servicenow_api, "_AGENT_AVAILABLE")
    assert isinstance(servicenow_api._MCP_AVAILABLE, bool)
    assert isinstance(servicenow_api._AGENT_AVAILABLE, bool)

    # Check that dir exposes elements
    attrs = dir(servicenow_api)
    assert "Api" in attrs
    assert "_expose_members" not in attrs

    print("Startup tests verified successfully with assertions.")
