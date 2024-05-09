import pytest

skip_openai = False
skip_redis = False
skip_docker = False
reason = "requested to skip"


# Registers command-line options like '--skip-openai' and '--skip-redis' via pytest hook.
# When these flags are set, it indicates that tests requiring OpenAI or Redis (respectively) should be skipped.
def pytest_addoption(parser):
    parser.addoption(
        "--skip-docker", action="store_true", help="Skip all tests that require docker"
    )


# pytest hook implementation extracting command line args and exposing it globally
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    global skip_docker
    skip_docker = config.getoption("--skip-docker", False)
