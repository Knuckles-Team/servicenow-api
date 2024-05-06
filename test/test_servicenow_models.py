import os
import sys

import pytest
from conftest import reason

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    import servicenow_api
    from servicenow_api.servicenow_models import (ApplicationServiceModel, CMDBModel, CICDModel, ChangeManagementModel,
                                                  IncidentModel, ImportSetModel, KnowledgeManagementModel, TableModel)

except ImportError:
    skip = True
    raise ("ERROR IMPORTING", ImportError)
else:
    skip = False


reason = "do not run on MacOS or windows OR dependency is not installed OR " + reason


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
    )
def test_servicenow_models():
    # test Project model group_id
    article_sys_id = "asdofaisudfa098098as0df9a8s"
    article = KnowledgeManagementModel(article_sys_id=article_sys_id)
    assert article_sys_id == article.article_sys_id


if __name__ == "__main__":
    test_servicenow_models()
