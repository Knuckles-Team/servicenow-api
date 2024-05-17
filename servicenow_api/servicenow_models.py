from typing import Union, List, Dict, Optional, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, Discriminator, Tag, field_validator, model_validator

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


########################################################################################################################
#                                               Input Models                                                           #
########################################################################################################################


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

    model_config = ConfigDict(validate_assignment=True)
    application_id: Optional[str] = None
    mode: Optional[str] = None
    api_parameters: Optional[str] = None

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

    @field_validator("mode")
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        return value.lower()

    @field_validator("mode")
    def validate_mode(cls, v):
        if v is not None and v in ["full", "shallow"]:
            raise ValueError("Invalid optional params")
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
        if "mode" in values:
            filters.append(f'mode={values["mode"]}')

        if filters:
            api_parameters = "?" + "&".join(filters)
            values["api_parameters"] = api_parameters

        return values


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

    model_config = ConfigDict(validate_assignment=True)
    cmdb_id: Optional[str] = None

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

    model_config = ConfigDict(validate_assignment=True)
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
    def validate_sys_ids_parameters(cls, v):
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

    model_config = ConfigDict(validate_assignment=True)
    change_request_sys_id: Optional[str] = None
    state: Optional[str] = None
    cmdb_ci_sys_ids: Optional[List[str]] = None
    cmdb_ci_sys_id: Optional[str] = None
    association_type: Optional[str] = None
    refresh_impacted_services: Optional[bool] = None
    name_value_pairs: Optional[str] = None
    order: Optional[str] = None
    sysparm_limit: Optional[Union[str, int]] = None
    sysparm_offset: Optional[Union[str, int]] = None
    sysparm_query: Optional[str] = None
    text_search: Optional[str] = None
    change_model_sys_id: Optional[str] = None
    template_sys_id: Optional[str] = None
    worker_sys_id: Optional[str] = None
    change_type: Optional[str] = None
    standard_change_template_id: Optional[str] = None
    response_length: int = 10
    api_parameters: Optional[str] = ""
    data: Optional[Dict] = None

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
        if v is not None and v not in ["emergency", "normal", "standard", "model"]:
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
        if v is not None and v not in ["affected", "impacted", "offering"]:
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
        if v is not None and v not in ["approved", "rejected"]:
            raise ParameterError
        return v

    @field_validator("order")
    def validate_order(cls, v):
        """
        Validate the 'state' parameter to ensure it is a valid state.

        Args:
        - v: The value of 'state'.

        Returns:
        - str: The validated 'state'.

        Raises:
        - ParameterError: If 'state' is not a valid state.
        """
        if v is not None and "^ORDERBY" not in v and "^ORDERBYDESC" not in v:
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
        if "name_value_pairs" in values and values["name_value_pairs"]:
            filters.append(values["name_value_pairs"])
        if "textSearch" in values and values["textSearch"]:
            filters.append(f'textSearch={values["textSearch"]}')
        if "sysparm_query" in values and values["sysparm_query"]:
            filters.append(f'sysparm_query={values["sysparm_query"]}')
        if "sysparm_limit" in values and values["sysparm_limit"]:
            filters.append(f'sysparm_limit={values["sysparm_limit"]}')
        if "sysparm_offset" in values and values["sysparm_offset"]:
            filters.append(f'sysparm_offset={values["sysparm_offset"]}')

        if filters:
            values["api_parameters"] = "?" + "&".join(filters)

        if "order" in values and values["order"]:
            values["api_parameters"] = f"{values['api_parameters']}{values['order']}"

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

    model_config = ConfigDict(validate_assignment=True)
    table: Optional[str] = None
    import_set_sys_id: Optional[str] = None
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

    model_config = ConfigDict(validate_assignment=True)
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

    model_config = ConfigDict(validate_assignment=True)
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

    model_config = ConfigDict(validate_assignment=True)
    table: Optional[str] = None
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


########################################################################################################################
#                                              Output Models                                                           #
########################################################################################################################
class FieldValue(BaseModel):
    __hash__ = object.__hash__
    value: Optional[str] = Field(default=None, description="The value of the field.")
    display_value: Optional[str] = Field(
        default=None, description="The display value of the field."
    )


