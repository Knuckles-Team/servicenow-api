from typing import Union, List, Dict, Optional
from pydantic import BaseModel, field_validator
import re

try:
    from servicenow_api.decorators import require_auth
except ModuleNotFoundError:
    from decorators import require_auth
try:
    from servicenow_api.exceptions import (AuthError, UnauthorizedError, ParameterError, MissingParameterError)
except ModuleNotFoundError:
    from exceptions import (AuthError, UnauthorizedError, ParameterError, MissingParameterError)


class ApplicationServiceModel(BaseModel):
    application_id: str = None

    @field_validator('dry_run', 'stats', 'force')
    def validate_bool_fields(cls, v):
        if v is not None and not isinstance(v, bool):
            raise ValueError("Invalid states")
        return v

    @field_validator('project_id', 'commit_hash', 'branch', 'start_branch', 'start_sha', 'start_project',
                     'pipeline_id', 'line')
    def validate_optional_parameters(cls, v, values):
        if 'project_id' in values and values['project_id'] is not None and v is not None:
            return v
        else:
            raise ValueError("Invalid optional params")

    @field_validator('commit_hash', 'branch', 'reference', 'name', 'context', 'note', 'path', 'line_type')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('coverage')
    def validate_coverage(cls, v):
        if v is not None and not isinstance(v, (float, int)):
            raise ValueError("Invalid states")
        return v

    @field_validator('state')
    def validate_state(cls, v):
        if v is not None and v not in ['pending', 'running', 'success', 'failed', 'canceled']:
            raise ValueError("Invalid states")
        return v

    @field_validator('line_type')
    def validate_line_type(cls, v):
        if v is not None and v not in ['new', 'old']:
            raise ValueError("Invalid line_type")
        return v

    @field_validator('report_type')
    def validate_report_type(cls, v):
        if v is not None and v not in ['license_scanning', 'code_coverage']:
            raise ValueError("Invalid report_type")
        return v

    @field_validator('rule_type')
    def validate_rule_type(cls, v):
        if v is not None and v not in ['any_approver', 'regular']:
            raise ValueError("Invalid rule_type")
        return v

    @field_validator('user_ids', 'group_ids', 'protected_branch_ids')
    def validate_list_parameters(cls, v):
        if v is not None and not isinstance(v, list):
            raise ValueError("Invalid user_ids, group_ids, protected_branch_ids")
        return v

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "branch": values.get("branch"),
            "commit_message": values.get("commit_message"),
            "start_branch": values.get("start_branch"),
            "start_sha": values.get("start_sha"),
            "start_project": values.get("start_project"),
            "actions": values.get("actions"),
            "author_email": values.get("author_email"),
            "author_name": values.get("author_name"),
            "stats": values.get("stats"),
            "force": values.get("force"),
            "note": values.get("note"),
            "path": values.get("path"),
            "line": values.get("line"),
            "line_type": values.get("line_type"),
            "state": values.get("state"),
            "ref": values.get("ref"),
            "name": values.get("name"),
            "context": values.get("context"),
            "target_url": values.get("target_url"),
            "description": values.get("description"),
            "coverage": values.get("coverage"),
            "pipeline_id": values.get("pipeline_id"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data


class CMDBModel(BaseModel):
    cmdb_id: str = None

    @field_validator('expires_at')
    def validate_expires_at(cls, v):
        if v is not None and not isinstance(v, str):
            raise ParameterError
        return v

    @field_validator('project_id', 'group_id', 'token')
    def validate_optional_parameters(cls, v, values):
        if ('project_id' in values or 'group_id' in values) and v is not None:
            return v
        else:
            raise MissingParameterError

    @field_validator('name', 'username', 'scopes')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ParameterError
        return v

    @field_validator('scopes')
    def validate_scopes(cls, v):
        valid_scopes = ['read_repository', 'read_registry', 'write_registry', 'read_package_registry',
                        'write_package_registry']
        if v is not None and v not in valid_scopes:
            raise ParameterError
        return v


class CICDModel(BaseModel):
    result_id: Optional[str] = None
    progress_id: Optional[str] = None
    rollback_id: Optional[str] = None
    name: Optional[str] = None
    notes: Optional[str] = None
    packages: Optional[str] = None
    app_sys_id: Optional[str] = None
    scope: Optional[str] = None
    auto_upgrade_base_app: Optional[bool] = None
    base_app_version: Optional[str] = None
    version: Optional[str] = None
    dev_notes: Optional[str] = None
    combo_sys_id: Optional[str] = None
    suite_sys_id: Optional[str] = None
    sys_ids: Optional[List[str]] = None
    scan_type: Optional[str] = None
    plugin_id: Optional[str] = None
    branch_name: Optional[str] = None
    credential_sys_id: Optional[str] = None
    mid_server_sys_id: Optional[str] = None
    repo_url: Optional[str] = None
    test_suite_sys_id: Optional[str] = None
    test_suite_name: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    api_parameters: str = None

    @field_validator('per_page', 'page')
    def validate_positive_integer(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ParameterError
        return v

    @field_validator('argument')
    def validate_argument(cls, v):
        if not isinstance(v, str):
            raise ParameterError
        return v

    @field_validator('group_id')
    def validate_group_id(cls, v):
        if v is None:
            raise MissingParameterError
        return v

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("page") is not None:
            filters.append(f'page={values["page"]}')

        if values.get("per_page") is not None:
            filters.append(f'per_page={values["per_page"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


class ChangeManagementModel(BaseModel):
    change_request_sys_id: Optional[str]
    state: Optional[str]
    cmdb_ci_sys_ids: Optional[List[str]]
    association_type: Optional[str]
    refresh_impacted_services: Optional[bool]
    name_value_pairs: Optional[Dict[str, Union[str, int, bool]]]
    order: Optional[str]
    max_pages: Optional[int]
    per_page: Optional[int]
    sysparm_query: Optional[str]
    text_search: Optional[str]
    model_sys_id: Optional[str]
    template_sys_id: Optional[str]
    worker_sys_id: Optional[str]
    change_type: Optional[str]
    standard_change_template_id: Optional[str]

    @field_validator('per_page', 'page')
    def validate_positive_integer(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ParameterError
        return v

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("page") is not None:
            filters.append(f'page={values["page"]}')

        if values.get("per_page") is not None:
            filters.append(f'per_page={values["per_page"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


class IncidentModel(BaseModel):
    incident_id: Union[int, str] = None
    data: Dict = None

    @field_validator('per_page', 'page')
    def validate_positive_integer(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ParameterError
        return v

    @field_validator('include_retried')
    def validate_include_retried(cls, v):
        if v is not None and not isinstance(v, bool):
            raise ParameterError
        return v

    @field_validator('scope')
    def validate_scope(cls, v):
        if v not in ['created', 'pending', 'running', 'failed', 'success', 'canceled', 'skipped',
                     'waiting_for_resource', 'manual']:
            raise ParameterError
        return v

    @field_validator('job_variable_attributes')
    def validate_job_variable_attributes(cls, v):
        if v is not None and (not isinstance(v, dict) or "job_variable_attributes" not in v.keys()):
            raise ParameterError
        return v

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("page") is not None:
            filters.append(f'page={values["page"]}')

        if values.get("per_page") is not None:
            filters.append(f'per_page={values["per_page"]}')

        if values.get("scope") is not None:
            filters.append(f'scope[]={values["scope"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


class ImportSetModel(BaseModel):
    table: str
    import_set_sys_id: Optional[str]
    data: Dict = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("approved_by_ids") is not None:
            filters.append(f'approved_by_ids={values["approved_by_ids"]}')

        if values.get("approver_ids") is not None:
            filters.append(f'approver_ids={values["approver_ids"]}')

        if values.get("assignee_id") is not None:
            filters.append(f'assignee_id={values["assignee_id"]}')

        if values.get("author_id") is not None:
            filters.append(f'author_id={values["author_id"]}')

        if values.get("author_username") is not None:
            filters.append(f'author_username={values["author_username"]}')

        if values.get("created_after") is not None:
            filters.append(f'created_after={values["created_after"]}')

        if values.get("deployed_after") is not None:
            filters.append(f'deployed_after={values["deployed_after"]}')

        if values.get("deployed_before") is not None:
            filters.append(f'deployed_before={values["deployed_before"]}')

        if values.get("environment") is not None:
            filters.append(f'environment={values["environment"]}')

        if values.get("search_in") is not None:
            filters.append(f'search_in={values["search_in"]}')

        if values.get("labels") is not None:
            filters.append(f'labels={values["labels"]}')

        if values.get("milestone") is not None:
            filters.append(f'milestone={values["milestone"]}')

        if values.get("my_reaction_emoji") is not None:
            filters.append(f'my_reaction_emoji={values["my_reaction_emoji"]}')

        if values.get("search_exclude") is not None:
            filters.append(f'search_exclude={values["search_exclude"]}')

        if values.get("order_by") is not None:
            filters.append(f'order_by={values["order_by"]}')

        if values.get("reviewer_id") is not None:
            filters.append(f'reviewer_id={values["reviewer_id"]}')

        if values.get("reviewer_username") is not None:
            filters.append(f'reviewer_username={values["reviewer_username"]}')

        if values.get("scope") is not None:
            filters.append(f'scope={values["scope"]}')

        if values.get("search") is not None:
            filters.append(f'search={values["search"]}')

        if values.get("sort") is not None:
            filters.append(f'sort={values["sort"]}')

        if values.get("source_branch") is not None:
            filters.append(f'source_branch={values["source_branch"]}')

        if values.get("state") is not None:
            filters.append(f'state={values["state"]}')

        if values.get("target_branch") is not None:
            filters.append(f'target_branch={values["target_branch"]}')

        if values.get("updated_after") is not None:
            filters.append(f'updated_after={values["updated_after"]}')

        if values.get("updated_before") is not None:
            filters.append(f'updated_before={values["updated_before"]}')

        if values.get("view") is not None:
            filters.append(f'view={values["view"]}')

        if values.get("with_labels_details") is not None:
            filters.append(f'with_labels_details={values["with_labels_details"]}')

        if values.get("with_merge_status_recheck") is not None:
            filters.append(f'with_merge_status_recheck={values["with_merge_status_recheck"]}')

        if values.get("wip") is not None:
            filters.append(f'wip={values["wip"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator("scope")
    def validate_scope(cls, value):
        valid_scopes = ['created_by_me', 'assigned_to_me', 'all']
        if value and not all(scope in valid_scopes for scope in value):
            raise ValueError("Invalid scope values")
        return value

    @field_validator("search_in")
    def validate_search_in(cls, value):
        valid_search_in = ['title', 'description', 'title,description']
        if value and value not in valid_search_in:
            raise ValueError("Invalid search_in value")
        return value

    @field_validator("search_exclude")
    def validate_search_exclude(cls, value):
        valid_search_exclude = ['labels', 'milestone', 'author_id', 'assignee_id', 'author_username',
                                'reviewer_id', 'reviewer_username', 'my_reaction_emoji']
        if value and value not in valid_search_exclude:
            raise ValueError("Invalid search_exclude value")
        return value

    @field_validator("state")
    def validate_state(cls, value):
        valid_states = ['opened', 'closed', 'locked', 'merged']
        if value and value not in valid_states:
            raise ValueError("Invalid state value")
        return value

    @field_validator("sort")
    def validate_sort(cls, value):
        valid_sorts = ['asc', 'desc']
        if value and value not in valid_sorts:
            raise ValueError("Invalid sort value")
        return value

    @field_validator("wip")
    def validate_wip(cls, value):
        valid_wip_values = ['yes', 'no']
        if value and value not in valid_wip_values:
            raise ValueError("Invalid wip value")
        return value

    @field_validator('project_id', 'source_branch', 'target_branch', 'title')
    def validate_string(cls, v):
        if not isinstance(v, str):
            raise ParameterError
        return v

    @field_validator('allow_collaboration', 'allow_maintainer_to_push', 'squash')
    def validate_boolean(cls, v):
        if not isinstance(v, bool):
            raise ParameterError
        return v

    @field_validator('approvals_before_merge', 'assignee_id', 'milestone_id', 'target_project_id')
    def validate_positive_integer(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ParameterError
        return v

    @field_validator('assignee_ids', 'reviewer_ids')
    def validate_list_of_integers(cls, v):
        if not isinstance(v, list) or not all(isinstance(i, int) for i in v):
            raise ParameterError
        return v

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "source_branch": values.get("source_branch"),
            "target_branch": values.get("target_branch"),
            "title": values.get("title"),
            "allow_collaboration": values.get("allow_collaboration"),
            "allow_maintainer_to_push": values.get("allow_maintainer_to_push"),
            "approvals_before_merge": values.get("approvals_before_merge"),
            "assignee_id": values.get("assignee_id"),
            "description": values.get("description"),
            "labels": values.get("labels"),
            "milestone_id": values.get("milestone_id"),
            "remove_source_branch": values.get("remove_source_branch"),
            "reviewer_ids": values.get("reviewer_ids"),
            "squash": values.get("squash"),
            "target_project_id": values.get("target_project_id"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data


class TableModel(BaseModel):
    table: str
    table_record_sys_id: Optional[str]
    name_value_pairs: Optional[Dict[str, Union[str, int, bool]]]
    sysparm_display_value: Optional[str]
    sysparm_exclude_reference_link: Optional[bool]
    sysparm_fields: Optional[str]
    sysparm_limit: Optional[int]
    sysparm_no_count: Optional[bool]
    sysparm_offset: Optional[int]
    sysparm_query: Optional[str]
    sysparm_query_category: Optional[str]
    sysparm_query_no_domain: Optional[bool]
    sysparm_suppress_pagination_header: Optional[bool]
    sysparm_view: Optional[str]
    data: Dict = None

    @field_validator("table")
    def check_required_fields(cls, value):
        if value is None:
            raise ValueError("This field is required.")
        return value

    @field_validator("report_type")
    def validate_report_type(cls, value):
        if value not in ['license_scanning', 'code_coverage']:
            raise ValueError("Invalid report_type")
        return value

    @field_validator("rule_type")
    def validate_rule_type(cls, value):
        if value not in ['any_approver', 'regular']:
            raise ValueError("Invalid rule_type")
        return value

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "approvals_required": values.get("approvals_required"),
            "name": values.get("name"),
            "applies_to_all_protected_branches": values.get("applies_to_all_protected_branches"),
            "group_ids": values.get("group_ids"),
            "protected_branch_ids": values.get("protected_branch_ids"),
            "report_type": values.get("report_type"),
            "rule_type": values.get("rule_type"),
            "user_ids": values.get("user_ids"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data
