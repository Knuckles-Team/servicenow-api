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
    """
    Pydantic model representing an application service.

    Attributes:
    - application_id (str): Identifier for the application service.

    Note:
    The class includes a field_validator for 'application_id' to ensure it is a valid string.

    Raises:
    - ValueError: If 'application_id' is provided and not a string.
    """
    application_id: str = None

    @field_validator('application_id')
    def validate_string_parameters(cls, v):
        """
        Validate 'application_id' to ensure it is a valid string.

        Args:
        - v: The value of 'application_id'.

        Returns:
        - str: The validated 'application_id'.

        Raises:
        - ValueError: If 'application_id' is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v


class CMDBModel(BaseModel):
    """
    Pydantic model representing a Configuration Management Database (CMDB) entry.

    Attributes:
    - cmdb_id (str): Identifier for the CMDB entry.

    Note:
    The class includes a field_validator for 'cmdb_id' to ensure it is a valid string.

    Raises:
    - ValueError: If 'cmdb_id' is provided and not a string.
    """
    cmdb_id: str = None

    @field_validator('cmdb_id')
    def validate_string_parameters(cls, v):
        """
        Validate 'cmdb_id' to ensure it is a valid string.

        Args:
        - v: The value of 'cmdb_id'.

        Returns:
        - str: The validated 'cmdb_id'.

        Raises:
        - ValueError: If 'cmdb_id' is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v