class BatchItem(BaseModel):
    __hash__ = object.__hash__
    customization_version: Optional[str] = Field(
        default=None,
        description="Version of the store application or scoped ServiceNow plugin customization package to install, "
                    "such as 1.0.2 or 2.3.",
    )
    id: Optional[str] = Field(
        default=None,
        description="Sys_id of the application or identifier of the plugin to install.",
    )
    install_date: Optional[str] = Field(
        default=None, description="Date and time that the package was installed."
    )
    name: Optional[str] = Field(default=None, description="Name of the package.")
    notes: Optional[str] = Field(
        default=None, description="User specified notes about the package."
    )
    state: Optional[str] = Field(
        default=None,
        description="Current state of the associated package installation.",
    )
    status_message: Optional[str] = Field(
        default=None,
        description="Describes any errors that occurred during the installation of the package and/or customizations.",
    )
    type: Optional[str] = Field(default=None, description="Type of application.")
    url: Optional[str] = Field(
        default=None,
        description="URL of the associated package installation record on your ServiceNow instance.",
    )
    version: Optional[str] = Field(
        default=None,
        description="Version of the package to install, such as 1.0.2 or 2.3.",
    )


class BatchPlan(BaseModel):
    __hash__ = object.__hash__
    id: Optional[str] = Field(
        default=None, description="Sys_id of the return results information."
    )
    name: Optional[str] = Field(
        default=None,
        description="User specified descriptive name for this batch request.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Notes that were passed in when the batch install was invoked.",
    )
    state: Optional[str] = Field(
        default=None, description="Current state of the overall batch installation."
    )
    url: Optional[str] = Field(
        default=None,
        description="URL of the batch installation plan record on your ServiceNow instance.",
    )


class BatchInstallResult(BaseModel):
    __hash__ = object.__hash__
    error: Optional[str] = Field(default=None, description="Error message.")
    batch_items: Optional[List[BatchItem]] = Field(
        default=None,
        description="JSON array, where each object provides details of a "
                    "package installation.",
    )
    batch_plan: Optional[BatchPlan] = Field(
        default=None, description="Describes the installation batch plan."
    )


