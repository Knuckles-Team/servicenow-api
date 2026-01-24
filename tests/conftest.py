import os
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def servicenow_config():
    """Fixture to provide ServiceNow configuration from environment variables."""
    config = {
        "instance": os.getenv("SERVICENOW_INSTANCE"),
        "username": os.getenv("SERVICENOW_USERNAME"),
        "password": os.getenv("SERVICENOW_PASSWORD"),
    }

    if not all(config.values()):
        pytest.fail("Missing required ServiceNow environment variables in .env file.")

    return config


@pytest.fixture(scope="session")
def api_client(servicenow_config):
    """Fixture to provide an authenticated Service Now Api client."""
    # Import here to avoid circular dependencies or import errors if dependencies aren't ready
    from servicenow_api.servicenow_api import Api

    client = Api(
        url=servicenow_config["instance"],
        username=servicenow_config["username"],
        password=servicenow_config["password"],
    )
    return client
