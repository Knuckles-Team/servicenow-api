from typing import Union, List, Dict
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


class BranchModel(BaseModel):
    project_id: Union[int, str]
    branch: str = None
    reference: str = None

    @field_validator('branch', 'reference')
    def validate_required_parameters(cls, v, values):
        if 'project_id' in values and values['project_id'] is not None and v is not None:
            return v
        else:
            raise ValueError("Missing project_id field, it is required")


class CommitModel(BaseModel):
    project_id: Union[int, str]
    commit_hash: str = None
    branch: str = None
    dry_run: bool = None
    message: str = None
    state: str = None
    reference: str = None
    name: str = None
    context: str = None
    target_url: str = None
    description: str = None
    coverage: Union[float, str] = None
    pipeline_id: Union[int, str] = None
    actions: list = None
    start_branch: str = None
    start_sha: str = None
    start_project: Union[int, str] = None
    author_email: str = None
    author_name: str = None
    stats: bool = None
    force: bool = None
    line: int = None
    line_type: str = None
    note: str = None
    path: str = None
    group_ids: list = None
    protected_branch_ids: list = None
    report_type: str = None
    rule_type: str = None
    user_ids: list = None
    data: Dict = None

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


class DeployTokenModel(BaseModel):
    project_id: Union[int, str] = None
    group_id: Union[int, str] = None
    token: str = None
    name: str = None
    expires_at: str = None
    username: str = None
    scopes: str = None

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


class GroupModel(BaseModel):
    group_id: Union[int, str] = None
    per_page: int = 100
    page: int = 1
    argument: str = 'state=opened'
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


class JobModel(BaseModel):
    project_id: Union[int, str] = None
    job_id: Union[int, str] = None
    scope: List[str] = None
    per_page: int = 100
    page: int = 1
    include_retried: bool = None
    job_variable_attributes: Dict = None
    api_parameters: str = None

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


class MembersModel(BaseModel):
    group_id: Union[int, str] = None
    project_id: Union[int, str] = None
    per_page: int = 100
    page: int = 1
    api_parameters: str = None

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


class MergeRequestModel(BaseModel):
    approved_by_ids: List[int] = None
    approver_ids: List[int] = None
    assignee_id: int = None
    author_id: int = None
    author_username: str = None
    created_after: str = None
    created_before: str = None
    deployed_after: str = None
    deployed_before: str = None
    environment: str = None
    search_in: str = None
    labels: str = None
    milestone: str = None
    my_reaction_emoji: str = None
    project_id: Union[int, str] = None
    search_exclude: str = None
    order_by: str = None
    reviewer_id: Union[int, str] = None
    reviewer_username: str = None
    scope: List[str] = None
    search: str = None
    sort: str = None
    source_branch: str = None
    state: str = None
    target_branch: str = None
    updated_after: str = None
    updated_before: str = None
    view: str = None
    with_labels_details: bool = None
    with_merge_status_recheck: bool = None
    wip: str = None
    title: str
    allow_collaboration: bool = None
    allow_maintainer_to_push: bool = None
    approvals_before_merge: int = None
    assignee_ids: List[int] = None
    description: str = None
    milestone_id: int = None
    remove_source_branch: str = None
    reviewer_ids: List[int] = None
    squash: bool = None
    target_project_id: Union[int, str] = None
    max_pages: int = 0
    per_page: int = 100
    api_parameters: str = None
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


class MergeRequestRuleModel(BaseModel):
    project_id: Union[int, str] = None
    approval_rule_id: Union[int, str] = None
    approvals_required: int = None
    name: str = None
    applies_to_all_protected_branches: bool = None
    group_ids: List[int] = None
    merge_request_iid: Union[int, str] = None
    protected_branch_ids: List[int] = None
    report_type: str = None
    rule_type: str = None
    user_ids: List[int] = None
    data: Dict = None

    @field_validator("project_id", "approvals_required", "name")
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