class ChangeRequest(BaseModel):
    __hash__ = object.__hash__
    action_status: Optional[int] = Field(
        default=None,
        description="Current action status of the associated change request.",
    )
    active: Optional[bool] = Field(
        default=True, description="Flag that indicates whether the change request is active."
    )
    activity_due: Optional[str] = Field(
        default=None,
        description="Date and time for which the associated case is expected to "
                    "be completed.",
    )
    additional_assignee_list: Optional[List[str]] = Field(
        default=None,
        description="List of sys_ids of additional persons "
                    "assigned to work on the change request.",
    )
    approval: Optional[str] = Field(
        default=None, description="Type of approval process required."
    )
    approval_history: Optional[str] = Field(
        default=None, description="Most recent approval history journal entry."
    )
    approval_set: Optional[str] = Field(
        default=None,
        description="Date and time that the associated action was approved.",
    )
    assigned_to: Optional[str] = Field(
        default=None, description="Sys_id of the user assigned to the change request."
    )
    assignment_group: Optional[str] = Field(
        default=None, description="Sys_id of the group assigned to the change request."
    )
    backout_plan: Optional[str] = Field(
        default=None,
        description="Description of the plan to execute if the change must be "
                    "reversed.",
    )
    business_duration: Optional[str] = Field(
        default=None,
        description="Length in scheduled work hours, work days, and work "
                    "weeks that it took to complete the change.",
    )
    business_service: Optional[str] = Field(
        default=None,
        description="Sys_id of the business service associated with the "
                    "change request.",
    )
    cab_date: Optional[str] = Field(
        default=None, description="Date on which the Change Advisory Board (CAB) meets."
    )
    cab_delegate: Optional[str] = Field(
        default=None,
        description="Sys_id of the user that can substitute for the CAB manager "
                    "during a CAB meeting.",
    )
    cab_recommendation: Optional[str] = Field(
        default=None,
        description="Description of the CAB recommendations for the change request.",
    )
    cab_required: Optional[bool] = Field(
        False, description="Flag that indicates whether the CAB is required."
    )
    calendar_duration: Optional[str] = Field(
        default=None, description="Not currently used by Change Management."
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of the change, for example hardware, network, or software.",
    )
    change_plan: Optional[str] = Field(
        default=None,
        description="Activities and roles for managing and controlling the change request.",
    )
    chg_model: Optional[str] = Field(
        default=None,
        description="Sys_id of the change model that the associated change request was based on.",
    )
    closed_at: Optional[str] = Field(
        default=None,
        description="Date and time that the associated change request was closed.",
    )
    closed_by: Optional[str] = Field(
        default=None, description="Sys_id of the person that closed the change request."
    )
    close_code: Optional[str] = Field(
        default=None,
        description="Code assigned to the change request when it was closed.",
    )
    close_notes: Optional[str] = Field(
        default=None,
        description="Notes that the person entered when closing the change request.",
    )
    cmdb_ci: Optional[str] = Field(
        default=None,
        description="Sys_id of the configuration item associated with the change request.",
    )
    comments: Optional[List[str]] = Field(
        default=None,
        description="List of customer-facing work notes entered in the associated change request.",
    )
    comments_and_work_notes: Optional[List[str]] = Field(
        default=None,
        description="List of both internal and customer-facing work notes entered for the associated change request.",
    )
    company: Optional[str] = Field(
        default=None,
        description="Sys_id of the company associated with the change request.",
    )
    conflict_last_run: Optional[str] = Field(
        default=None,
        description="Date and time that the conflict detection script was last run on the change request.",
    )
    conflict_status: Optional[str] = Field(
        default=None,
        description="Current conflict status as detected by the conflict detection script.",
    )
    contact_type: Optional[str] = Field(
        default=None,
        description="Method in which the change request was initially requested.",
    )
    contract: Optional[str] = Field(
        default=None,
        description="Sys_id of the contract associated with the change request.",
    )
    correlation_display: Optional[str] = Field(
        default=None, description="User-friendly name for the correlation_id."
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Globally unique ID (GUID) of a matching change request record in a third-party system.",
    )
    delivery_plan: Optional[str] = Field(
        default=None,
        description="No longer in use. Sys_id of the delivery plan associated with the change request.",
    )
    delivery_task: Optional[str] = Field(
        default=None,
        description="No longer in use. Sys_id of the delivery task associated with the change request.",
    )
    description: Optional[str] = Field(
        default=None, description="Detailed description of the change request."
    )
    due_date: Optional[str] = Field(
        default=None, description="Task due date. Not used by change request process."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Date and time when the change request is to be completed.",
    )
    escalation: Optional[int] = Field(
        default=None, description="Current escalation level."
    )
    expected_start: Optional[str] = Field(
        default=None,
        description="Date and time when the task is to start. Not used by the change request process.",
    )
    follow_up: Optional[str] = Field(
        default=None,
        description="Date and time when a user followed-up with the person requesting the change request.",
    )
    group_list: Optional[List[str]] = Field(
        default=None,
        description="List of sys_ids and names of the groups associated with the change request.",
    )
    impact: Optional[int] = Field(
        default=None,
        description="Impact on the change request will have on the customer.",
    )
    implementation_plan: Optional[str] = Field(
        default=None,
        description="Sequential steps to execute to implement this change.",
    )
    justification: Optional[str] = Field(
        default=None,
        description="Benefits of implementing this change and the impact if this change is not implemented.",
    )
    knowledge: Optional[bool] = Field(
        False,
        description="Flag that indicates whether there are any knowledge base (KB) articles associated with the "
                    "change request.",
    )
    location: Optional[str] = Field(
        default=None,
        description="Sys_id and name of the location of the equipment referenced in the change request.",
    )
    made_sla: Optional[bool] = Field(
        default=None,
        description="No longer used. Flag that indicates whether the change request was implemented in alignment with "
                    "the associated service level agreement.",
    )
    needs_attention: Optional[bool] = Field(
        False,
        description="Flag that indicates whether the change request needs attention.",
    )
    number: Optional[str] = Field(
        default=None,
        description="Change number assigned to the change request by the system.",
    )
    on_hold: Optional[bool] = Field(
        False,
        description="Flag that indicates whether the change request is currently on hold.",
    )
    on_hold_reason: Optional[str] = Field(
        default=None,
        description="If the on_hold parameter is 'true', description of the reason why the change request is being "
                    "held up.",
    )
    on_hold_task: Optional[List[str]] = Field(
        default=None,
        description="If the on_hold parameter is 'true', list of the sys_ids of the tasks that must be completed "
                    "before the hold is released.",
    )
    opened_at: Optional[str] = Field(
        default=None, description="Date and time that the change release was created."
    )
    opened_by: Optional[str] = Field(
        default=None,
        description="Sys_id and name of the user that created the change release.",
    )
    order: Optional[int] = Field(
        default=None,
        description="Not used by Change Management. Optional numeric field by which to order records.",
    )
    outside_maintenance_schedule: Optional[bool] = Field(
        False,
        description="Flag that indicates whether maintenance by an outside company has been scheduled for the change "
                    "request.",
    )
    parent: Optional[str] = Field(
        default=None,
        description="Sys_id and name of the parent task to this change request, if any.",
    )
    phase: Optional[str] = Field(
        default=None, description="Current phase of the change request."
    )
    phase_state: Optional[str] = Field(
        default=None,
        description="Change_phase records that should be created for a change.",
    )
    priority: Optional[int] = Field(4, description="Priority of the change request.")
    production_system: Optional[bool] = Field(
        False,
        description="Flag that indicates whether the change request is for a ServiceNow instance that is in a "
                    "production environment.",
    )
    reason: Optional[str] = Field(
        default=None, description="Description of why the change request was initiated."
    )
    reassignment_count: Optional[int] = Field(
        default=None,
        description="Number of times that the change request has been reassigned to a new owner.",
    )
    rejection_goto: Optional[str] = Field(
        default=None,
        description="Sys_id of the task to perform if the change request is rejected.",
    )
    requested_by: Optional[str] = Field(
        default=None, description="Sys_id of the user that requested the change."
    )
    requested_by_date: Optional[str] = Field(
        default=None,
        description="Date and time when the change is requested to be implemented by.",
    )
    review_comments: Optional[str] = Field(
        default=None,
        description="Comments entered when the change request was reviewed.",
    )
    review_date: Optional[str] = Field(
        default=None, description="Date that the change request was reviewed."
    )
    review_status: Optional[str] = Field(
        default=None,
        description="Current status of the requested change request review.",
    )
    risk: Optional[int] = Field(
        default=None, description="Level of risk associated with the change request."
    )
    risk_impact_analysis: Optional[str] = Field(
        default=None,
        description="Description of the risk and analysis of implementing the change request.",
    )
    route_reason: Optional[int] = Field(
        default=None, description="Reason that the change request was transferred."
    )
    scope: Optional[int] = Field(
        default=None, description="Size of the change request."
    )
    service_offering: Optional[str] = Field(
        default=None,
        description="Sys_id of the service offering associated with the change request.",
    )
    short_description: Optional[str] = Field(
        default=None, description="Description of the change request."
    )
    skills: Optional[List[str]] = Field(
        default=None,
        description="List of the sys_ids of all of the skills required to implement the change request.",
    )
    sla_due: Optional[str] = Field(
        default=None,
        description="Date and time that the change request must be completed based on the associated service level "
                    "agreement.",
    )
    sn_esign_document: Optional[str] = Field(
        default=None,
        description="Sys_id of any E-signed document attached to the change request.",
    )
    sn_esign_esignature_configuration: Optional[str] = Field(
        default=None,
        description="Sys_id of the E-signed signature template used for the associated document.",
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Date and time that the change request is planned to start implementation.",
    )
    state: Optional[int] = Field(1, description="Current state of the change request.")
    std_change_producer_version: Optional[str] = Field(
        default=None,
        description="Sys_id of the record producer and change proposal associated with the change request.",
    )
    sys_class_name: Optional[str] = Field(
        default=None,
        description="Name of the table in which the change request is located.",
    )
    sys_created_by: Optional[str] = Field(
        default=None,
        description="Name of the user that initially created the change request.",
    )
    sys_created_on: Optional[str] = Field(
        default=None,
        description="Date and time that the associated change request record was originally created.",
    )
    sys_domain: Optional[str] = Field(
        default=None,
        description="Name of the domain to which the change module record is associated.",
    )
    sys_domain_path: Optional[str] = Field(
        default=None,
        description="Domain path in which the associated change module record resides.",
    )
    sys_id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the associated change request record.",
    )
    sys_mod_count: Optional[int] = Field(
        default=None,
        description="Number of updates to the case since it was initially created.",
    )
    sys_updated_by: Optional[str] = Field(
        default=None, description="Person that last updated the case."
    )
    sys_updated_on: Optional[str] = Field(
        default=None, description="Date and time when the case was last updated."
    )
    task_effective_number: Optional[str] = Field(
        default=None, description="Universal request number."
    )
    task_for: Optional[str] = Field(
        default=None, description="Sys_id of the user that the task was created for."
    )
    test_plan: Optional[str] = Field(
        default=None,
        description="Description of the associated test plan for the change.",
    )
    time_worked: Optional[str] = Field(
        default=None, description="Total amount of time worked on the change request."
    )
    type: Optional[str] = Field(default=None, description="Change request type.")
    unauthorized: Optional[bool] = Field(
        default=None,
        description="Flag that indicates whether the change request is unauthorized.",
    )
    universal_request: Optional[str] = Field(
        default=None,
        description="Sys_id of the Parent Universal request to which this change request is a part of.",
    )
    upon_approval: Optional[str] = Field(
        default=None, description="Action to take if the change request is approved."
    )
    upon_reject: Optional[str] = Field(
        default=None, description="Action to take if the change request is rejected."
    )
    urgency: Optional[int] = Field(
        default=None, description="Urgency of the change request."
    )
    user_input: Optional[str] = Field(
        default=None, description="Additional user input."
    )
    variables: Optional[str] = Field(
        default=None,
        description="Name-value pairs of variables associated with the change request.",
    )
    watch_list: Optional[List[str]] = Field(
        default=None,
        description="List of sys_ids of the users who receive notifications about this change request.",
    )
    wf_activity: Optional[str] = Field(
        default=None,
        description="Sys_id of the workflow activity record associated with the change request.",
    )
    work_end: Optional[str] = Field(
        default=None, description="Date and time work ended on the change request."
    )
    work_notes: Optional[str] = Field(
        default=None,
        description="Information about how to resolve the change request, or steps taken to resolve it.",
    )
    work_notes_list: Optional[List[str]] = Field(
        default=None,
        description="List of sys_ids of the internal users who receive notifications about this change request when "
                    "work notes are added.",
    )
    work_start: Optional[str] = Field(
        default=None,
        description="Date and time that work started on the change request.",
    )


