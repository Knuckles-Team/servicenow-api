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
    assert change.api_parameters == {
        "sysparm_query": "assignment_group=1234556789asdfv81238a"
    }
    change.sysparm_offset = 100
    change.model_post_init(change)
    assert change.api_parameters == {
        "sysparm_query": "assignment_group=1234556789asdfv81238a",
        "sysparm_offset": 100,
    }
    change.sysparm_query = ""
    change.name_value_pairs = name_value_pairs
    change.sysparm_offset = 500
    change.model_post_init(change)
    assert change.api_parameters == {
        "name_value_pairs": "assignment_group=1234556789asdfv81238a",
        "sysparm_offset": 500,
    }


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
def test_servicenow_cicd_responses():
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
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.progress.id == "c159b1e9db1c0010b5e3f6c5ae961903"
    assert response.result.base_type == "CICD"

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
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.progress.id == "c159b1e9db1c0010b5e3f6c5ae961903"
    assert response.result.status == "0"
    assert response.result.base_type == "CICD"

    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "c159b1e9db1c0010b5e3f6c5ae961903",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/c159b1e9db1c0010b5e3f6c5ae961903",
                },
                "results": {
                    "id": "df24b1e9db2d0110b5e3f6c5ae97c561",
                    "url": "https://instance.servicenow.com/api/sn_cicd/app/batch/results/df24b1e9db2d0110b5e3f6c5ae97c561",
                },
                "rollback": {"id": "a329f82e871da64c724ba21c82a764f2"},
            },
            "status": "0",
            "status_label": "Pending",
            "status_message": "",
            "status_detail": "",
            "error": "",
            "percent_complete": 0,
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.results.id == "df24b1e9db2d0110b5e3f6c5ae97c561"
    assert response.result.percent_complete == 0
    assert response.result.base_type == "CICD"

    example_data = {
        "result": {
            "links": {
                "results": {
                    "id": "2891389d1b1040103d374087bc4bcb09",
                    "url": "https://instance.servicenow.com/sys_atf_test_suite_result.do?sys_id=2891389d1b1040103d374087bc4bcb09",
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
            "child_suite_results": [],
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.results.id == "2891389d1b1040103d374087bc4bcb09"
    assert response.result.rolledup_test_skip_count == 0
    assert response.result.base_type == "CICD"

    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "a4fae8911bdc00103d374087bc4bcbbd",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/a4fae8911bdc00103d374087bc4bcbbd",
                },
                "source": {
                    "id": "59c4c4d11b5c00103d374087bc4bcb26",
                    "url": "https://instance.servicenow.com/api/now/table/sys_app/59c4c4d11b5c00103d374087bc4bcb26",
                },
            },
            "status": "2",
            "status_label": "Successful",
            "status_message": "This operation succeeded",
            "status_detail": "Successfully applied commit 1f14e11a7dedcbfa194beb5875fcdaa15ed8accb from source control",
            "error": "",
            "percent_complete": 100,
        }
    }

    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.progress.id == "a4fae8911bdc00103d374087bc4bcbbd"
    assert response.result.percent_complete == 100
    assert response.result.base_type == "CICD"

    example_data = {
        "result": {
            "links": {
                "results": {
                    "id": "2891389d1b1040103d374087bc4bcb09",
                    "url": "https://instance.servicenow.com/sys_atf_test_suite_result.do?sys_id=2891389d1b1040103d374087bc4bcb09",
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
            "child_suite_results": [],
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.results.id == "2891389d1b1040103d374087bc4bcb09"
    assert response.result.base_type == "CICD"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_batch_install_responses():
    example_data = {
        "result": {
            "batch_plan": {
                "name": "Release 2.0 IT Operations",
                "id": "df24b1e9db2d0110b5e3f6c5ae97c561",
                "url": "https://instance.service-now.com/sys_batch_install_plan.do?sys_id=df24b1e9db2d0110b5e3f6c5ae97c561",
                "state": "Installed",
                "notes": "User specified notes for batch install plan",
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
                    "notes": "",
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
                    "status_message": "",
                },
            ],
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.batch_plan.name == "Release 2.0 IT Operations"
    assert response.result.batch_items[0].name == "com.sn_cicd_spoke"
    assert response.result.base_type == "BatchInstallResult"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_install_responses():
    example_data = {
        "result": {
            "links": {
                "progress": {
                    "id": "a4fae8911bdc00103d374087bc4bcbbd",
                    "url": "https://instance.servicenow.com/api/sn_cicd/progress/a4fae8911bdc00103d374087bc4bcbbd",
                },
                "source": {
                    "id": "59c4c4d11b5c00103d374087bc4bcb26",
                    "url": "https://instance.servicenow.com/api/now/table/sys_app/59c4c4d11b5c00103d374087bc4bcb26",
                },
            },
            "status": "2",
            "status_label": "Successful",
            "status_message": "This operation succeeded",
            "status_detail": "Successfully applied commit 1f14e11a7dedcbfa194beb5875fcdaa15ed8accb from source control",
            "error": "",
            "percent_complete": 100,
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.links.progress.id == "a4fae8911bdc00103d374087bc4bcbbd"
    assert response.result.status == "2"
    assert response.result.percent_complete == 100
    assert response.result.base_type == "CICD"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_oauth_responses():
    example_data = {
        "access_token": "CH1XAvt8FU1yjsRHq-ixDB1Fct4mpcztmvlD_2Wfu_F83thGqcPVfjvHsf8HvBi_ByeMsPXz1Igd5OYdADfXFw",
        "refresh_token": "EuoV22-H28J_frduuMUlKXcuJ-tFz9F2Pe_PSNa3Ml3H8bzG4FIn8ChCcmtLJkMeP_T4a-MBI-c6YRW_1D4Mcw",
        "scope": "useraccount",
        "token_type": "Bearer",
        "expires_in": 1799,
    }

    response = Response(**example_data, status_code=200, json=example_data)
    assert (
        response.access_token
        == "CH1XAvt8FU1yjsRHq-ixDB1Fct4mpcztmvlD_2Wfu_F83thGqcPVfjvHsf8HvBi_ByeMsPXz1Igd5OYdADfXFw"
    )


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_schedule_responses():
    example_data = {
        "result": {
            "worker": {
                "sysId": "d7d1f2b4a444b010f87712198fe9caae",
                "link": "https://instance.service-now.com/api/sn_chg_rest/change/worker/d7d1f2b4a444b010f87712198fe9caae",
            },
            "request": '{"cmdb_ci_sys_id":"82967cdd0ad3370236092104ce988d76","planned_start_time":"","duration_in_seconds":10800,"timezone":"America/Los_Angeles"}',
            "state": {"value": 3, "display_value": "Complete"},
            "type": "schedule",
            "messages": {
                "errorMessages": [],
                "warningMessages": [],
                "infoMessages": [],
            },
            "payload": {
                "spans": [
                    {
                        "start": {
                            "value": "2021-05-15 08:00:00",
                            "display_value": "2021-05-15 01:00:00",
                        },
                        "end": {
                            "value": "2021-05-15 11:00:00",
                            "display_value": "2021-05-15 04:00:00",
                        },
                    },
                    {
                        "start": {
                            "value": "2021-05-22 08:00:00",
                            "display_value": "2021-05-22 01:00:00",
                        },
                        "end": {
                            "value": "2021-05-22 11:00:00",
                            "display_value": "2021-05-22 04:00:00",
                        },
                    },
                ]
            },
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.worker.sysId == "d7d1f2b4a444b010f87712198fe9caae"
    assert response.result.base_type == "Schedule"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_change_requests_responses():
    example_data = {
        "result": [
            {
                "reason": {"display_value": "", "value": ""},
                "parent": {"display_value": "", "value": ""},
                "watch_list": {"display_value": "", "value": ""},
                "proposed_change": {"display_value": "", "value": ""},
                "upon_reject": {
                    "display_value": "Cancel all future Tasks",
                    "value": "cancel",
                },
                "sys_updated_on": {
                    "display_value": "2015-07-06 11:59:27",
                    "value": "2015-07-06 18:59:27",
                    "display_value_internal": "2015-07-06 11:59:27",
                },
                "type": {"display_value": "Standard", "value": "standard"},
                "approval_history": {"display_value": "", "value": ""},
                "skills": {"display_value": "", "value": ""},
                "test_plan": {
                    "display_value": "--Confirm that there are no monitoring alerts for the router",
                    "value": "--Confirm that there are no monitoring alerts for the router",
                },
                "number": {"display_value": "CHG0000024", "value": "CHG0000024"},
                "is_bulk": {"display_value": "false", "value": False},
                "cab_delegate": {"display_value": "", "value": ""},
                "requested_by_date": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "ci_class": {"display_value": "cmdb_ci", "value": "cmdb_ci"},
                "state": {"display_value": "Closed", "value": 3.0},
                "sys_created_by": {"display_value": "admin", "value": "admin"},
                "knowledge": {"display_value": "false", "value": False},
                "order": {"display_value": "", "value": ""},
                "phase": {"display_value": "Requested", "value": "requested"},
                "cmdb_ci": {"display_value": "", "value": ""},
                "delivery_plan": {"display_value": "", "value": ""},
                "impact": {"display_value": "3 - Low", "value": 3.0},
                "contract": {"display_value": "", "value": ""},
                "active": {"display_value": "false", "value": False},
                "work_notes_list": {"display_value": "", "value": ""},
                "priority": {"display_value": "4 - Low", "value": 4.0},
                "sys_domain_path": {"display_value": "/", "value": "/"},
                "cab_recommendation": {"display_value": "", "value": ""},
                "production_system": {"display_value": "false", "value": False},
                "rejection_goto": {"display_value": "", "value": ""},
                "review_date": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "requested_by": {
                    "display_value": "System Administrator",
                    "value": "6816f79cc0a8016401c5a33be04be441",
                },
                "business_duration": {"display_value": "", "value": ""},
                "group_list": {"display_value": "", "value": ""},
                "change_plan": {"display_value": "", "value": ""},
                "approval_set": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "wf_activity": {"display_value": "", "value": ""},
                "implementation_plan": {
                    "display_value": "-- Place router into maintenance mode in the monitoring platform\r\n-- Logon to router through SSH\r\n-- Run the following command\r\n\r\nrouter(config-router)#router bgp 12345\r\nrouter(config-router)#neighbor {neighbor ip} soft-reconfig [inbound]\r\nrouter#clear ip bgp {neighbor ip} soft in\r\n\r\n-- Confirm the sessions have been cleared\r\n-- Place router back into operational mode in the monitoring platform",
                    "value": "-- Place router into maintenance mode in the monitoring platform\r\n-- Logon to router through SSH\r\n-- Run the following command\r\n\r\nrouter(config-router)#router bgp 12345\r\nrouter(config-router)#neighbor {neighbor ip} soft-reconfig [inbound]\r\nrouter#clear ip bgp {neighbor ip} soft in\r\n\r\n-- Confirm the sessions have been cleared\r\n-- Place router back into operational mode in the monitoring platform",
                },
                "universal_request": {"display_value": "", "value": ""},
                "end_date": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "short_description": {
                    "display_value": "Clear BGP sessions on a Cisco router",
                    "value": "Clear BGP sessions on a Cisco router",
                },
                "correlation_display": {"display_value": "", "value": ""},
                "work_start": {
                    "display_value": "2015-07-06 11:56:04",
                    "value": "2015-07-06 18:56:04",
                    "display_value_internal": "2015-07-06 11:56:04",
                },
                "delivery_task": {"display_value": "", "value": ""},
                "outside_maintenance_schedule": {
                    "display_value": "false",
                    "value": False,
                },
                "additional_assignee_list": {"display_value": "", "value": ""},
                "std_change_producer_version": {
                    "display_value": "Clear BGP sessions on a Cisco router - 1",
                    "value": "16c2273c47010200e90d87e8dee49006",
                },
                "sys_class_name": {
                    "display_value": "Change Request",
                    "value": "change_request",
                },
                "service_offering": {"display_value": "", "value": ""},
                "closed_by": {
                    "display_value": "System Administrator",
                    "value": "6816f79cc0a8016401c5a33be04be441",
                },
                "follow_up": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "review_status": {"display_value": "", "value": ""},
                "reassignment_count": {"display_value": "2", "value": 2.0},
                "start_date": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "assigned_to": {"display_value": "", "value": ""},
                "variables": {
                    "display_value": "variable_pool",
                    "value": "variable_pool",
                },
                "sla_due": {
                    "display_value": "UNKNOWN",
                    "value": "",
                    "display_value_internal": "",
                },
                "comments_and_work_notes": {"display_value": "", "value": ""},
                "escalation": {"display_value": "Normal", "value": 0.0},
                "upon_approval": {
                    "display_value": "Proceed to Next Task",
                    "value": "proceed",
                },
                "correlation_id": {"display_value": "", "value": ""},
                "made_sla": {"display_value": "true", "value": True},
                "backout_plan": {
                    "display_value": "Due to the limited number of commands in the implementation plan it is not possible to backout the change.\r\n\r\nIf required you are authorized to reboot the router if BGP fails to work",
                    "value": "Due to the limited number of commands in the implementation plan it is not possible to backout the change.\r\n\r\nIf required you are authorized to reboot the router if BGP fails to work",
                },
                "conflict_status": {"display_value": "Not Run", "value": "Not Run"},
                "task_effective_number": {
                    "display_value": "CHG0000024",
                    "value": "CHG0000024",
                },
                "sys_updated_by": {"display_value": "admin", "value": "admin"},
                "opened_by": {
                    "display_value": "System Administrator",
                    "value": "6816f79cc0a8016401c5a33be04be441",
                },
                "user_input": {"display_value": "", "value": ""},
                "sys_created_on": {
                    "display_value": "2015-07-06 11:55:46",
                    "value": "2015-07-06 18:55:46",
                    "display_value_internal": "2015-07-06 11:55:46",
                },
                "on_hold_task": {"display_value": "", "value": ""},
                "sys_domain": {"display_value": "global", "value": "global"},
                "route_reason": {"display_value": "", "value": ""},
                "closed_at": {
                    "display_value": "2015-07-06 11:56:23",
                    "value": "2015-07-06 18:56:23",
                    "display_value_internal": "2015-07-06 11:56:23",
                },
                "review_comments": {"display_value": "", "value": ""},
                "business_service": {"display_value": "", "value": ""},
                "time_worked": {"display_value": "", "value": ""},
                "chg_model": {"display_value": "", "value": ""},
                "expected_start": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "opened_at": {
                    "display_value": "2015-06-09 11:55:46",
                    "value": "2015-06-09 18:55:46",
                    "display_value_internal": "2015-06-09 11:55:46",
                },
                "work_end": {
                    "display_value": "2015-07-06 11:56:10",
                    "value": "2015-07-06 18:56:10",
                    "display_value_internal": "2015-07-06 11:56:10",
                },
                "phase_state": {"display_value": "Open", "value": "open"},
                "cab_date": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "work_notes": {"display_value": "", "value": ""},
                "close_code": {"display_value": "Successful", "value": "successful"},
                "assignment_group": {
                    "display_value": "Network",
                    "value": "287ebd7da9fe198100f92cc8d1d2154e",
                },
                "description": {
                    "display_value": "Resend the complete BGP table to neighboring routers\r\n\r\n--Both neighbors need to support soft reset route refresh capability.\r\n--Stores complete BGP table of you neighbor in router memory.\r\n--Not a good idea on a peering router with full feed, due to the memory requirements.\r\n",
                    "value": "Resend the complete BGP table to neighboring routers\r\n\r\n--Both neighbors need to support soft reset route refresh capability.\r\n--Stores complete BGP table of you neighbor in router memory.\r\n--Not a good idea on a peering router with full feed, due to the memory requirements.\r\n",
                },
                "on_hold_reason": {"display_value": "", "value": ""},
                "calendar_duration": {"display_value": "", "value": ""},
                "close_notes": {
                    "display_value": "Completed without issues",
                    "value": "Completed without issues",
                },
                "sys_id": {
                    "display_value": "1766f1de47410200e90d87e8dee490f6",
                    "value": "1766f1de47410200e90d87e8dee490f6",
                },
                "contact_type": {"display_value": "Phone", "value": "phone"},
                "cab_required": {"display_value": "false", "value": False},
                "urgency": {"display_value": "3 - Low", "value": 3.0},
                "scope": {"display_value": "Medium", "value": 3.0},
                "company": {"display_value": "", "value": ""},
                "justification": {"display_value": "", "value": ""},
                "activity_due": {
                    "display_value": "UNKNOWN",
                    "value": "",
                    "display_value_internal": "",
                },
                "comments": {"display_value": "", "value": ""},
                "approval": {"display_value": "Approved", "value": "approved"},
                "due_date": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "sys_mod_count": {"display_value": "10", "value": 10.0},
                "on_hold": {"display_value": "false", "value": False},
                "sys_tags": {"display_value": "", "value": ""},
                "conflict_last_run": {
                    "display_value": "",
                    "value": "",
                    "display_value_internal": "",
                },
                "risk_value": {"display_value": "", "value": ""},
                "unauthorized": {"display_value": "false", "value": False},
                "risk": {"display_value": "Moderate", "value": 3.0},
                "location": {"display_value": "", "value": ""},
                "category": {"display_value": "Other", "value": "Other"},
                "risk_impact_analysis": {"display_value": "", "value": ""},
            }
        ]
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result[0].upon_reject.display_value == "Cancel all future Tasks"
    assert response.result[0].base_type == "ChangeRequest"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_state_responses():
    example_data = {
        "result": {
            "available_states": ["0", "4", "-1"],
            "state_transitions": [
                [
                    {
                        "sys_id": "7a0d2ccdc343101035ae3f52c1d3ae2e",
                        "display_value": "Implement to Review",
                        "from_state": "-1",
                        "to_state": "0",
                        "transition_available": False,
                        "automatic_transition": True,
                        "conditions": [
                            {
                                "passed": False,
                                "condition": {
                                    "name": "No active Change Tasks",
                                    "description": None,
                                    "sys_id": "3c1d2ccdc343101035ae3f52c1d3aea4",
                                },
                            }
                        ],
                    },
                    {
                        "sys_id": "db401481c343101035ae3f52c1d3aedd",
                        "display_value": "Implement to Review",
                        "from_state": "-1",
                        "to_state": "0",
                        "transition_available": True,
                        "automatic_transition": False,
                        "conditions": [
                            {
                                "passed": True,
                                "condition": {
                                    "name": "Not On hold",
                                    "description": None,
                                    "sys_id": "2132deb6c303101035ae3f52c1d3ae8c",
                                },
                            }
                        ],
                    },
                ],
                [
                    {
                        "sys_id": "5327c551c343101035ae3f52c1d3aeec",
                        "display_value": "Implement to Canceled",
                        "from_state": "-1",
                        "to_state": "4",
                        "transition_available": True,
                        "automatic_transition": False,
                        "conditions": [],
                    }
                ],
            ],
            "state_label": {"0": "Review", "4": "Canceled", "-1": "Implement"},
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert (
        response.result.state_transitions[0][0].sys_id
        == "7a0d2ccdc343101035ae3f52c1d3ae2e"
    )
    assert response.result.base_type == "State"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_task_responses():
    example_data = {
        "result": [
            {
                "sys_id": {
                    "value": "12629ec4b750230096c3e4f6ee11a9d5",
                    "display_value": "12629ec4b750230096c3e4f6ee11a9d5",
                },
                "parent": {
                    "value": "0f4ac6c4b750230096c3e4f6ee11a9fe",
                    "display_value": "CHG0033046",
                },
                "short_description": {
                    "value": "Retire node",
                    "display_value": "Retire node",
                },
                "active": True,
                "comments": "No additional comments.",
                "approval_history": "Approval history details.",
                "assigned_to": {"value": "user123", "display_value": "John Doe"},
                "sys_created_on": "2024-05-17 10:00:00",
                "description": "Detailed description of the task to retire the node.",
                "escalation": 1,
                "number": "TASK0001",
                "opened_at": "2024-05-16 09:00:00",
                "priority": 3,
                "state": 2,
                "sys_class_name": "Task",
                "time_worked": "00:30:00",
                "watch_list": [
                    {"value": "user234", "display_value": "Jane Smith"},
                    {"value": "user345", "display_value": "Richard Roe"},
                ],
                "work_notes": "Work notes example.",
                "work_notes_list": [
                    {"value": "user456", "display_value": "Alice Johnson"},
                    {"value": "user567", "display_value": "Bob Brown"},
                ],
            }
        ]
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result[0].sys_id.display_value == "12629ec4b750230096c3e4f6ee11a9d5"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_change_request_responses():
    example_data = {
        "result": {
            "reason": {"display_value": "", "value": ""},
            "parent": {"display_value": "", "value": ""},
            "watch_list": {"display_value": "", "value": ""},
            "proposed_change": {"display_value": "", "value": ""},
            "upon_reject": {
                "display_value": "Cancel all future Tasks",
                "value": "cancel",
            },
            "sys_updated_on": {
                "display_value": "2015-07-06 11:59:27",
                "value": "2015-07-06 18:59:27",
                "display_value_internal": "2015-07-06 11:59:27",
            },
            "type": {"display_value": "Standard", "value": "standard"},
            "approval_history": {"display_value": "", "value": ""},
            "skills": {"display_value": "", "value": ""},
            "test_plan": {
                "display_value": "--Confirm that there are no monitoring alerts for the router",
                "value": "--Confirm that there are no monitoring alerts for the router",
            },
            "number": {"display_value": "CHG0000024", "value": "CHG0000024"},
            "is_bulk": {"display_value": "false", "value": False},
            "cab_delegate": {"display_value": "", "value": ""},
            "requested_by_date": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "ci_class": {"display_value": "cmdb_ci", "value": "cmdb_ci"},
            "state": {"display_value": "Closed", "value": 3.0},
            "sys_created_by": {"display_value": "admin", "value": "admin"},
            "knowledge": {"display_value": "false", "value": False},
            "order": {"display_value": "", "value": ""},
            "phase": {"display_value": "Requested", "value": "requested"},
            "cmdb_ci": {"display_value": "", "value": ""},
            "delivery_plan": {"display_value": "", "value": ""},
            "impact": {"display_value": "3 - Low", "value": 3.0},
            "contract": {"display_value": "", "value": ""},
            "active": {"display_value": "false", "value": False},
            "work_notes_list": {"display_value": "", "value": ""},
            "priority": {"display_value": "4 - Low", "value": 4.0},
            "sys_domain_path": {"display_value": "/", "value": "/"},
            "cab_recommendation": {"display_value": "", "value": ""},
            "production_system": {"display_value": "false", "value": False},
            "rejection_goto": {"display_value": "", "value": ""},
            "review_date": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "requested_by": {
                "display_value": "System Administrator",
                "value": "6816f79cc0a8016401c5a33be04be441",
            },
            "business_duration": {"display_value": "", "value": ""},
            "group_list": {"display_value": "", "value": ""},
            "change_plan": {"display_value": "", "value": ""},
            "approval_set": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "wf_activity": {"display_value": "", "value": ""},
            "implementation_plan": {
                "display_value": "-- Place router into maintenance mode in the monitoring platform\r\n-- Logon to router through SSH\r\n-- Run the following command\r\n\r\nrouter(config-router)#router bgp 12345\r\nrouter(config-router)#neighbor {neighbor ip} soft-reconfig [inbound]\r\nrouter#clear ip bgp {neighbor ip} soft in\r\n\r\n-- Confirm the sessions have been cleared\r\n-- Place router back into operational mode in the monitoring platform",
                "value": "-- Place router into maintenance mode in the monitoring platform\r\n-- Logon to router through SSH\r\n-- Run the following command\r\n\r\nrouter(config-router)#router bgp 12345\r\nrouter(config-router)#neighbor {neighbor ip} soft-reconfig [inbound]\r\nrouter#clear ip bgp {neighbor ip} soft in\r\n\r\n-- Confirm the sessions have been cleared\r\n-- Place router back into operational mode in the monitoring platform",
            },
            "universal_request": {"display_value": "", "value": ""},
            "end_date": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "short_description": {
                "display_value": "Clear BGP sessions on a Cisco router",
                "value": "Clear BGP sessions on a Cisco router",
            },
            "correlation_display": {"display_value": "", "value": ""},
            "work_start": {
                "display_value": "2015-07-06 11:56:04",
                "value": "2015-07-06 18:56:04",
                "display_value_internal": "2015-07-06 11:56:04",
            },
            "delivery_task": {"display_value": "", "value": ""},
            "outside_maintenance_schedule": {"display_value": "false", "value": False},
            "additional_assignee_list": {"display_value": "", "value": ""},
            "std_change_producer_version": {
                "display_value": "Clear BGP sessions on a Cisco router - 1",
                "value": "16c2273c47010200e90d87e8dee49006",
            },
            "sys_class_name": {
                "display_value": "Change Request",
                "value": "change_request",
            },
            "service_offering": {"display_value": "", "value": ""},
            "closed_by": {
                "display_value": "System Administrator",
                "value": "6816f79cc0a8016401c5a33be04be441",
            },
            "follow_up": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "review_status": {"display_value": "", "value": ""},
            "reassignment_count": {"display_value": "2", "value": 2.0},
            "start_date": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "assigned_to": {"display_value": "", "value": ""},
            "variables": {"display_value": "variable_pool", "value": "variable_pool"},
            "sla_due": {
                "display_value": "UNKNOWN",
                "value": "",
                "display_value_internal": "",
            },
            "comments_and_work_notes": {"display_value": "", "value": ""},
            "escalation": {"display_value": "Normal", "value": 0.0},
            "upon_approval": {
                "display_value": "Proceed to Next Task",
                "value": "proceed",
            },
            "correlation_id": {"display_value": "", "value": ""},
            "made_sla": {"display_value": "true", "value": True},
            "backout_plan": {
                "display_value": "Due to the limited number of commands in the implementation plan it is not possible to backout the change.\r\n\r\nIf required you are authorized to reboot the router if BGP fails to work",
                "value": "Due to the limited number of commands in the implementation plan it is not possible to backout the change.\r\n\r\nIf required you are authorized to reboot the router if BGP fails to work",
            },
            "conflict_status": {"display_value": "Not Run", "value": "Not Run"},
            "task_effective_number": {
                "display_value": "CHG0000024",
                "value": "CHG0000024",
            },
            "sys_updated_by": {"display_value": "admin", "value": "admin"},
            "opened_by": {
                "display_value": "System Administrator",
                "value": "6816f79cc0a8016401c5a33be04be441",
            },
            "user_input": {"display_value": "", "value": ""},
            "sys_created_on": {
                "display_value": "2015-07-06 11:55:46",
                "value": "2015-07-06 18:55:46",
                "display_value_internal": "2015-07-06 11:55:46",
            },
            "on_hold_task": {"display_value": "", "value": ""},
            "sys_domain": {"display_value": "global", "value": "global"},
            "route_reason": {"display_value": "", "value": ""},
            "closed_at": {
                "display_value": "2015-07-06 11:56:23",
                "value": "2015-07-06 18:56:23",
                "display_value_internal": "2015-07-06 11:56:23",
            },
            "review_comments": {"display_value": "", "value": ""},
            "business_service": {"display_value": "", "value": ""},
            "time_worked": {"display_value": "", "value": ""},
            "chg_model": {"display_value": "", "value": ""},
            "expected_start": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "opened_at": {
                "display_value": "2015-06-09 11:55:46",
                "value": "2015-06-09 18:55:46",
                "display_value_internal": "2015-06-09 11:55:46",
            },
            "work_end": {
                "display_value": "2015-07-06 11:56:10",
                "value": "2015-07-06 18:56:10",
                "display_value_internal": "2015-07-06 11:56:10",
            },
            "phase_state": {"display_value": "Open", "value": "open"},
            "cab_date": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "work_notes": {"display_value": "", "value": ""},
            "close_code": {"display_value": "Successful", "value": "successful"},
            "assignment_group": {
                "display_value": "Network",
                "value": "287ebd7da9fe198100f92cc8d1d2154e",
            },
            "description": {
                "display_value": "Resend the complete BGP table to neighboring routers\r\n\r\n--Both neighbors need to support soft reset route refresh capability.\r\n--Stores complete BGP table of you neighbor in router memory.\r\n--Not a good idea on a peering router with full feed, due to the memory requirements.\r\n",
                "value": "Resend the complete BGP table to neighboring routers\r\n\r\n--Both neighbors need to support soft reset route refresh capability.\r\n--Stores complete BGP table of you neighbor in router memory.\r\n--Not a good idea on a peering router with full feed, due to the memory requirements.\r\n",
            },
            "on_hold_reason": {"display_value": "", "value": ""},
            "calendar_duration": {"display_value": "", "value": ""},
            "close_notes": {
                "display_value": "Completed without issues",
                "value": "Completed without issues",
            },
            "sys_id": {
                "display_value": "1766f1de47410200e90d87e8dee490f6",
                "value": "1766f1de47410200e90d87e8dee490f6",
            },
            "contact_type": {"display_value": "Phone", "value": "phone"},
            "cab_required": {"display_value": "false", "value": False},
            "urgency": {"display_value": "3 - Low", "value": 3.0},
            "scope": {"display_value": "Medium", "value": 3.0},
            "company": {"display_value": "", "value": ""},
            "justification": {"display_value": "", "value": ""},
            "activity_due": {
                "display_value": "UNKNOWN",
                "value": "",
                "display_value_internal": "",
            },
            "comments": {"display_value": "", "value": ""},
            "approval": {"display_value": "Approved", "value": "approved"},
            "due_date": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "sys_mod_count": {"display_value": "10", "value": 10.0},
            "on_hold": {"display_value": "false", "value": False},
            "sys_tags": {"display_value": "", "value": ""},
            "conflict_last_run": {
                "display_value": "",
                "value": "",
                "display_value_internal": "",
            },
            "risk_value": {"display_value": "", "value": ""},
            "unauthorized": {"display_value": "false", "value": False},
            "risk": {"display_value": "Moderate", "value": 3.0},
            "location": {"display_value": "", "value": ""},
            "category": {"display_value": "Other", "value": "Other"},
            "risk_impact_analysis": {"display_value": "", "value": ""},
        }
    }

    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.sys_updated_on.display_value == "2015-07-06 11:59:27"
    assert response.result.base_type == "ChangeRequest"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_table_responses():
    example_data = {
        "result": {
            "upon_approval": "",
            "location": {
                "link": "https://instance.servicenow.com/api/now/table/cmn_location/105cf7f3c611227501e75e08b14a38ba",
                "value": "105cf7f3c611227501e75e08b14a38ba",
            },
            "expected_start": "",
            "reopen_count": "",
            "close_notes": "",
            "additional_assignee_list": "",
            "impact": "1",
            "urgency": "3",
            "correlation_id": "",
            "sys_tags": "",
            "sys_domain": {
                "link": "https://instance.servicenow.com/api/now/table/sys_user_group/global",
                "value": "global",
            },
            "description": "",
            "group_list": "",
            "priority": "3",
            "delivery_plan": "",
            "sys_mod_count": "4",
            "work_notes_list": "",
            "business_service": "",
            "follow_up": "",
            "closed_at": "",
            "sla_due": "2015-11-11 22:04:15",
            "delivery_task": "",
            "sys_updated_on": "2015-11-01 22:37:27",
            "parent": "",
            "work_end": "",
            "number": "INC0000046",
            "closed_by": "",
            "work_start": "",
            "calendar_stc": "",
            "category": "software",
            "business_duration": "",
            "incident_state": "1",
            "activity_due": "",
            "correlation_display": "",
            "company": "",
            "active": "true",
            "due_date": "",
            "assignment_group": {
                "link": "https://instance.servicenow.com/api/now/table/sys_user_group/8a4dde73c6112278017a6a4baf547aa7",
                "value": "8a4dde73c6112278017a6a4baf547aa7",
            },
            "caller_id": {
                "link": "https://instance.servicenow.com/api/now/table/sys_user/46c6f9efa9fe198101ddf5eed9adf6e7",
                "value": "46c6f9efa9fe198101ddf5eed9adf6e7",
            },
            "knowledge": "false",
            "made_sla": "false",
            "comments_and_work_notes": "",
            "parent_incident": "",
            "state": "1",
            "user_input": "",
            "sys_created_on": "2015-11-01 22:05:30",
            "approval_set": "",
            "reassignment_count": "1",
            "rfc": "",
            "child_incidents": "",
            "opened_at": "2015-11-02 22:04:15",
            "short_description": "Can't access SFA software",
            "order": "",
            "sys_updated_by": "glide.maint",
            "resolved_by": "",
            "notify": "1",
            "upon_reject": "",
            "approval_history": "",
            "problem_id": {
                "link": "https://instance.servicenow.com/api/now/table/problem/a9e4890bc6112276003d7a5a5c774a74",
                "value": "a9e4890bc6112276003d7a5a5c774a74",
            },
            "work_notes": "",
            "calendar_duration": "",
            "close_code": "",
            "sys_id": "a9e30c7dc61122760116894de7bcc7bd",
            "approval": "not requested",
            "caused_by": "",
            "severity": "3",
            "sys_created_by": "admin",
            "resolved_at": "",
            "assigned_to": "",
            "business_stc": "",
            "wf_activity": "",
            "sys_domain_path": "/",
            "cmdb_ci": {
                "link": "https://instance.servicenow.com/api/now/table/cmdb_ci/a9c0c8d2c6112276018f7705562f9cb0",
                "value": "a9c0c8d2c6112276018f7705562f9cb0",
            },
            "opened_by": {
                "link": "https://instance.servicenow.com/api/now/table/sys_user/46c6f9efa9fe198101ddf5eed9adf6e7",
                "value": "46c6f9efa9fe198101ddf5eed9adf6e7",
            },
            "subcategory": "",
            "rejection_goto": "",
            "sys_class_name": "incident",
            "watch_list": "",
            "time_worked": "",
            "contact_type": "phone",
            "escalation": "0",
            "comments": "",
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.sys_class_name == "incident"
    assert response.result.cmdb_ci["value"] == "a9c0c8d2c6112276018f7705562f9cb0"
    assert response.result.base_type == "Table"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_service_responses():
    example_data = {
        "service": {
            "name": "PeopleSoft Portals",
            "url": "/api/now/table/cmdb_ci_service_discovered/2fce42d80a0a0bb4004af34d7e3984c8",
            "service_relations": [
                {"parent": "", "child": "3a2810c20a0a0bb400268337d6e942ca"},
                {
                    "parent": "3a27f1520a0a0bb400ecd6ff7afcf036",
                    "child": "3a5dd3dbc0a8ce0100655f1ec66ed42c",
                },
                {
                    "parent": "3a290cc60a0a0bb400000bdb386af1cf",
                    "child": "3a307c930a0a0bb400353965d0b8861f",
                },
                {
                    "parent": "3a172e820a0a0bb40034228e9f65f1be",
                    "child": "3a27d4370a0a0bb4006316812bf45439",
                },
                {"parent": "", "child": "3a172e820a0a0bb40034228e9f65f1be"},
                {"parent": "", "child": "3a27f1520a0a0bb400ecd6ff7afcf036"},
                {
                    "parent": "3a2810c20a0a0bb400268337d6e942ca",
                    "child": "3a290cc60a0a0bb400000bdb386af1cf",
                },
            ],
        },
        "cmdb": {
            "relations": [],
            "items": [
                {
                    "values": {
                        "sys_id": "3a172e820a0a0bb40034228e9f65f1be",
                        "name": "PS LoadBal01",
                    },
                    "className": "cmdb_ci_win_server",
                },
                {
                    "values": {
                        "sys_id": "3a2810c20a0a0bb400268337d6e942ca",
                        "name": "PS Apache03",
                    },
                    "className": "cmdb_ci_web_server",
                },
                {
                    "values": {
                        "sys_id": "55b35562c0a8010e01cff22378e0aea9",
                        "name": "ny8500-nbxs08",
                    },
                    "className": "cmdb_ci_netgear",
                },
                {
                    "values": {
                        "sys_id": "3a27f1520a0a0bb400ecd6ff7afcf036",
                        "name": "PS Apache02",
                    },
                    "className": "cmdb_ci_web_server",
                },
                {
                    "values": {
                        "sys_id": "3a307c930a0a0bb400353965d0b8861f",
                        "name": "PS ORA01",
                    },
                    "className": "cmdb_ci_database",
                },
            ],
        },
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.service.name == "PeopleSoft Portals"
    assert response.cmdb.items[1].values.sys_id == "3a2810c20a0a0bb400268337d6e942ca"
    assert response.service.base_type == "Service"
    assert response.cmdb.base_type == "CMDBService"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_cmdb_responses():
    example_data = {
        "result": {
            "icon_url": "images/app.ngbsm/computer.svg",
            "is_extendable": True,
            "parent": "cmdb_ci_hardware",
            "children": [
                "cmdb_ci_ucs_blade",
                "cmdb_ci_pc_hardware",
                "cmdb_ci_ucs_rack_unit",
                "cmdb_ci_mainframe_hardware",
                "cmdb_ci_server",
                "cmdb_ci_storage_switch",
            ],
            "name": "cmdb_ci_computer",
            "icon": "c6442dd69fb00200eb3919eb552e7012",
            "attributes": [
                {
                    "is_inherited": "false",
                    "is_mandatory": "false",
                    "is_read_only": "false",
                    "default_value": None,
                    "label": "OS Address Width (bits)",
                    "type": "integer",
                    "element": "os_address_width",
                    "max_length": "40",
                    "is_display": "false",
                },
                {
                    "is_inherited": "true",
                    "is_mandatory": "false",
                    "is_read_only": "true",
                    "default_value": "false",
                    "label": "Skip sync",
                    "type": "boolean",
                    "element": "skip_sync",
                    "max_length": "40",
                    "is_display": "false",
                },
                {
                    "is_inherited": "true",
                    "is_mandatory": "false",
                    "is_read_only": "false",
                    "default_value": None,
                    "label": "DNS Domain",
                    "type": "string",
                    "element": "dns_domain",
                    "max_length": "255",
                    "is_display": "false",
                },
                {
                    "is_inherited": "true",
                    "is_mandatory": "false",
                    "is_read_only": "false",
                    "default_value": None,
                    "label": "Purchased",
                    "type": "glide_date",
                    "element": "purchase_date",
                    "max_length": "40",
                    "is_display": "false",
                },
                {
                    "is_inherited": "true",
                    "is_mandatory": "false",
                    "is_read_only": "false",
                    "default_value": None,
                    "label": "Lease contract",
                    "type": "string",
                    "element": "lease_id",
                    "max_length": "40",
                    "is_display": "false",
                },
            ],
            "relationship_rules": [
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "cb5592603751200032ff8c00dfbe5d17",
                    "child": "dscy_route_next_hop",
                },
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "cb5592603751200032ff8c00dfbe5d17",
                    "child": "dscy_router_interface",
                },
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "cb5592603751200032ff8c00dfbe5d17",
                    "child": "dscy_route_interface",
                },
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "55c95bf6c0a8010e0118ec7056ebc54d",
                    "child": "cmdb_ci_storage_pool",
                },
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "55c95bf6c0a8010e0118ec7056ebc54d",
                    "child": "cmdb_ci_disk_partition",
                },
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "55c95bf6c0a8010e0118ec7056ebc54d",
                    "child": "cmdb_ci_storage_volume",
                },
                {
                    "parent": "cmdb_ci_computer",
                    "relation_type": "55c95bf6c0a8010e0118ec7056ebc54d",
                    "child": "cmdb_ci_storage_device",
                },
            ],
            "label": "Computer",
            "identification_rules": {
                "related_rules": [
                    {
                        "condition": "",
                        "exact_count_match": False,
                        "referenced_field": "installed_on",
                        "active": True,
                        "attributes": "name",
                        "allow_fallback": False,
                        "table": "cmdb_print_queue_instance",
                        "order": 100,
                        "allow_null_attribute": False,
                    }
                ],
                "applies_to": "cmdb_ci_hardware",
                "identifiers": [
                    {
                        "condition": "valid=true^absent=false^EQ",
                        "exact_count_match": True,
                        "referenced_field": "cmdb_ci",
                        "active": True,
                        "attributes": "serial_number,serial_number_type",
                        "allow_fallback": False,
                        "table": "cmdb_serial_number",
                        "order": 100,
                        "allow_null_attribute": False,
                    },
                    {
                        "condition": None,
                        "exact_count_match": False,
                        "referenced_field": None,
                        "active": True,
                        "attributes": "serial_number",
                        "allow_fallback": False,
                        "table": None,
                        "order": 200,
                        "allow_null_attribute": False,
                    },
                    {
                        "condition": None,
                        "exact_count_match": False,
                        "referenced_field": None,
                        "active": True,
                        "attributes": "name",
                        "allow_fallback": False,
                        "table": None,
                        "order": 300,
                        "allow_null_attribute": False,
                    },
                    {
                        "condition": "install_status!=100^EQ",
                        "exact_count_match": True,
                        "referenced_field": "cmdb_ci",
                        "active": True,
                        "attributes": "ip_address,mac_address",
                        "allow_fallback": False,
                        "table": "cmdb_ci_network_adapter",
                        "order": 400,
                        "allow_null_attribute": False,
                    },
                ],
                "name": "Hardware Rule",
                "description": "Identifier for hardware.",
                "active": True,
                "is_independent": True,
            },
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.children[0] == "cmdb_ci_ucs_blade"
    assert response.result.base_type == "CMDB"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_import_set_responses():
    example_data = {
        "import_set": "ISET0010001",
        "staging_table": "imp_user",
        "result": [
            {
                "transform_map": "User",
                "table": "sys_user",
                "display_name": "name",
                "display_value": "John Public",
                "record_link": "https://instance.service-now.com/api/now/table/sys_user/ea928be64f411200adf9f8e18110c777",
                "status": "inserted",
                "sys_id": "ea928be64f411200adf9f8e18110c777",
            }
        ],
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.import_set == "ISET0010001"
    assert response.staging_table == "imp_user"
    assert response.result[0].table == "sys_user"
    assert response.result[0].base_type == "ImportSetResult"


@pytest.mark.skipif(
    sys.platform in ["darwin"] or skip,
    reason=reason,
)
def test_servicenow_kb_article_responses():
    example_data = {
        "result": {
            "meta": {
                "start": 0,
                "end": 2,
                "fields": "short_description,sys_class_name",
                "query": "Windows",
                "filter": "",
                "kb": "",
                "language": "en",
                "count": 19,
                "ts_query_id": "7976f36129c30410f877796e70786991",
                "status": {"code": 200},
            },
            "articles": [
                {
                    "link": "?sys_kb_id=9e528db1474321009db4b5b08b9a71a6&id=kb_article_view&sysparm_rank=1&sysparm_tsqueryId=7976f36129c30410f877796e70786991",
                    "rank": 1,
                    "id": "kb_knowledge:9e528db1474321009db4b5b08b9a71a6",
                    "title": "Windows: Should I upgrade to Windows 8.x?",
                    "snippet": "    Should I upgrade to <B>Windows</B> 8.x? <B>Windows</B> 8.x is designed for using touch, mouse, and keyboard the <B>Windows</B> Store and access apps such as Calendar, Mail, and Messaging. By most accounts, <B>Windows</B> boot times, smaller memory footprint, and more free memory for the programs you run. <B>Windows</B>",
                    "score": 14.869,
                    "number": "KB0000020",
                    "fields": {
                        "short_description": {
                            "display_value": "Windows: Should I upgrade to Windows 8.x?\n\t\t",
                            "name": "short_description",
                            "label": "Short description",
                            "type": "string",
                            "value": "Windows: Should I upgrade to Windows 8.x?\n\t\t",
                        },
                        "sys_class_name": {
                            "display_value": "Knowledge",
                            "name": "sys_class_name",
                            "label": "Class",
                            "type": "sys_class_name",
                            "value": "kb_knowledge",
                        },
                    },
                },
                {
                    "link": "?sys_kb_id=3b07857187032100deddb882a2e3ec20&id=kb_article_view&sysparm_rank=2&sysparm_tsqueryId=7976f36129c30410f877796e70786991",
                    "rank": 2,
                    "id": "kb_knowledge:3b07857187032100deddb882a2e3ec20",
                    "title": "What is the Windows key?",
                    "snippet": "What is the <B>Windows</B> key? The <B>Windows</B> key is a standard key on most keyboards on computers built to use a <B>Windows</B> operating system. It is labeled with a <B>Windows</B> logo, and is usually placed between on the right side as well. Pressing Win (the <B>Windows</B> key) on its own will do the following: <B>Windows</B> 8.x: Toggle",
                    "score": 13.4826,
                    "number": "KB0000017",
                    "fields": {
                        "short_description": {
                            "display_value": "What is the Windows key?\t\t",
                            "name": "short_description",
                            "label": "Short description",
                            "type": "string",
                            "value": "What is the Windows key?\t\t",
                        },
                        "sys_class_name": {
                            "display_value": "Knowledge",
                            "name": "sys_class_name",
                            "label": "Class",
                            "type": "sys_class_name",
                            "value": "kb_knowledge",
                        },
                    },
                },
            ],
        }
    }

    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.base_type == "KnowledgeManagement"
    example_data = {
        "result": {
            "meta": {
                "start": 0,
                "end": 3,
                "fields": "short_description",
                "query": "homepage",
                "filter": "",
                "kb": "",
                "language": "en",
                "status": {"code": 200},
                "count": 2,
            },
            "articles": [
                {
                    "link": "?id=kb_article_view&sys_kb_id=f27d7f79c0a8011b0018f9d700d2b9aa",
                    "id": "kb_knowledge:f27d7f79c0a8011b0018f9d700d2b9aa",
                    "title": "Email Interruption Tonight at 11:00 PM Eastern",
                    "snippet": " If the site is UP but you can't access the page, try one of the below solutions: Browser Related Problems Force a full refresh for the site. This can be achieved by pressing CTRL + F5 keys at the same time on your favourite browser (Firefox, Chrome, Explorer, etc.) Try alternative urls such as m.outlook.com Clear the temporary cache and cookies ",
                    "score": -1,
                    "number": "KB0000002",
                    "fields": {
                        "short_description": {
                            "display_value": "Email Interruption Tonight at 11:00 PM Eastern\n\t\t",
                            "name": "short_description",
                            "label": "Short description",
                            "type": "string",
                            "value": "Email Interruption Tonight at 11:00 PM Eastern\n\t\t",
                        }
                    },
                },
                {
                    "link": "?id=kb_article_view&sys_kb_id=f2765f9fc0a8011b0120ec1b352bf09b",
                    "id": "kb_knowledge:f2765f9fc0a8011b0120ec1b352bf09b",
                    "title": "Sales Force Automation is DOWN",
                    "snippet": "  On Friday, January 20th, we experienced a widespread outage that affected all Zoho services. The outage started around 8:13 am Pacific Time. Zoho services started coming back online for customer use at 3:49 pm, and all services were fully restored at 6:22 pm PST. We absolutely realize how important our services are for businesses and users who",
                    "score": -1,
                    "number": "KB0000001",
                    "fields": {
                        "short_description": {
                            "display_value": "Sales Force Automation is DOWN",
                            "name": "short_description",
                            "label": "Short description",
                            "type": "string",
                            "value": "Sales Force Automation is DOWN",
                        }
                    },
                },
            ],
        }
    }

    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.base_type == "KnowledgeManagement"
    example_data = {
        "result": {
            "content": '<p><span style="font-size: 18pt;"><strong>How to Deal with Spam</strong></span></p>\r\n<p>Spam has increasingly become a problem on the Internet. While every Internet user receives some spam, email  addresses posted to web sites or in newsgroups and chat rooms attract the most spam.</p>\r\n<p>To reduce the amount of spam you receive:</p>\r\n<p>',
            "template": False,
            "number": "KB0000011",
            "sys_id": "0b48fd75474321009db4b5b08b9a71c2",
            "short_description": "How to Deal with Spam",
            "display_attachments": True,
            "attachments": [
                {
                    "sys_id": "dc27ae18294f4010f877796e707869c8",
                    "file_name": "image.jpg",
                    "size_bytes": "66792",
                    "state": "available_conditionally",
                },
                {
                    "sys_id": "fedf5614294f4010f877796e70786956",
                    "file_name": "attachment.txt",
                    "size_bytes": "75",
                    "state": "available_conditionally",
                },
            ],
            "embedded_content": [],
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.base_type == "Article"

    example_data = {
        "result": {
            "meta": {
                "start": 0,
                "end": 5,
                "fields": "",
                "query": "",
                "filter": "workflow_state=published^valid_to>=javascript:gs.beginningOfToday()^active=true^sys_class_name!=kb_knowledge_block^sys_view_count>0^ORDERBYDESCsys_view_count^ORDERBYshort_description",
                "kb": "",
                "count": 2,
                "status": {"code": 200},
                "language": "en",
            },
            "articles": [
                {
                    "link": "?id=kb_article_view&sys_kb_id=0b48fd75474321009db4b5b08b9a71c2",
                    "id": "kb_knowledge:0b48fd75474321009db4b5b08b9a71c2",
                    "title": "How to Deal with Spam",
                    "snippet": "How to Deal with Spam Spam has increasingly become a problem on the Internet. While every Internet user receives some spam, email addresses posted to web sites or in newsgroups and chat rooms attract the most spam. To reduce the amount of spam you receive: Don't reply to spam Be careful releasing your email address, and know how it will be used ",
                    "score": 7,
                    "tags": [],
                    "number": "KB0000011",
                },
                {
                    "link": "?id=kb_article_view&sys_kb_id=c85cd2519f77230088aebde8132e70c2",
                    "id": "kb_knowledge:c85cd2519f77230088aebde8132e70c2",
                    "title": "Microsoft Outlook Issues",
                    "snippet": "Microsoft Outlook Issues This article explains how to use automatic replies in Outlook 2010 for Exchange accounts. Setting Up Automatic Replies Click the File tab. Click Automatic Replies. Select Send automatic replies. If desired, select the Only send during this time range check box to schedule when your out of office replies are active. If yo",
                    "score": 6,
                    "tags": [],
                    "number": "KB99999999",
                },
            ],
        }
    }
    response = Response(**example_data, status_code=200, json=example_data)
    assert response.result.base_type == "KnowledgeManagement"


if __name__ == "__main__":
    test_servicenow_article()
    test_servicenow_change()
    test_servicenow_incident()
    test_servicenow_cicd()
    test_servicenow_application()
    test_servicenow_table()
    test_servicenow_import_set()
    test_servicenow_cmdb()
    test_servicenow_cicd_responses()
    test_servicenow_batch_install_responses()
    test_servicenow_oauth_responses()
    test_servicenow_install_responses()
    test_servicenow_state_responses()
    test_servicenow_change_requests_responses()
    test_servicenow_change_request_responses()
    test_servicenow_cmdb_responses()
    test_servicenow_table_responses()
    test_servicenow_service_responses()
    test_servicenow_import_set_responses()
    test_servicenow_kb_article_responses()
