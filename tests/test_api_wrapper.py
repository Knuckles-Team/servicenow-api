import pytest

pytestmark = pytest.mark.integration

import os
import sys

import pytest

reason = "Skipped"

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    import servicenow_api
except ImportError:
    skip = True
else:
    skip = False


reason = "do not run on MacOS or windows OR dependency is not installed OR " + reason


@pytest.mark.skipif(
    sys.platform in ["darwin", "win32"] or skip,
    reason=reason,
)
def test_servicenow_api():
    servicenow_url = "http://servicenow.com/api/"
    token = os.environ.get("token", default="NA")
    client = servicenow_api.Api(url=servicenow_url, token=token, verify=False)
    table = client.get_table(table="users")
    assert table == list


if __name__ == "__main__":
    test_servicenow_api()