class ChangeRequests(BaseModel):
    type: str = Field("ChangeRequests")
    __hash__ = object.__hash__
    result: List[ChangeRequest] = Field(
        default=None,
        description="List containing one or more change request record objects.",
    )


class Task(BaseModel):
    type: str = Field("Task")
    __hash__ = object.__hash__
    sys_id: Optional[FieldValue] = Field(
        default=None, description="Sys_id information for the change request task."
    )
    parent: Optional[FieldValue] = Field(
        default=None,
        description="Information for the change request associated to the task.",
    )
    short_description: Optional[FieldValue] = Field(
        default=None, description="Short description of the change request task."
    )
    additional_fields: Optional[Dict[str, FieldValue]] = Field(
        default=None,
        description="All other name-value pairs for the identified change request task.",
    )


class Tasks(BaseModel):
    type: str = Field("Tasks")
    __hash__ = object.__hash__
    result: Optional[Union[Dict, List[Task], List]] = Field(
        default=None,
        description="List of records with their associated fields and values.",
    )


class ConfigurationItem(BaseModel):
    type: str = Field("ConfigurationItem")
    __hash__ = object.__hash__
    sys_id: Optional[Union[FieldValue, str]] = None
    ci_item: Optional[Union[FieldValue, str]] = None
    cmdb_ci_service: Optional[Union[FieldValue, str]] = None
    record_fields: Optional[Dict] = None


