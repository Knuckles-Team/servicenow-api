import ast
from typing import Union, List, Dict, Optional
from pydantic import BaseModel, field_validator

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

    @field_validator('application_id')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v


class CMDBModel(BaseModel):
    cmdb_id: str = None

    @field_validator('cmdb_id')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
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

    @field_validator('result_id', 'progress_id', 'rollback_id', 'name', 'notes', 'packages')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('auto_upgrade_base_app', 'browser_name')
    def convert_to_lowercase(cls, value):
        return value.lower()

    @field_validator('browser_name')
    def validate_browser_name(cls, v):
        if v not in ['any', 'chrome', 'firefox', 'edge', 'ie', 'safari']:
            raise ParameterError
        return v

    @field_validator("data")
    def construct_data_dict(cls, values):
        data = {
            "name": values.get("name"),
            "packages": values.get("packages"),
            "app_scope_sys_ids": values.get("sys_ids")
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("sys_id") is not None:
            filters.append(f'sys_id={values["sys_id"]}')

        if values.get("scope") is not None:
            filters.append(f'scope={values["scope"]}')

        if values.get("auto_upgrade_base_app") is not None:
            filters.append(f'auto_upgrade_base_app={values["auto_upgrade_base_app"]}')

        if values.get("base_app_version") is not None:
            filters.append(f'base_app_version={values["base_app_version"]}')

        if values.get("version") is not None:
            filters.append(f'version={values["version"]}')

        if values.get("dev_notes") is not None:
            filters.append(f'dev_notes={values["dev_notes"]}')

        if values.get("target_table") is not None:
            filters.append(f'target_table={values["target_table"]}')

        if values.get("target_sys_id") is not None:
            filters.append(f'target_sys_id={values["target_sys_id"]}')

        if values.get("app_sys_id") is not None:
            filters.append(f'app_sys_id={values["app_sys_id"]}')

        if values.get("branch_name") is not None:
            filters.append(f'branch_name={values["branch_name"]}')

        if values.get("credential_sys_id") is not None:
            filters.append(f'credential_sys_id={values["credential_sys_id"]}')

        if values.get("mid_server_sys_id") is not None:
            filters.append(f'mid_server_sys_id={values["mid_server_sys_id"]}')

        if values.get("test_suite_sys_id") is not None:
            filters.append(f'test_suite_sys_id={values["test_suite_sys_id"]}')

        if values.get("test_suite_name") is not None:
            filters.append(f'test_suite_name={values["test_suite_name"]}')

        if values.get("browser_name") is not None:
            filters.append(f'browser_name={values["browser_name"]}')

        if values.get("browser_version") is not None:
            filters.append(f'browser_version={values["browser_version"]}')

        if values.get("os_name") is not None:
            filters.append(f'os_name={values["os_name"]}')

        if values.get("os_version") is not None:
            filters.append(f'os_version={values["os_version"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


class ChangeManagementModel(BaseModel):
    change_request_sys_id: Optional[str]
    state: Optional[str]
    cmdb_ci_sys_ids: Optional[List[str]]
    cmdb_ci_sys_id: Optional[str]
    association_type: Optional[str]
    refresh_impacted_services: Optional[bool]
    name_value_pairs: Optional[Dict[str, Union[str, int, bool]]]
    order: Optional[str] = "desc"
    max_pages: Optional[int]
    per_page: Optional[int]
    sysparm_query: Optional[str]
    text_search: Optional[str]
    model_sys_id: Optional[str]
    template_sys_id: Optional[str]
    worker_sys_id: Optional[str]
    change_type: Optional[str]
    standard_change_template_id: Optional[str]
    response_length: int = 10

    @field_validator('change_request_sys_id', 'cmdb_ci_sys_ids', 'standard_change_template_id',
                     'template_sys_id', 'worker_sys_id')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('state', 'change_type')
    def convert_to_lowercase(cls, value):
        return value.lower()

    @field_validator('change_type')
    def validate_change_type(cls, v):
        if v not in ['emergency', 'normal', 'standard', 'model']:
            raise ParameterError
        return v

    @field_validator('association_type')
    def validate_association_type(cls, v):
        if v not in ['affected', 'impacted', 'offering']:
            raise ParameterError
        return v

    @field_validator('association_type')
    def validate_state(cls, v):
        if v not in ['approved', 'rejected']:
            raise ParameterError
        return v

    @field_validator("data")
    def construct_data_dict(cls, values):

        if values.get("name_value_pairs"):
            data = ast.literal_eval(values)
        else:
            data = {
                "association_type": values.get("association_type"),
                "refresh_impacted_services": values.get("refresh_impacted_services"),
                "cmdb_ci_sys_ids": values.get("cmdb_ci_sys_ids"),
                "state": values.get("state"),
            }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("name_value_pairs") is not None:
            filters.append(f'{values["name_value_pairs"]}')

        if values.get("sysparm_query") is not None:
            filters.append(f'sysparm_query={values["sysparm_query"]}ORDERBY{values["order"]}')

        if values.get("textSearch") is not None:
            filters.append(f'textSearch={values["textSearch"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None


class ImportSetModel(BaseModel):
    table: str
    import_set_sys_id: Optional[str]
    data: Dict = None

    @field_validator('table', 'import_set_sys_id')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

class IncidentModel(BaseModel):
    incident_id: Union[int, str] = None
    data: Dict = None

    @field_validator('incident_id')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v


class TableModel(BaseModel):
    table: str
    table_record_sys_id: Optional[str]
    name_value_pairs: Optional[Dict[str, Union[str, int, bool]]]
    sysparm_display_value: Optional[str, bool]
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

    @field_validator('table', 'table_record_sys_id')
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('sysparm_display_value', 'sysparm_no_count', 'sysparm_query_no_domain',
                     'sysparm_suppress_pagination_header')
    def convert_to_lowercase(cls, value):
        return value.lower()

    @field_validator('sysparm_view')
    def validate_sysparm_view(cls, v):
        if v not in ['desktop', 'mobile', 'both']:
            raise ParameterError
        return v

    @field_validator('sysparm_display_value')
    def validate_sysparm_display_value(cls, v):
        if v not in [True, False, 'all']:
            raise ParameterError
        return v

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        filters = []

        if values.get("name_value_pairs") is not None:
            filters.append(f'{values["name_value_pairs"]}')

        if values.get("sysparm_display_value") is not None:
            filters.append(f'sysparm_display_value={values["sysparm_display_value"]}')

        if values.get("sysparm_exclude_reference_link") is not None:
            filters.append(f'sysparm_exclude_reference_link={values["sysparm_exclude_reference_link"]}')

        if values.get("sysparm_fields") is not None:
            filters.append(f'sysparm_fields={values["sysparm_fields"]}')

        if values.get("sysparm_limit") is not None:
            filters.append(f'sysparm_limit={values["sysparm_limit"]}')

        if values.get("sysparm_no_count") is not None:
            filters.append(f'sysparm_no_count={values["sysparm_no_count"]}')

        if values.get("sysparm_offset") is not None:
            filters.append(f'sysparm_offset={values["sysparm_offset"]}')

        if values.get("sysparm_query") is not None:
            filters.append(f'sysparm_query={values["sysparm_query"]}')

        if values.get("sysparm_query_category") is not None:
            filters.append(f'sysparm_query_category={values["sysparm_query_category"]}')

        if values.get("sysparm_query_no_domain") is not None:
            filters.append(f'sysparm_query_no_domain={values["sysparm_query_no_domain"]}')

        if values.get("sysparm_suppress_pagination_header") is not None:
            filters.append(f'sysparm_suppress_pagination_header={values["sysparm_suppress_pagination_header"]}')

        if values.get("sysparm_view") is not None:
            filters.append(f'sysparm_view={values["sysparm_view"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            return api_parameters

        return None
