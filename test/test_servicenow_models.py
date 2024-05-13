import os
import sys

import pytest
from conftest import reason

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    import servicenow_api
    from servicenow_api.servicenow_models import (
        ApplicationServiceModel,
        CMDBModel,
        CICDModel,
        ChangeManagementModel,
        IncidentModel,
        ImportSetModel,
        KnowledgeManagementModel,
        TableModel,
    )

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
def test_servicenow_article():
    article_sys_id = "asdofaisudfa098098as0df9a8s"
    article = KnowledgeManagementModel(article_sys_id=article_sys_id)
    assert article_sys_id == article.article_sys_id


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_change():
    change_request_sys_id = "asdofaisudfa098098as0df9a8s"
    change = ChangeManagementModel(change_request_sys_id=change_request_sys_id)
    assert change_request_sys_id == change.change_request_sys_id


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_incident():
    incident_id = "asdofaisudfa098098as0df9a8s"
    incident = IncidentModel(incident_id=incident_id)
    assert incident_id == incident.incident_id


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_cicd():
    result_id = "asdofaisudfa098098as0df9a8s"
    cicd = CICDModel(result_id=result_id)
    assert result_id == cicd.result_id


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_application():
    application_id = "asdofaisudfa098098as0df9a8s"
    application = ApplicationServiceModel(application_id=application_id)
    assert application_id == application.application_id


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_table():
    table_name = "users"
    table = TableModel(table=table_name)
    assert table_name == table.table


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_import_set():
    import_set_sys_id = "asdofaisudfa098098as0df9a8s"
    import_set = ImportSetModel(import_set_sys_id=import_set_sys_id)
    assert import_set_sys_id == import_set.import_set_sys_id


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_cmdb():
    cmdb_id = "asdofaisudfa098098as0df9a8s"
    cmdb = CMDBModel(cmdb_id=cmdb_id)
    assert cmdb_id == cmdb.cmdb_id


if __name__ == "__main__":
    test_servicenow_article()
    test_servicenow_change()
    test_servicenow_incident()
    test_servicenow_cicd()
    test_servicenow_application()
    test_servicenow_table()
    test_servicenow_import_set()
    test_servicenow_cmdb()