class ConfigurationItems(BaseModel):
    type: str = Field("ConfigurationItems")
    __hash__ = object.__hash__
    result: List[ConfigurationItem] = None


class ConditionDetail(BaseModel):
    __hash__ = object.__hash__
    description: Optional[str] = Field(
        default=None, description="Description of the condition."
    )
    name: Optional[str] = Field(default=None, description="Name of the condition.")
    sys_id: Optional[str] = Field(default=None, description="Sys_id of the condition.")


class Condition(BaseModel):
    __hash__ = object.__hash__
    condition: Optional[ConditionDetail] = Field(
        default=None, description="Values of a specific condition."
    )
    passed: Optional[bool] = Field(
        default=None,
        description="Flag that indicates whether the change request met the associated condition.",
    )


class StateTransition(BaseModel):
    __hash__ = object.__hash__
    sys_id: Optional[str] = Field(
        default=None, description="Sys_id of the transition state."
    )
    display_value: Optional[str] = Field(
        default=None, description="Displayed description of the state."
    )
    from_state: Optional[str] = Field(
        default=None,
        description="Value of the state that the change request is transitioning from.",
    )
    to_state: Optional[str] = Field(
        default=None,
        description="Value of the state that the change request is transitioning to.",
    )
    transition_available: Optional[bool] = Field(
        default=None,
        description="Flag that indicates whether the change request can transition from its current state to this "
                    "state.",
    )
    automatic_transition: Optional[bool] = Field(
        default=None,
        description="Flag that indicates whether to automatically transition to this state.",
    )
    conditions: Optional[List[Condition]] = Field(
        default=None, description="List of the conditions associated with the state."
    )


