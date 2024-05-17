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
        Response,
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
    sysparm_query = "assignment_group=1234556789asdfv81238a"
    name_value_pairs = "assignment_group=1234556789asdfv81238a"
    change = ChangeManagementModel(
        change_request_sys_id=change_request_sys_id, sysparm_query=sysparm_query
    )
    assert change.change_request_sys_id == change_request_sys_id
    assert change.sysparm_query == sysparm_query
    assert (
        change.api_parameters == "?sysparm_query=assignment_group=1234556789asdfv81238a"
    )
    change.sysparm_offset = 100
    assert (
        change.api_parameters
        == "?sysparm_query=assignment_group=1234556789asdfv81238a&sysparm_offset=100"
    )
    change.sysparm_query = ""
    change.name_value_pairs = name_value_pairs
    change.sysparm_offset = 500
    assert (
        change.api_parameters
        == "?assignment_group=1234556789asdfv81238a&sysparm_offset=500"
    )


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


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_responses():
    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "c159b1e9db1c0010b5e3f6c5ae961903",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/c159b1e9db1c0010b5e3f6c5ae961903",
                }
            },
            "status": "0",
            "status_label": "Pending",
            "status_message": "",
            "status_detail": "",
            "error": "",
            "percent_complete": 0,
            "rollback_version": "1.1.0",
        }
    }
    response = Response(**example_data)
    assert response.result.links.progress.id == "c159b1e9db1c0010b5e3f6c5ae961903"

    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "c159b1e9db1c0010b5e3f6c5ae961903",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/c159b1e9db1c0010b5e3f6c5ae961903"
                }
            },
            "status": "0",
            "status_label": "Pending",
            "status_message": "",
            "status_detail": "",
            "error": "",
            "percent_complete": 0
        }
    }
    response = Response(**example_data)
    assert response.result.links.progress.id == "c159b1e9db1c0010b5e3f6c5ae961903"
    assert response.result.status == "0"

    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "c159b1e9db1c0010b5e3f6c5ae961903",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/c159b1e9db1c0010b5e3f6c5ae961903"
                },
                "results": {
                    "id": "df24b1e9db2d0110b5e3f6c5ae97c561",
                    "url": "https://instance.servicenow.com/api/sn_cicd/app/batch/results/df24b1e9db2d0110b5e3f6c5ae97c561"
                },
                "rollback": {
                    "id": "a329f82e871da64c724ba21c82a764f2"
                }
            },
            "status": "0",
            "status_label": "Pending",
            "status_message": "",
            "status_detail": "",
            "error": "",
            "percent_complete": 0
        }
    }
    response = Response(**example_data)
    assert response.result.links.results.id == "df24b1e9db2d0110b5e3f6c5ae97c561"
    assert response.result.percent_complete == 0

    example_data = {
        "result": {
            "links": {
                "results": {
                    "id": "2891389d1b1040103d374087bc4bcb09",
                    "url": "https://instance.servicenow.com/sys_atf_test_suite_result.do?sys_id=2891389d1b1040103d374087bc4bcb09"
                }
            },
            "status": "2",
            "status_label": "Successful",
            "status_message": "",
            "status_detail": "",
            "error": "",
            "test_suite_status": "success",
            "test_suite_duration": "1 Second",
            "rolledup_test_success_count": 1,
            "rolledup_test_failure_count": 0,
            "rolledup_test_error_count": 0,
            "rolledup_test_skip_count": 0,
            "test_suite_name": "Quick Test",
            "child_suite_results": []
        }
    }
    response = Response(**example_data)
    assert response.result.links.results.id == "2891389d1b1040103d374087bc4bcb09"
    assert response.result.rolledup_test_skip_count == 0

    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "a4fae8911bdc00103d374087bc4bcbbd",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/a4fae8911bdc00103d374087bc4bcbbd"
                },
                "source": {
                    "id": "59c4c4d11b5c00103d374087bc4bcb26",
                    "url": "https://instance.servicenow.com/api/now/table/sys_app/59c4c4d11b5c00103d374087bc4bcb26"
                }
            },
            "status": "2",
            "status_label": "Successful",
            "status_message": "This operation succeeded",
            "status_detail": "Successfully applied commit 1f14e11a7dedcbfa194beb5875fcdaa15ed8accb from source control",
            "error": "",
            "percent_complete": 100
        }
    }

    response = Response(**example_data)
    assert response.result.links.progress.id == "a4fae8911bdc00103d374087bc4bcbbd"
    assert response.result.percent_complete == 100

    example_data = {
        "result": {
            "batch_plan": {
                "name": "Release 2.0 IT Operations",
                "id": "df24b1e9db2d0110b5e3f6c5ae97c561",
                "url": "https://instance.service-now.com/sys_batch_install_plan.do?sys_id=df24b1e9db2d0110b5e3f6c5ae97c561",
                "state": "Installed",
                "notes": "User specified notes for batch install plan"
            },
            "batch_items": [
                {
                    "name": "com.sn_cicd_spoke",
                    "type": "Application",
                    "version": "7.0.0",
                    "state": "Installed",
                    "install_date": "2020-08-31 15:30:01",
                    "id": "c159b1e9db1c0010b5e3f6c5ae961903",
                    "url": "https://instance.service-now.com/sys_batch_install_item.do?sys_id=c159b1e9db1c0010b5e3f6c5ae961903",
                    "notes": ""
                },
                {
                    "name": "Customization for CSM App1",
                    "type": "Application",
                    "version": "1.0.0",
                    "state": "Installed",
                    "install_date": "2020-08-31 15:32:01",
                    "id": "e824b1e9db2d1001b5e3f6c5ae97d628",
                    "url": "https://instance.service-now.com/sys_batch_install_item.do?sys_id=e824b1e9db2d1001b5e3f6c5ae97d628",
                    "notes": "Customized headers.",
                    "customization_version": "2.1.1",
                    "status_message": ""
                }
            ]
        }
    }

    response = Response(**example_data)
    assert response.result.batch_plan.name == "Release 2.0 IT Operations"
    assert response.result.batch_items[0].name == "com.sn_cicd_spoke"

if __name__ == "__main__":
    test_servicenow_article()
    test_servicenow_change()
    test_servicenow_incident()
    test_servicenow_cicd()
    test_servicenow_application()
    test_servicenow_table()
    test_servicenow_import_set()
    test_servicenow_cmdb()