class PackageModel(BaseModel):
    project_id: Union[int, str] = None
    package_name: str = None
    package_version: str = None
    file_name: str = None
    status: str = None
    select: str = None
    api_parameters: str = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("status") is not None:
            filters.append(f'status={values["status"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator('file_name', 'package_name')
    def validate_file_name(cls, value):
        pattern = r'^[a-zA-Z0-9._-]+$'
        if not re.match(pattern, value):
            raise ValueError("Invalid characters in the filename")

        if len(value) > 255:
            raise ValueError("Filename is too long (maximum 255 characters)")

        return value

    @field_validator("status")
    def validate_rule_type(cls, value):
        if value not in ['default', 'hidden']:
            raise ValueError("Invalid rule_type")
        return value

    @field_validator("select")
    def validate_rule_type(cls, value):
        if value not in ['package_file', 'package_file']:
            raise ValueError("Invalid rule_type")
        return value

class PipelineModel(BaseModel):
    project_id: Union[int, str] = None
    per_page: int = 100
    page: int = 1
    pipeline_id: Union[int, str] = None
    reference: str = None
    variables: Dict = None
    api_parameters: str = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("page") is not None:
            filters.append(f'page={values["page"]}')

        if values.get("per_page") is not None:
            filters.append(f'per_page={values["per_page"]}')

        if values.get("ref") is not None:
            filters.append(f'ref={values["reference"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


class ProjectModel(BaseModel):
    project_id: Union[int, str]
    group_id: Union[int, str] = None
    allow_merge_on_skipped_pipeline: bool = None
    only_allow_merge_if_all_status_checks_passed: bool = None
    analytics_access_level: str = None
    approvals_before_merge: int = None
    auto_cancel_pending_pipelines: str = None
    auto_devops_deploy_strategy: str = None
    auto_devops_enabled: bool = None
    autoclose_referenced_issues: bool = None
    avatar: str = None
    build_git_strategy: str = None
    build_timeout: int = None
    builds_access_level: str = None
    ci_config_path: str = None
    ci_default_git_depth: int = None
    ci_forward_deployment_enabled: bool = None
    ci_allow_fork_pipelines_to_run_in_parent_project: bool = None
    ci_separated_caches: bool = None
    container_expiration_policy_attributes: str = None
    container_registry_access_level: str = None
    default_branch: str = None
    description: str = None
    emails_disabled: bool = None
    enforce_auth_checks_on_uploads: bool = None
    external_authorization_classification_label: str = None
    expires_at: str = None
    forking_access_level: str = None
    group_acces: int = None
    import_url: str = None
    issues_access_level: str = None
    issues_template: str = None
    keep_latest_artifact: bool = None
    lfs_enabled: bool = None
    max_pages: int = 0
    per_page: int = 100
    merge_commit_template: str = None
    merge_method: str = None
    merge_pipelines_enabled: bool = None
    merge_requests_access_level: str = None
    merge_requests_template: str = None
    merge_trains_enabled: bool = None
    mirror_overwrites_diverged_branches: bool = None
    mirror_trigger_builds: bool = None
    mirror_user_id: int = None
    mirror: bool = None
    mr_default_target_self: bool = None
    name: str = None
    order_by: str = None
    only_allow_merge_if_all_discussions_are_resolved: bool = None
    only_allow_merge_if_pipeline_succeeds: bool = None
    only_mirror_protected_branches: bool = None
    operations_access_level: str = None
    packages_enabled: bool = None
    pages_access_level: str = None
    path: str = None
    printing_merge_request_link_enabled: bool = None
    public_builds: bool = None
    releases_access_level: str = None
    remove_source_branch_after_merge: bool = None
    repository_access_level: str = None
    repository_storage: str = None
    request_access_enabled: bool = None
    requirements_access_level: str = None
    resolve_outdated_diff_discussions: bool = None
    restrict_user_defined_variables: bool = None
    security_and_compliance_access_level: str = None
    service_desk_enabled: bool = None
    shared_runners_enabled: bool = None
    snippets_access_level: str = None
    squash_commit_template: str = None
    squash_option: str = None
    suggestion_commit_message: str = None
    tag_list: List[str] = None
    topics: List[str] = None
    visibility: str = None
    wiki_access_level: str = None
    api_parameters: str = None
    data: Dict = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("group_id") is not None:
            filters.append(f'group_id={values["group_id"]}')

        if values.get("group_access") is not None:
            filters.append(f'group_access={values["group_access"]}')

        if values.get("expires_at") is not None:
            filters.append(f'expires_at={values["expires_at"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator("analytics_access_level", "builds_access_level", "container_registry_access_level",
                     "forking_access_level", "issues_access_level", "operations_access_level", "pages_access_level",
                     "releases_access_level", "repository_access_level", "requirements_access_level",
                     "security_and_compliance_access_level", "snippets_access_level", "wiki_access_level")
    def validate_access_level(cls, value):
        valid_access_levels = ['disabled', 'private', 'enabled']
        if value and value not in valid_access_levels:
            raise ValueError("Invalid access level value")
        return value

    @field_validator("auto_cancel_pending_pipelines", "auto_devops_deploy_strategy",
                     "mirror_overwrites_diverged_branches",
                     "mirror_trigger_builds", "mr_default_target_self",
                     "only_allow_merge_if_all_discussions_are_resolved",
                     "only_allow_merge_if_pipeline_succeeds", "only_mirror_protected_branches", "auto_devops_enabled",
                     "autoclose_referenced_issues", "emails_disabled", "enforce_auth_checks_on_uploads",
                     "ci_forward_deployment_enabled", "ci_allow_fork_pipelines_to_run_in_parent_project",
                     "ci_separated_caches", "keep_latest_artifact", "lfs_enabled", "merge_pipelines_enabled",
                     "merge_trains_enabled", "printing_merge_request_link_enabled", "public_builds",
                     "remove_source_branch_after_merge", "request_access_enabled", "resolve_outdated_diff_discussions",
                     "restrict_user_defined_variables", "service_desk_enabled", "shared_runners_enabled",
                     "packages_enabled")
    def validate_boolean(cls, value):
        if value is not None and not isinstance(value, bool):
            raise ValueError("Invalid boolean value")
        return value

    @field_validator("approvals_before_merge", "build_timeout", "ci_default_git_depth", "mirror_user_id")
    def validate_positive_integer(cls, value):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("Invalid positive integer value")
        return value

    @field_validator("tag_list", "topics")
    def validate_tag_topics(cls, value):
        if value is not None and not all(isinstance(tag, str) for tag in value):
            raise ValueError("Invalid tag or topic value")
        return value

    @field_validator("order_by")
    def validate_order_by(cls, value):
        if value not in ['id', 'name', 'username', 'created_at', 'updated_at']:
            raise ValueError("Invalid order_by")
        return value


class ProtectedBranchModel(BaseModel):
    project_id: Union[int, str]
    branch: str
    push_access_level: int
    merge_access_level: int
    unprotect_access_level: int
    allow_force_push: List[str]
    allowed_to_push: List[str]
    allowed_to_merge: List[str]
    allowed_to_unprotect: List[str]
    code_owner_approval_required: bool
    api_parameters: str = None
    data: Dict = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("branch") is not None:
            filters.append(f'name={values["branch"]}')

        if values.get("push_access_level") is not None:
            filters.append(f'push_access_level={values["push_access_level"]}')

        if values.get("merge_access_level") is not None:
            filters.append(f'merge_access_level={values["merge_access_level"]}')

        if values.get("unprotect_access_level") is not None:
            filters.append(f'unprotect_access_level={values["unprotect_access_level"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator('project_id')
    def validate_project_id(cls, value):
        if value is None:
            raise ValueError('Project ID cannot be None')
        return value

    @field_validator('project_id')
    def validate_project_id_type(cls, value):
        if not isinstance(value, (int, str)):
            raise ValueError('Project ID must be an integer or a string')
        return value

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "allow_force_push": values.get("allow_force_push"),
            "allowed_to_push": values.get("allowed_to_push"),
            "allowed_to_merge": values.get("allowed_to_merge"),
            "allowed_to_unprotect": values.get("allowed_to_unprotect"),
            "code_owner_approval_required": values.get("code_owner_approval_required"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data


class ReleaseModel(BaseModel):
    project_id: Union[int, str]
    order_by: str = None
    sort: str = None
    simple: bool = None
    include_html_description: bool = None
    tag_name: str = None
    description: str = None
    tag_message: str = None
    ref: str = None
    direct_asset_path: str = None
    name: List[str] = None
    milestones: str = None
    released_at: str = None
    api_parameters: str = None
    data: Dict = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("simple") is not None:
            filters.append(f'simple=true')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


    @field_validator("order_by")
    def validate_order_by(cls, value):
        if value not in ['id', 'name', 'username', 'created_at', 'updated_at']:
            raise ValueError("Invalid order_by")
        return value

    @field_validator("sort")
    def validate_sort(cls, value):
        valid_sorts = ['asc', 'desc']
        if value and value not in valid_sorts:
            raise ValueError("Invalid sort value")
        return value

    @field_validator('project_id')
    def validate_project_id(cls, value):
        if value is None:
            raise ValueError('Project ID cannot be None')
        return value

    @field_validator('project_id')
    def validate_project_id_type(cls, value):
        if not isinstance(value, (int, str)):
            raise ValueError('Project ID must be an integer or a string')
        return value

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "name": values.get("description"),
            "tag_name": values.get("tag_name"),
            "tag_message": values.get("tag_message"),
            "description": values.get("description"),
            "ref": values.get("ref"),
            "milestones": values.get("milestones"),
            "assets:links": values.get("assets:links"),
            "assets:links:name": values.get("assets:links:name"),
            "assets:links:url": values.get("assets:links:url"),
            "assets:links:direct_asset_path": values.get("assets:links:direct_asset_path"),
            "released_at": values.get("released_at"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data


class RunnerModel(BaseModel):
    description: str = None
    active: bool = None
    paused: bool = None
    tag_list: List[str] = None
    run_untagged: bool = None
    locked: bool = None
    access_level: str = None
    maintenance_note: str = None
    info: str = None
    token: str = None
    project_id: Union[int, str] = None
    group_id: Union[int, str] = None
    maximum_timeout: int = None
    runner_type: str = None
    status: str = None
    all_runners: bool = False
    api_parameters: str = None
    data: Dict = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("tag_list") is not None:
            filters.append(f'tag_list={values["tag_list"]}')

        if values.get("runner_type") is not None:
            filters.append(f'runner_type={values["runner_type"]}')

        if values.get("status") is not None:
            filters.append(f'status={values["status"]}')

        if values.get("paused") is not None:
            filters.append(f'paused={values["paused"]}')

        if values.get("tag_list") is not None:
            filters.append(f'tag_list={values["tag_list"]}')

        if values.get("all_runners"):
            filters = ['/all']

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator("runner_type")
    def validate_runner_type(cls, value):
        if value not in ['instance_type', 'group_type', 'project_type']:
            raise ValueError("Invalid runner_type")
        return value

    @field_validator("status")
    def validate_status(cls, value):
        if value not in ['online', 'offline', 'stale', 'never_contacted', 'active', 'paused']:
            raise ValueError("Invalid status")
        return value

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "description": values.get("description"),
            "active": values.get("active"),
            "paused": values.get("paused"),
            "tag_list": values.get("tag_list"),
            "run_untagged": values.get("run_untagged"),
            "locked": values.get("locked"),
            "access_level": values.get("access_level"),
            "maximum_timeout": values.get("maximum_timeout"),
            "info": values.get("info"),
            "maintenance_note": values.get("maximum_timeout"),
            "token": values.get("token"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data


class UserModel(BaseModel):
    username: str = None
    active: bool = None
    blocked: bool = None
    external: bool = None
    exclude_internal: bool = None
    exclude_external: bool = None
    without_project_bots: bool = None
    extern_uid: str = None
    provider: str = None
    created_before: str = None
    created_after: str = None
    with_custom_attributes: str = None
    sort: str = None
    order_by: str = None
    two_factor: str = None
    without_projects: bool = None
    admins: bool = None
    saml_provider_id: str = None
    max_pages: int = 0
    page: int = 1
    per_page: int = 100
    sudo: bool = False
    user_id: Union[str, int] = None
    api_parameters: str = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("username") is not None:
            filters.append(f'username={values["username"]}')

        if values.get("active") is not None:
            filters.append(f'active={values["active"]}')

        if values.get("blocked") is not None:
            filters.append(f'blocked={values["blocked"]}')

        if values.get("external") is not None:
            filters.append(f'external={values["external"]}')

        if values.get("exclude_internal") is not None:
            filters.append(f'exclude_internal={values["exclude_internal"]}')

        if values.get("exclude_external") is not None:
            filters.append(f'exclude_external={values["exclude_external"]}')

        if values.get("without_project_bots") is not None:
            filters.append(f'without_project_bots={values["without_project_bots"]}')

        if values.get("order_by") is not None:
            filters.append(f'order_by={values["order_by"]}')

        if values.get("sort") is not None:
            filters.append(f'sort={values["sort"]}')

        if values.get("two_factor") is not None:
            filters.append(f'two_factor={values["two_factor"]}')

        if values.get("without_projects") is not None:
            filters.append(f'without_projects={values["without_projects"]}')

        if values.get("admins") is not None:
            filters.append(f'admins={values["admins"]}')

        if values.get("saml_provider_id") is not None:
            filters.append(f'saml_provider_id={values["saml_provider_id"]}')

        if values.get("extern_uid") is not None:
            filters.append(f'extern_uid={values["extern_uid"]}')

        if values.get("provider") is not None:
            filters.append(f'provider={values["provider"]}')

        if values.get("created_before") is not None:
            filters.append(f'created_before={values["created_before"]}')

        if values.get("created_after") is not None:
            filters.append(f'created_after={values["created_after"]}')

        if values.get("with_custom_attributes") is not None:
            filters.append(f'with_custom_attributes={values["with_custom_attributes"]}')

        if values.get("sudo") is not None:
            filters.append(f'sudo={values["user_id"]}')
        elif values.get("user_id") is not None:
            filters.append(f'{values["user_id"]}')

        if values.get("page") is not None:
            filters.append(f'page={values["page"]}')

        if values.get("per_page") is not None:
            filters.append(f'per_page={values["per_page"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator("order_by")
    def validate_order_by(cls, value):
        if value not in ['id', 'name', 'username', 'created_at', 'updated_at']:
            raise ValueError("Invalid order_by")
        return value

    @field_validator("sort")
    def validate_sort(cls, value):
        valid_sorts = ['asc', 'desc']
        if value and value not in valid_sorts:
            raise ValueError("Invalid sort value")
        return value

    @field_validator("two_factor")
    def validate_two_factor(cls, value):
        valid_two_factor = ['enabled', 'disabled']
        if value and value not in valid_two_factor:
            raise ValueError("Invalid two_factor value")
        return value


class WikiModel(BaseModel):
    project_id: Union[int, str] = None
    slug: str = None
    content: str = None
    title: str = None
    format_type: str = None
    with_content: bool = None
    file: str = None
    branch: str = None
    api_parameters: str = None
    data: Dict = None

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("with_content") is not None:
            filters.append(f'with_content={values["1"]}')

        if values.get("render_html") is not None:
            filters.append(f'render_html={values["1"]}')

        if values.get("version") is not None:
            filters.append(f'version={values["version"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None

    @field_validator('project_id')
    def validate_project_id(cls, value):
        if value is None:
            raise ValueError('Project ID cannot be None')
        return value

    @field_validator('project_id')
    def validate_project_id_type(cls, value):
        if not isinstance(value, (int, str)):
            raise ValueError('Project ID must be an integer or a string')
        return value

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "content": values.get("content"),
            "title": values.get("title"),
            "format": values.get("format"),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data