class State(BaseModel):
    type: str = Field("State")
    __hash__ = object.__hash__
    available_states: Optional[List[str]] = Field(
        default=None,
        description="Values for the states that are available for the specified change request, including the current "
                    "state.",
    )
    state_transitions: Optional[Union[List, List[List[StateTransition]]]] = Field(
        default=None,
        description='Information on what is required to transition to each available state. Each distinct available '
                    '"to state" is in its own Array with each differing set of conditions for that to state being in '
                    'its own Object.',
    )
    state_label: Optional[Dict] = Field(
        default=None,
        description="Key-value pairs that associate labels with the available states.",
    )


class States(BaseModel):
    type: str = Field("States")
    __hash__ = object.__hash__
    states: Optional[List[State]] = Field(default=None, description="List of States")


class Item(BaseModel):
    __hash__ = object.__hash__
    className: Optional[str] = Field(
        default=None, description="Name of the class that contains the CI."
    )
    values: Optional[FieldValue] = Field(
        default=None, description="Information to use to locate an associated CI."
    )


class Relation(BaseModel):
    __hash__ = object.__hash__
    parent: Optional[str] = Field(
        default=None, description="Name of a parent CI related to the CI."
    )
    child: Optional[str] = Field(
        default=None, description="Name of a child CI related to the CI."
    )


class Attribute(BaseModel):
    __hash__ = object.__hash__
    is_inherited: Optional[str] = Field(
        default=None, description="Indicates if the attribute is inherited."
    )
    is_mandatory: Optional[str] = Field(
        default=None, description="Indicates if the attribute is mandatory."
    )
    is_read_only: Optional[str] = Field(
        default=None, description="Indicates if the attribute is read-only."
    )
    default_value: Optional[Any] = Field(
        default=None, description="Default value of the attribute."
    )
    label: Optional[str] = Field(default=None, description="Label of the attribute.")
    type: Optional[str] = Field(default=None, description="Type of the attribute.")
    element: Optional[str] = Field(
        default=None, description="Element name of the attribute."
    )
    max_length: Optional[str] = Field(
        default=None, description="Max length of the attribute."
    )
    is_display: Optional[str] = Field(
        default=None, description="Indicates if the attribute is a display field."
    )


class RelationshipRule(BaseModel):
    __hash__ = object.__hash__
    parent: Optional[str] = Field(
        default=None, description="Parent class of the relationship."
    )
    relation_type: Optional[str] = Field(
        default=None, description="Type of the relationship."
    )
    child: Optional[str] = Field(
        default=None, description="Child class of the relationship."
    )


class RelatedRule(BaseModel):
    __hash__ = object.__hash__
    condition: Optional[str] = Field(
        default=None, description="Condition for the related rule."
    )
    exact_count_match: Optional[bool] = Field(
        default=None, description="Indicates if exact count match is required."
    )
    referenced_field: Optional[str] = Field(
        default=None, description="Referenced field for the related rule."
    )
    active: Optional[bool] = Field(
        default=None, description="Indicates if the rule is active."
    )
    attributes: Optional[str] = Field(
        default=None, description="Attributes associated with the rule."
    )
    allow_fallback: Optional[bool] = Field(
        default=None, description="Indicates if fallback is allowed."
    )
    table: Optional[str] = Field(
        default=None, description="Table name for the related rule."
    )
    order: Optional[int] = Field(default=None, description="Order of the rule.")
    allow_null_attribute: Optional[bool] = Field(
        default=None, description="Indicates if null attributes are allowed."
    )


class IdentificationRule(BaseModel):
    __hash__ = object.__hash__
    related_rules: Optional[List[RelatedRule]] = Field(
        default=None, description="List of related rules."
    )
    applies_to: Optional[str] = Field(
        default=None, description="Class to which the identification rules apply."
    )
    identifiers: Optional[List[RelatedRule]] = Field(
        default=None, description="List of identifiers for the class."
    )
    name: Optional[str] = Field(
        default=None, description="Name of the identification rule."
    )
    description: Optional[str] = Field(
        default=None, description="Description of the identification rule."
    )
    active: Optional[bool] = Field(
        default=None, description="Indicates if the identification rule is active."
    )
    is_independent: Optional[bool] = Field(
        default=None, description="Indicates if the rule is independent."
    )