class CICDModel(BaseModel):
    """
    Pydantic model representing a Continuous Integration/Continuous Deployment (CICD) entity.

    Attributes:
    - result_id (Optional[str]): Identifier for the result.
    - progress_id (Optional[str]): Identifier for the progress.
    - rollback_id (Optional[str]): Identifier for the rollback.
    - name (Optional[str]): Name of the CICD entity.
    - notes (Optional[str]): Additional notes or comments.
    - packages (Optional[str]): Package information.
    - app_sys_id (Optional[str]): Identifier for the application system.
    - scope (Optional[str]): Scope information.
    - auto_upgrade_base_app (Optional[bool]): Flag indicating automatic upgrade of the base app.
    - base_app_version (Optional[str]): Version of the base app.
    - version (Optional[str]): Version information.
    - dev_notes (Optional[str]): Developer notes.
    - combo_sys_id (Optional[str]): Identifier for the combination system.
    - suite_sys_id (Optional[str]): Identifier for the suite system.
    - app_scope_sys_ids (Optional[List[str]]): List of application scope identifiers.
    - scan_type (Optional[str]): Type of scan.
    - plugin_id (Optional[str]): Identifier for the plugin.
    - branch_name (Optional[str]): Name of the branch.
    - credential_sys_id (Optional[str]): Identifier for the credential.
    - mid_server_sys_id (Optional[str]): Identifier for the mid server.
    - repo_url (Optional[str]): URL of the repository.
    - test_suite_sys_id (Optional[str]): Identifier for the test suite.
    - test_suite_name (Optional[str]): Name of the test suite.
    - browser_name (Optional[str]): Name of the browser.
    - browser_version (Optional[str]): Version of the browser.
    - os_name (Optional[str]): Name of the operating system.
    - os_version (Optional[str]): Version of the operating system.
    - api_parameters (str): API parameters.
    - data (Dict): Dictionary containing data.

    Note:
    The class includes field_validator functions for specific attribute validations.
    """
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
    app_scope_sys_ids: Optional[List[str]] = None
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
    data: Dict = None
    sys_ids: List = None

    @field_validator('result_id', 'progress_id', 'rollback_id', 'name', 'notes', 'packages')
    def validate_string_parameters(cls, v):
        """
        Validate specific string parameters to ensure they are valid strings.

        Args:
        - v: The value of the parameter.

        Returns:
        - str: The validated parameter value.

        Raises:
        - ValueError: If the parameter is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('sys_ids')
    def validate_string_parameters(cls, v):
        """
        Validate specific string parameters to ensure they are a List

        Args:
        - v: The value of the parameter.

        Returns:
        - str: The validated parameter value as a list.

        Raises:
        - ValueError: If the parameter is provided and not a List, str, or int.
        """
        if v is not None and not isinstance(v, List):
            if v is isinstance(v, str) or v is isinstance(v, int):
                return [v]
            else:
                raise ValueError("Invalid optional params")
        return v

    @field_validator('auto_upgrade_base_app', 'browser_name')
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator('browser_name')
    def validate_browser_name(cls, v):
        """
        Validate the 'browser_name' parameter to ensure it is a valid browser name.

        Args:
        - v: The value of 'browser_name'.

        Returns:
        - str: The validated 'browser_name'.

        Raises:
        - ParameterError: If 'browser_name' is not a valid browser name.
        """
        if v not in ['any', 'chrome', 'firefox', 'edge', 'ie', 'safari']:
            raise ParameterError
        return v

    @field_validator("data")
    def construct_data_dict(cls, values):
        """
        Construct a data dictionary from specific parameters.

        Args:
        - values: The values of specific parameters.

        Returns:
        - Dict: The constructed data dictionary.

        Raises:
        - ValueError: If the data dictionary is empty.
        """
        data = {
            "name": values.get("name"),
            "packages": values.get("packages"),
            "app_scope_sys_ids": values.get("app_scope_sys_ids")
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            raise ValueError("At least one key is required in the data dictionary.")

        return data

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        """
        Build API parameters from specific values.

        Args:
        - values: The values of specific parameters.

        Returns:
        - str: The constructed API parameters.
        """
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
    """
    Pydantic model representing a Change Management entity.

    Attributes:
    - change_request_sys_id (Optional[str]): Identifier for the change request.
    - state (Optional[str]): State of the change request.
    - cmdb_ci_sys_ids (Optional[List[str]]): List of Configuration Item (CI) system identifiers.
    - cmdb_ci_sys_id (Optional[str]): Configuration Item (CI) system identifier.
    - association_type (Optional[str]): Type of association.
    - refresh_impacted_services (Optional[bool]): Flag indicating whether to refresh impacted services.
    - name_value_pairs (Optional[Dict]): Dictionary containing name-value pairs.
    - order (Optional[str]): Order for sorting (default is "desc").
    - max_pages (Optional[Union[str, int]]): Maximum number of pages.
    - per_page (Optional[Union[str, int]]): Number of items per page.
    - sysparm_query (Optional[str]): Sysparm query.
    - text_search (Optional[str]): Text search query.
    - model_sys_id (Optional[str]): Identifier for the model.
    - template_sys_id (Optional[str]): Identifier for the template.
    - worker_sys_id (Optional[str]): Identifier for the worker.
    - change_type (Optional[str]): Type of change.
    - standard_change_template_id (Optional[str]): Identifier for the standard change template.
    - response_length (int): Length of the response (default is 10).
    - api_parameters (str): API parameters.
    - data (Dict): Dictionary containing data.

    Note:
    The class includes field_validator functions for specific attribute validations.
    """
    change_request_sys_id: Optional[str]
    state: Optional[str]
    cmdb_ci_sys_ids: Optional[List[str]]
    cmdb_ci_sys_id: Optional[str]
    association_type: Optional[str]
    refresh_impacted_services: Optional[bool]
    name_value_pairs: Optional[Dict]
    order: Optional[str] = "desc"
    max_pages: Optional[Union[str, int]]
    per_page: Optional[Union[str, int]]
    sysparm_query: Optional[str]
    text_search: Optional[str]
    model_sys_id: Optional[str]
    template_sys_id: Optional[str]
    worker_sys_id: Optional[str]
    change_type: Optional[str]
    standard_change_template_id: Optional[str]
    response_length: int = 10
    api_parameters: str = None
    data: Dict = None

    @field_validator('change_request_sys_id', 'cmdb_ci_sys_ids', 'standard_change_template_id',
                     'template_sys_id', 'worker_sys_id')
    def validate_string_parameters(cls, v):
        """
        Validate specific string parameters to ensure they are valid strings.

        Args:
        - v: The value of the parameter.

        Returns:
        - str: The validated parameter value.

        Raises:
        - ValueError: If the parameter is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('state', 'change_type')
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator('change_type')
    def validate_change_type(cls, v):
        """
        Validate the 'change_type' parameter to ensure it is a valid change type.

        Args:
        - v: The value of 'change_type'.

        Returns:
        - str: The validated 'change_type'.

        Raises:
        - ParameterError: If 'change_type' is not a valid change type.
        """
        if v not in ['emergency', 'normal', 'standard', 'model']:
            raise ParameterError
        return v

    @field_validator('association_type')
    def validate_association_type(cls, v):
        """
        Validate the 'association_type' parameter to ensure it is a valid association type.

        Args:
        - v: The value of 'association_type'.

        Returns:
        - str: The validated 'association_type'.

        Raises:
        - ParameterError: If 'association_type' is not a valid association type.
        """
        if v not in ['affected', 'impacted', 'offering']:
            raise ParameterError
        return v

    @field_validator('state')
    def validate_state(cls, v):
        """
        Validate the 'state' parameter to ensure it is a valid state.

        Args:
        - v: The value of 'state'.

        Returns:
        - str: The validated 'state'.

        Raises:
        - ParameterError: If 'state' is not a valid state.
        """
        if v not in ['approved', 'rejected']:
            raise ParameterError
        return v

    @field_validator("data")
    def construct_data_dict(cls, values):
        """
        Construct a data dictionary from specific parameters.

        Args:
        - values: The values of specific parameters.

        Returns:
        - Dict: The constructed data dictionary.

        Raises:
        - ValueError: If the data dictionary is empty.
        """
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
        """
        Build API parameters from specific values.

        Args:
        - values: The values of specific parameters.

        Returns:
        - str: The constructed API parameters.
        """
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
    """
    Pydantic model representing an Import Set.

    Attributes:
    - table (str): Name of the table.
    - import_set_sys_id (Optional[str]): System identifier for the Import Set.
    - data (Dict): Dictionary containing additional data.
    """
    table: str
    import_set_sys_id: Optional[str]
    data: Dict = None

    @field_validator('table', 'import_set_sys_id')
    def validate_string_parameters(cls, v):
        """
        Validate specific string parameters to ensure they are valid strings.

        Args:
        - v: The value of the parameter.

        Returns:
        - str: The validated parameter value.

        Raises:
        - ValueError: If the parameter is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v


class IncidentModel(BaseModel):
    """
    Pydantic model representing an Incident.

    Attributes:
    - incident_id (Union[int, str]): Identifier for the incident.
    - data (Dict): Dictionary containing additional data.
    """
    incident_id: Union[int, str] = None
    data: Dict = None

    @field_validator('incident_id')
    def validate_string_parameters(cls, v):
        """
        Validate the 'incident_id' parameter to ensure it is a valid string.

        Args:
        - v: The value of 'incident_id'.

        Returns:
        - str: The validated 'incident_id'.

        Raises:
        - ValueError: If 'incident_id' is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v


