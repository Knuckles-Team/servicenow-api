from typing import Union, List, Dict, Optional
from pydantic import BaseModel, field_validator, model_validator

try:
    from servicenow_api.decorators import require_auth
except ModuleNotFoundError:
    pass
try:
    from servicenow_api.exceptions import (
        AuthError,
        UnauthorizedError,
        ParameterError,
        MissingParameterError,
    )
except ModuleNotFoundError:
    from exceptions import (
        ParameterError,
    )


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

    @field_validator("application_id")
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

    @field_validator("cmdb_id")
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
    api_parameters: Optional[str] = ""
    data: Dict = Optional[None]
    sys_ids: Optional[List] = None

    @field_validator(
        "result_id", "progress_id", "rollback_id", "name", "notes", "packages"
    )
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

    @field_validator("sys_ids")
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

    @field_validator("auto_upgrade_base_app", "browser_name")
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator("browser_name")
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
        if v not in ["any", "chrome", "firefox", "edge", "ie", "safari"]:
            raise ParameterError
        return v

    @model_validator(mode="before")
    def build_api_parameters(cls, values):
        """
        Build API parameters.

        Args:
        - values: Dictionary of values.

        Returns:
        - The constructed API parameters string.

        Raises:
        - None.
        """

        filters = []
        if "sys_id" in values:
            filters.append(f'sys_id={values["sys_id"]}')
        if "scope" in values:
            filters.append(f'scope={values["scope"]}')
        if "auto_upgrade_base_app" in values:
            filters.append(f'auto_upgrade_base_app={values["auto_upgrade_base_app"]}')
        if "base_app_version" in values:
            filters.append(f'base_app_version={values["base_app_version"]}')
        if "version" in values:
            filters.append(f'version={values["version"]}')
        if "dev_notes" in values:
            filters.append(f'dev_notes={values["dev_notes"]}')
        if "target_table" in values:
            filters.append(f'target_table={values["target_table"]}')
        if "target_sys_id" in values:
            filters.append(f'target_sys_id={values["target_sys_id"]}')
        if "app_sys_id" in values:
            filters.append(f'app_sys_id={values["app_sys_id"]}')
        if "branch_name" in values:
            filters.append(f'branch_name={values["branch_name"]}')
        if "credential_sys_id" in values:
            filters.append(f'credential_sys_id={values["credential_sys_id"]}')
        if "mid_server_sys_id" in values:
            filters.append(f'mid_server_sys_id={values["mid_server_sys_id"]}')
        if "browser_name" in values:
            filters.append(f'browser_name={values["browser_name"]}')
        if "browser_version" in values:
            filters.append(f'browser_version={values["browser_version"]}')
        if "os_name" in values:
            filters.append(f'os_name={values["os_name"]}')
        if "os_version" in values:
            filters.append(f'os_version={values["os_version"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            values["api_parameters"] = api_parameters

        data = {}

        if "name" in values:
            data["name"] = values.get("name")
        if "packages" in values:
            data["packages"] = values.get("packages")
        if "app_scope_sys_ids" in values:
            data["app_scope_sys_ids"] = values.get("app_scope_sys_ids")

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        values["data"] = data
        return values


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
    - change_model_sys_id (Optional[str]): Identifier for the model.
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
    change_model_sys_id: Optional[str]
    template_sys_id: Optional[str]
    worker_sys_id: Optional[str]
    change_type: Optional[str]
    standard_change_template_id: Optional[str]
    response_length: int = 10
    api_parameters: Optional[str] = ""
    data: Dict = Optional[None]

    @field_validator(
        "change_request_sys_id",
        "cmdb_ci_sys_ids",
        "standard_change_template_id",
        "template_sys_id",
        "worker_sys_id",
    )
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

    @field_validator("state", "change_type")
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator("change_type")
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
        if v not in ["emergency", "normal", "standard", "model"]:
            raise ParameterError
        return v

    @field_validator("association_type")
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
        if v not in ["affected", "impacted", "offering"]:
            raise ParameterError
        return v

    @field_validator("state")
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
        if v not in ["approved", "rejected"]:
            raise ParameterError
        return v

    @model_validator(mode="before")
    def build_api_parameters(cls, values):
        """
        Build API parameters.

        Args:
        - values: Dictionary of values.

        Returns:
        - The constructed API parameters string.

        Raises:
        - None.
        """
        filters = []
        if "name_value_pairs" in values:
            filters.append(f'{values["name_value_pairs"]}')
        if "textSearch" in values:
            filters.append(f'textSearch={values["textSearch"]}')
        if "sysparm_query" in values:
            filters.append(
                f'sysparm_query={values["sysparm_query"]}ORDERBY{values["order"]}'
            )

        if filters:
            api_parameters = "?" + "&".join(filters)
            values["api_parameters"] = api_parameters

        data = {}

        if "association_type" in values:
            data["association_type"] = values.get("association_type")
        if "refresh_impacted_services" in values:
            data["refresh_impacted_services"] = values.get("refresh_impacted_services")
        if "cmdb_ci_sys_ids" in values:
            data["cmdb_ci_sys_ids"] = values.get("cmdb_ci_sys_ids")
        if "state" in values:
            data["state"] = values.get("state")

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        values["data"] = data
        return values


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
    data: Optional[Dict] = None

    @field_validator("table", "import_set_sys_id")
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
    data: Optional[Dict] = None

    @field_validator("incident_id")
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


class KnowledgeManagementModel(BaseModel):
    """
    Pydantic model representing Knowledge Management.

    Attributes:
    - article_sys_id (Optional[str]): System identifier for the article.
    - attachment_sys_id (Optional[str]): System identifier for the attachment.
    - sysparm_fields (Optional[str]): Sysparm fields.
    - sysparm_limit (Optional[Union[str, int]]): Sysparm limit.
    - sysparm_offset (Optional[Union[str, int]]): Sysparm offset.
    - sysparm_query (Optional[str]): Sysparm query.
    - sysparm_search_id (Optional[str]): Sysparm search ID.
    - sysparm_search_rank (Optional[int]): Sysparm search rank.
    - sysparm_update_view (Optional[bool]): Flag indicating whether to update the view.
    - api_parameters (str): API parameters.

    Note:
    The class includes field_validator functions for specific attribute validations.
    """

    article_sys_id: Optional[str] = None
    attachment_sys_id: Optional[str] = None
    sysparm_fields: Optional[str] = None
    sysparm_limit: Optional[Union[str, int]] = None
    sysparm_offset: Optional[Union[str, int]] = None
    sysparm_query: Optional[str] = None
    sysparm_search_id: Optional[str] = None
    sysparm_search_rank: Optional[int] = None
    sysparm_update_view: Optional[bool] = None
    api_parameters: Optional[str] = ""

    @model_validator(mode="before")
    def build_api_parameters(cls, values):
        """
        Build API parameters.

        Args:
        - values: Dictionary of values.

        Returns:
        - The constructed API parameters string.

        Raises:
        - None.
        """
        filters = []
        if "sysparm_fields" in values:
            filters.append(f'sysparm_fields={values["sysparm_fields"]}')
        if "sysparm_limit" in values:
            filters.append(f'sysparm_limit={values["sysparm_limit"]}')
        if "sysparm_search_id" in values:
            filters.append(f'sysparm_search_id={values["sysparm_search_id"]}')
        if "sysparm_search_rank" in values:
            filters.append(f'sysparm_search_rank={values["sysparm_search_rank"]}')
        if "sysparm_update_view" in values:
            filters.append(f'sysparm_update_view={values["sysparm_update_view"]}')
        if "sysparm_offset" in values:
            filters.append(f'sysparm_offset={values["sysparm_offset"]}')
        if "sysparm_query" in values:
            filters.append(f'sysparm_query={values["sysparm_query"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            values["api_parameters"] = api_parameters
        return values


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

    table: str = None
    table_record_sys_id: Optional[str] = None
    name_value_pairs: Optional[Dict] = None
    sysparm_display_value: Optional[str] = None
    sysparm_exclude_reference_link: Optional[bool] = None
    sysparm_fields: Optional[str] = None
    sysparm_limit: Optional[Union[str, int]] = None
    sysparm_no_count: Optional[bool] = None
    sysparm_offset: Optional[Union[str, int]] = None
    sysparm_query: Optional[str] = None
    sysparm_query_category: Optional[str] = None
    sysparm_query_no_domain: Optional[bool] = None
    sysparm_suppress_pagination_header: Optional[bool] = None
    sysparm_view: Optional[str] = None
    api_parameters: Optional[str] = ""
    data: Optional[Dict] = None

    @field_validator("table", "table_record_sys_id")
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

    @field_validator(
        "sysparm_display_value",
        "sysparm_no_count",
        "sysparm_query_no_domain",
        "sysparm_suppress_pagination_header",
    )
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator("sysparm_view")
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
        if v not in ["desktop", "mobile", "both"]:
            raise ParameterError
        return v

    @field_validator("sysparm_display_value")
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
        if v not in [True, False, "all"]:
            raise ParameterError
        return v

    @model_validator(mode="before")
    def build_api_parameters(cls, values):
        """
        Build API parameters.

        Args:
        - values: Dictionary of values.

        Returns:
        - The constructed API parameters string.

        Raises:
        - None.
        """
        filters = []
        if "name_value_pairs" in values:
            filters.append(f'{values["name_value_pairs"]}')
        if "sysparm_display_value" in values:
            filters.append(f'sysparm_display_value={values["sysparm_display_value"]}')
        if "sysparm_exclude_reference_link" in values:
            filters.append(
                f'sysparm_exclude_reference_link={values["sysparm_exclude_reference_link"]}'
            )
        if "sysparm_fields" in values:
            filters.append(f'sysparm_fields={values["sysparm_fields"]}')
        if "sysparm_limit" in values:
            filters.append(f'sysparm_limit={values["sysparm_limit"]}')
        if "sysparm_no_count" in values:
            filters.append(f'sysparm_no_count={values["sysparm_no_count"]}')
        if "sysparm_offset" in values:
            filters.append(f'sysparm_offset={values["sysparm_offset"]}')
        if "sysparm_query" in values:
            filters.append(f'sysparm_query={values["sysparm_query"]}')
        if "sysparm_query_category" in values:
            filters.append(f'sysparm_query_category={values["sysparm_query_category"]}')
        if "sysparm_query_no_domain" in values:
            filters.append(
                f'sysparm_query_no_domain={values["sysparm_query_no_domain"]}'
            )
        if "sysparm_suppress_pagination_header" in values:
            filters.append(
                f'sysparm_suppress_pagination_header={values["sysparm_suppress_pagination_header"]}'
            )
        if "sysparm_view" in values:
            filters.append(f'sysparm_view={values["sysparm_view"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            values["api_parameters"] = api_parameters

        return values