class Link(BaseModel):
    __hash__ = object.__hash__
    id: Optional[str] = Field(
        default=None, description="Unique identifier of the results information."
    )
    url: Optional[str] = Field(
        default=None,
        description="URL to retrieve a list of records that violated the checks.",
    )
    label: Optional[str] = Field(
        default=None,
        description="Additional information about the instance scan findings.",
    )


class Rollback(BaseModel):
    __hash__ = object.__hash__
    id: Optional[str] = Field(
        default=None,
        description="Sys_id of the rollback details for the installed packages.",
    )


class Links(BaseModel):
    __hash__ = object.__hash__
    findings: Optional[Link] = Field(
        default=None,
        description="Object that contains information about the instance scan findings.",
    )
    progress: Optional[Link] = Field(
        default=None, description="Describes the progress link information."
    )
    results: Optional[Link] = Field(default=None, description="Results information.")
    source: Optional[Link] = Field(default=None, description="Source information.")
    stash: Optional[Link] = Field(
        default=None, description="Information about the stash."
    )
    rollback: Optional[Rollback] = Field(
        default=None, description="Describes the batch install rollback information."
    )


class TestSuiteResults(BaseModel):
    __hash__ = object.__hash__
    child_suite_results: Optional[List] = Field(
        default=[], description="Results of nested test suites."
    )
    error: Optional[str] = Field(default=None, description="Error message.")


class CICD(BaseModel):
    type: str = Field("CICD")
    error: Optional[str] = Field(default=None, description="Error message.")
    links: Optional[Links] = Field(
        default=None, description="All links and sys_ids associated with the response."
    )
    percent_complete: Optional[float] = Field(
        default=None, description="Percentage of the request that is complete."
    )
    status: Optional[str] = Field(default=None, description="Numeric execution state.")
    status_detail: Optional[str] = Field(
        default=None, description="Additional information about the current state."
    )
    status_label: Optional[str] = Field(
        default=None, description="Execution state description."
    )
    status_message: Optional[str] = Field(
        default=None, description="Additional information on why the operation failed."
    )
    rolledup_test_error_count: Optional[int] = Field(
        default=None, description="Number of tests with errors."
    )
    rolledup_test_failure_count: Optional[int] = Field(
        default=None, description="Number of tests that failed."
    )
    rolledup_test_skip_count: Optional[int] = Field(
        default=None, description="Number of tests that were skipped."
    )
    rolledup_test_success_count: Optional[int] = Field(
        default=None, description="Number of tests that ran successfully."
    )
    test_suite_duration: Optional[str] = Field(
        default=None,
        description="Amount of time that it took to execute the test suite.",
    )
    test_suite_name: Optional[str] = Field(
        default=None, description="Name of the test suite."
    )
    test_suite_status: Optional[str] = Field(
        default=None, description="State of the test suite."
    )
    rollback_version: Optional[str] = Field(
        default=None, description="Version to rollback the application"
    )

    @property
    def is_successful(self):
        return self.status == "2" and self.test_suite_status == "success"


class CMDB(BaseModel):
    type: str = Field("CMDB")
    __hash__ = object.__hash__
    icon_url: Optional[str] = Field(default=None, description="Class icon URL.")
    is_extendable: Optional[bool] = Field(
        default=None, description="Indicates if the class can be extended."
    )
    parent: Optional[str] = Field(default=None, description="Parent class.")
    children: Optional[List[str]] = Field(
        default=None, description="List of classes extended from the specified class."
    )
    name: Optional[str] = Field(default=None, description="Table/class name.")
    icon: Optional[str] = Field(default=None, description="Class icon sys_id.")
    attributes: Optional[List[Attribute]] = Field(
        default=None, description="Available fields in the specified class table."
    )
    relationship_rules: Optional[List[RelationshipRule]] = Field(
        default=None,
        description="Relationships between the specified class and other classes in the CMDB.",
    )
    label: Optional[str] = Field(
        default=None, description="Specified class display name."
    )
    identification_rules: Optional[IdentificationRule] = Field(
        default=None,
        description="Attributes associated with the configuration item identification rules for the specified class.",
    )
    items: Optional[List[Item]] = Field(
        default=None, description="CIs within the application service."
    )
    relations: Optional[List[Relation]] = Field(
        default=None, description="Relationship data for associated CIs."
    )