class TableModel(BaseModel):
    """
    Pydantic model representing a Table.

    Attributes:
    - table (str): Name of the table.
    - table_record_sys_id (Optional[str]): System identifier for the table record.
    - name_value_pairs (Optional[Dict]]): Dictionary containing name-value pairs.
    - sysparm_display_value (Optional[str]): Sysparm display value.
    - sysparm_exclude_reference_link (Optional[bool]): Flag indicating whether to exclude reference link.
    - sysparm_fields (Optional[str]): Sysparm fields.
    - sysparm_limit (Optional[Union[str, int]]): Sysparm limit.
    - sysparm_no_count (Optional[bool]): Flag indicating whether to omit count.
    - sysparm_offset (Optional[Union[str, int]]): Sysparm offset.
    - sysparm_query (Optional[str]): Sysparm query.
    - sysparm_query_category (Optional[str]): Sysparm query category.
    - sysparm_query_no_domain (Optional[bool]): Flag indicating whether to exclude domain from the query.
    - sysparm_suppress_pagination_header (Optional[bool]): Flag indicating whether to suppress pagination header.
    - sysparm_view (Optional[str]): Sysparm view.
    - api_parameters (str): API parameters.
    - data (Dict): Dictionary containing additional data.

    Note:
    The class includes field_validator functions for specific attribute validations.
    """
    table: str
    table_record_sys_id: Optional[str]
    name_value_pairs: Optional[Dict]
    sysparm_display_value: Optional[str]
    sysparm_exclude_reference_link: Optional[bool]
    sysparm_fields: Optional[str]
    sysparm_limit: Optional[Union[str, int]]
    sysparm_no_count: Optional[bool]
    sysparm_offset: Optional[Union[str, int]]
    sysparm_query: Optional[str]
    sysparm_query_category: Optional[str]
    sysparm_query_no_domain: Optional[bool]
    sysparm_suppress_pagination_header: Optional[bool]
    sysparm_view: Optional[str]
    api_parameters: str = None
    data: Dict = None

    @field_validator('table', 'table_record_sys_id')
    def validate_string_parameters(cls, v):
        """
        Validate specific string parameters to ensure they are valid strings.

        Args:
        - v: The value of the parameter.

        Returns:
        - str: The validated parameter value.

        Raises:
        - ValueError: If the parameter is provided and not a string.
        """
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator('sysparm_display_value', 'sysparm_no_count', 'sysparm_query_no_domain',
                     'sysparm_suppress_pagination_header')
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator('sysparm_view')
    def validate_sysparm_view(cls, v):
        """
        Validate the 'sysparm_view' parameter to ensure it is a valid view.

        Args:
        - v: The value of 'sysparm_view'.

        Returns:
        - str: The validated 'sysparm_view'.

        Raises:
        - ParameterError: If 'sysparm_view' is not a valid view.
        """
        if v not in ['desktop', 'mobile', 'both']:
            raise ParameterError
        return v

    @field_validator('sysparm_display_value')
    def validate_sysparm_display_value(cls, v):
        """
        Validate the 'sysparm_display_value' parameter to ensure it is a valid display value.

        Args:
        - v: The value of 'sysparm_display_value'.

        Returns:
        - str: The validated 'sysparm_display_value'.

        Raises:
        - ParameterError: If 'sysparm_display_value' is not a valid display value.
        """
        if v not in [True, False, 'all']:
            raise ParameterError
        return v

    @field_validator("api_parameters")
    def build_api_parameters(cls, values):
        """
        Build API parameters from specific values.

        Args:
        - values: The values of specific parameters.

        Returns:
        - str: The constructed API parameters.
        """
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