class ServiceRelation(BaseModel):
    __hash__ = object.__hash__
    parent: Optional[str] = Field(
        default=None, description="Name of a parent CI related to the CI."
    )
    child: Optional[str] = Field(
        default=None, description="Name of a child CI related to the CI."
    )


class Service(BaseModel):
    __hash__ = object.__hash__
    name: Optional[str] = Field(
        default=None, description="Name of the application service."
    )
    url: Optional[str] = Field(
        default=None, description="Relative path to the application service."
    )
    service_relations: Optional[List[ServiceRelation]] = Field(
        default=None,
        description="Hierarchy data for the CIs within the application service.",
    )


class ApplicationService(BaseModel):
    __hash__ = object.__hash__
    cmdb: Optional[CMDB] = Field(
        default=None,
        description="List of objects that describe the CIs associated with the specified application service.",
    )
    service: Optional[Service] = Field(
        default=None, description="List of services related to the identified service."
    )


class Token(BaseModel):
    type: str = Field("Token")
    __hash__ = object.__hash__
    scope: Optional[str] = Field(
        default=None,
        description="Amount of access granted by the access token. The scope is always useraccount, meaning that the "
                    "access token has the same rights as the user account that authorized the token. For example, "
                    "if Abel Tuter authorizes an application by providing login credentials, then the resulting "
                    "access token grants the token bearer the same access privileges as Abel Tuter.",
    )
    token_type: Optional[str] = Field(
        default=None,
        description="Type of token issued by the request as defined in the OAuth RFC. The token type is always "
                    "Bearer, meaning that anyone in possession of the access token can access a protected resource "
                    "without providing a cryptographic key.",
    )
    expires_in: Optional[int] = Field(
        default=None, description="Lifespan of the access token in seconds."
    )
    refresh_token: Optional[str] = Field(
        default=None, description="String value of the refresh token."
    )
    access_token: Optional[str] = Field(
        default=None,
        description="String value of the access token. Access requests made within the access token expiration time "
                    "always return the current access token.",
    )
    format: Optional[str] = Field(
        default=None, description="Output Format type. Always JSON"
    )


class Response(BaseModel):
    result: Optional[Union[
        Annotated[BatchInstallResult],
        Annotated[CICD],
        Annotated[ChangeRequest],
        Annotated[ChangeRequests],
        Annotated[CMDB],
        Annotated[Task],
        Annotated[Tasks],
        Annotated[ConfigurationItem],
        Annotated[ConfigurationItems],
        Annotated[State],
        Annotated[States],
        Annotated[Token],
    ]] = Field(default=None, description="Result containing available responses.")
    cmdb: Optional[CMDB] = Field(
        default=None,
        description="List of objects that describe the CIs associated with the specified application service.",
    )
    service: Optional[Service] = Field(
        default=None, description="List of services related to the identified service."
    )
    error: Optional[Any] = None

    @model_validator(mode="before")
    def determine_result_type(cls, values):
        result = values.get("result")
        if result:
            try:
                BatchInstallResult.model_validate(**result)
                values["result"] = BatchInstallResult(**result)
            except Exception as e:
                pass
            try:
                ChangeRequest.model_validate(**result)
                values["result"] = ChangeRequest(**result)
            except Exception as e:
                pass
            try:
                ChangeRequests.model_validate(**result)
                values["result"] = ChangeRequests(**result)
            except Exception as e:
                pass
            try:
                CICD.model_validate(**result)
                values["result"] = CICD(**result)
            except Exception as e:
                pass
            try:
                CMDB.model_validate(**result)
                values["result"] = CMDB(**result)
            except Exception as e:
                pass
            try:
                Task.model_validate(**result)
                values["result"] = Task(**result)
            except Exception as e:
                pass
            try:
                Tasks.model_validate(**result)
                values["result"] = Tasks(**result)
            except Exception as e:
                pass
            try:
                ConfigurationItem.model_validate(**result)
                values["result"] = ConfigurationItem(**result)
            except Exception as e:
                pass
            try:
                ConfigurationItems.model_validate(**result)
                values["result"] = ConfigurationItems(**result)
            except Exception as e:
                pass
            try:
                State.model_validate(**result)
                values["result"] = State(**result)
            except Exception as e:
                pass
            try:
                States.model_validate(**result)
                values["result"] = States(**result)
            except Exception as e:
                pass
            try:
                Token.model_validate(**result)
                values["result"] = Token(**result)
            except Exception as e:
                pass
        return values
