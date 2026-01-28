from typing import Union, List, Dict, Optional, Any, TypeVar, Generic

import requests
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)
from servicenow_api.exceptions import (
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
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)

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
        if value is None:
            return None
        return str(value).lower()

    @field_validator("mode")
    def validate_mode(cls, v):
        if v is not None and v in ["full", "shallow"]:
            raise ValueError("Invalid optional params")
        return v

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.mode:
            self.api_parameters["mode"] = self.mode


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


class CMDBInstanceModel(BaseModel):
    """
    Pydantic model representing a CMDB Instance operation.

    Attributes:
    - className (Optional[str]): CMDB class name.
    - sys_id (Optional[str]): Sys_id of the CI.
    - rel_sys_id (Optional[str]): Sys_id of the relation to remove.
    - sysparm_limit (Optional[Union[str, int]]): Maximum number of records to return.
    - sysparm_offset (Optional[Union[str, int]]): Starting record index.
    - sysparm_query (Optional[str]): Encoded query.
    - attributes (Optional[Dict]): Data attributes for CI record.
    - inbound_relations (Optional[List[Dict]]): List of inbound relations.
    - outbound_relations (Optional[List[Dict]]): List of outbound relations.
    - source (Optional[str]): Discovery source.
    - api_parameters (Dict): API parameters.
    - data (Dict): Payload data.
    """

    model_config = ConfigDict(validate_assignment=True)
    className: Optional[str] = None
    sys_id: Optional[str] = None
    rel_sys_id: Optional[str] = None
    sysparm_limit: Optional[Union[str, int]] = None
    sysparm_offset: Optional[Union[str, int]] = None
    sysparm_query: Optional[str] = None
    attributes: Optional[Dict] = None
    inbound_relations: Optional[List[Dict]] = None
    outbound_relations: Optional[List[Dict]] = None
    source: Optional[str] = None
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)
    data: Optional[Dict] = None

    @field_validator(
        "className",
        "sys_id",
        "rel_sys_id",
        "sysparm_query",
        "source",
    )
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    def model_post_init(self, __context):
        """
        Build the API parameters and data payload
        """
        self.api_parameters = {}
        if self.sysparm_limit:
            self.api_parameters["sysparm_limit"] = self.sysparm_limit
        if self.sysparm_offset:
            self.api_parameters["sysparm_offset"] = self.sysparm_offset
        if self.sysparm_query:
            self.api_parameters["sysparm_query"] = self.sysparm_query

        data = {}
        if self.attributes:
            data["attributes"] = self.attributes
        if self.inbound_relations:
            data["inbound_relations"] = self.inbound_relations
        if self.outbound_relations:
            data["outbound_relations"] = self.outbound_relations
        if self.source:
            data["source"] = self.source

        # Only set data if there are fields to send
        if data:
            self.data = data
        else:
            self.data = None


class CMDBIngestModel(BaseModel):
    """
    Pydantic model representing a CMDB Data Ingestion operation.

    Attributes:
    - data_source_sys_id (Optional[str]): Sys_id of the data source record.
    - records (Optional[List[Dict]]): Array of objects to ingest.
    - data (Dict): Payload data.
    """

    model_config = ConfigDict(validate_assignment=True)
    data_source_sys_id: Optional[str] = None
    records: Optional[List[Dict]] = None
    data: Optional[Dict] = None

    @field_validator("data_source_sys_id")
    def validate_string_parameters(cls, v):
        if v is not None and not isinstance(v, str):
            raise ValueError("Invalid optional params")
        return v

    @field_validator("records")
    def validate_list_parameters(cls, v):
        if v is not None and not isinstance(v, list):
            raise ValueError("Invalid optional params")
        return v

    def model_post_init(self, __context):
        """
        Build the data payload
        """
        self.data = {}
        if self.records:
            self.data["records"] = self.records


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
    - target_table (Optional[str]): Target table for scan.
    - target_sys_id (Optional[str]): Target sys_id for scan.
    - update_set_id (Optional[str]): Sys_id of the update set.
    - update_source_id (Optional[str]): Sys_id of the remote instance record.
    - update_source_instance_id (Optional[str]): Instance ID of the remote instance.
    - auto_preview (Optional[bool]): Flag indicating whether to automatically preview the update set after retrieval.
    - cleanup_retrieved (Optional[bool]): Flag indicating whether to remove the existing retrieved update set.
    - remote_update_set_id (Optional[str]): Sys_id of the remote update set.
    - remote_update_set_ids (Optional[List[str]]): List of sys_ids for remote update sets.
    - force_commit (Optional[bool]): Flag indicating whether to force commit the update set.
    - rollback_installs (Optional[bool]): Flag indicating whether to rollback installations.
    - update_set_name (Optional[str]): Name to give the update set.
    - description (Optional[str]): Description of the update set.
    - sys_id (Optional[str]): General sys_id, used in various contexts.
    - api_parameters (Dict): Dictionary containing API parameters.
    - data (Dict): Dictionary containing data.

    Note:
    The class includes field_validator functions for specific attribute validations.
    """

    sys_id: Optional[str] = None
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
    target_table: Optional[str] = None
    target_sys_id: Optional[str] = None
    update_set_id: Optional[str] = None
    update_source_id: Optional[str] = None
    update_source_instance_id: Optional[str] = None
    auto_preview: Optional[bool] = None
    cleanup_retrieved: Optional[bool] = None
    remote_update_set_id: Optional[str] = None
    remote_update_set_ids: Optional[List[str]] = None
    force_commit: Optional[bool] = None
    rollback_installs: Optional[bool] = None
    update_set_name: Optional[str] = None
    description: Optional[str] = None
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)
    data: Optional[Dict] = None

    @field_validator(
        "result_id",
        "progress_id",
        "rollback_id",
        "name",
        "notes",
        "packages",
        "update_set_id",
        "update_source_id",
        "update_source_instance_id",
        "remote_update_set_id",
        "update_set_name",
        "description",
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

    @field_validator("app_scope_sys_ids", "remote_update_set_ids")
    def validate_list_parameters(cls, v):
        """
        Validate specific list parameters to ensure they are lists.

        Args:
        - v: The value of the parameter.

        Returns:
        - list: The validated parameter value as a list.

        Raises:
        - ValueError: If the parameter is provided and not a list, str, or int.
        """
        if v is not None and not isinstance(v, list):
            if isinstance(v, str) or isinstance(v, int):
                return [str(v)]
            else:
                raise ValueError("Invalid optional params")
        return v

    @field_validator("browser_name")
    def convert_to_lowercase(cls, value):
        """
        Convert specified parameters to lowercase.

        Args:
        - value: The value of the parameter.

        Returns:
        - str: The value converted to lowercase.
        """
        if value is not None:
            return str(value).lower()
        return value

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
    def build_data(cls, values):
        """
        Build API parameters.

        Args:
        - values: Dictionary of values.

        Returns:
        - The constructed API parameters string.

        Raises:
        - None.
        """

        data = {}

        if "name" in values:
            data["name"] = values.get("name")
        if "packages" in values:
            data["packages"] = values.get("packages")
        if "app_scope_sys_ids" in values:
            data["app_scope_sys_ids"] = values.get("app_scope_sys_ids")
        if "force_commit" in values and values["force_commit"] is not None:
            data["force_commit"] = str(values["force_commit"]).lower()

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        if "data" not in values or values["data"] is None:
            values["data"] = data
        return values

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.sys_id:
            self.api_parameters["sys_id"] = self.sys_id
        if self.scope:
            self.api_parameters["scope"] = self.scope
        if self.auto_upgrade_base_app:
            self.api_parameters["auto_upgrade_base_app"] = self.auto_upgrade_base_app
        if self.base_app_version:
            self.api_parameters["base_app_version"] = self.base_app_version
        if self.version:
            self.api_parameters["version"] = self.version
        if self.dev_notes:
            self.api_parameters["dev_notes"] = self.dev_notes
        if self.target_table:
            self.api_parameters["target_table"] = self.target_table
        if self.target_sys_id:
            self.api_parameters["target_sys_id"] = self.target_sys_id
        if self.app_sys_id:
            self.api_parameters["app_sys_id"] = self.app_sys_id
        if self.test_suite_sys_id:
            self.api_parameters["test_suite_sys_id"] = self.test_suite_sys_id
        if self.test_suite_name:
            self.api_parameters["test_suite_name"] = self.test_suite_name
        if self.branch_name:
            self.api_parameters["branch_name"] = self.branch_name
        if self.credential_sys_id:
            self.api_parameters["credential_sys_id"] = self.credential_sys_id
        if self.mid_server_sys_id:
            self.api_parameters["mid_server_sys_id"] = self.mid_server_sys_id
        if self.browser_name:
            self.api_parameters["browser_name"] = self.browser_name
        if self.browser_version:
            self.api_parameters["browser_version"] = self.browser_version
        if self.os_name:
            self.api_parameters["os_name"] = self.os_name
        if self.os_version:
            self.api_parameters["os_version"] = self.os_version
        if self.update_set_id:
            self.api_parameters["update_set_id"] = self.update_set_id
        if self.update_source_id:
            self.api_parameters["update_source_id"] = self.update_source_id
        if self.update_source_instance_id:
            self.api_parameters["update_source_instance_id"] = (
                self.update_source_instance_id
            )
        if self.auto_preview:
            self.api_parameters["auto_preview"] = self.auto_preview
        if self.cleanup_retrieved:
            self.api_parameters["cleanup_retrieved"] = self.cleanup_retrieved
        if self.remote_update_set_ids:
            self.api_parameters["remote_update_set_ids"] = ",".join(
                self.remote_update_set_ids
            )
        if self.rollback_installs:
            self.api_parameters["rollback_installs"] = self.rollback_installs
        if self.update_set_name:
            self.api_parameters["update_set_name"] = self.update_set_name
        if self.description:
            self.api_parameters["description"] = self.description


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
    - name_value_pairs (Optional[str]): String containing name-value pairs. &active=true&assigned_to=john.smith
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
    change_request_task_sys_id: Optional[str] = None
    state: Optional[str] = None
    cmdb_ci_sys_ids: Optional[List[str]] = None
    cmdb_ci_sys_id: Optional[str] = None
    task_sys_id: Optional[str] = None
    model_sys_id: Optional[str] = None
    association_type: Optional[str] = None
    refresh_impacted_services: Optional[bool] = None
    name_value_pairs: Optional[str] = None
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
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)
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
        if value is None:
            return None
        return str(value).lower()

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

    @model_validator(mode="before")
    def build_data(cls, values):
        """
        Build API parameters.

        Args:
        - values: Dictionary of values.

        Returns:
        - The constructed API parameters string.

        Raises:
        - None.
        """

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

        if "data" not in values or values["data"] is None:
            values["data"] = data
        return values

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.name_value_pairs:
            self.api_parameters["name_value_pairs"] = self.name_value_pairs
        if self.text_search:
            self.api_parameters["textSearch"] = self.text_search
        if self.sysparm_query:
            self.api_parameters["sysparm_query"] = self.sysparm_query
        if self.sysparm_limit:
            self.api_parameters["sysparm_limit"] = self.sysparm_limit
        if self.sysparm_offset:
            self.api_parameters["sysparm_offset"] = self.sysparm_offset


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
    name_value_pairs: Optional[str] = None
    sysparm_display_value: Optional[Union[str, bool]] = None
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
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)
    data: Optional[Dict] = Field(
        default=None, description="Table dictionary value to insert"
    )

    @field_validator("incident_id")
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
        if value is None:
            return None
        return str(value).lower()

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
        if v not in ["desktop", "mobile", "both", None]:
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
        if v not in [True, False, "all", "true", "false", None]:
            raise ParameterError
        return v

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.name_value_pairs:
            self.api_parameters["name_value_pairs"] = self.name_value_pairs
        if self.sysparm_display_value:
            self.api_parameters["sysparm_display_value"] = self.sysparm_display_value
        if self.sysparm_exclude_reference_link:
            self.api_parameters["sysparm_exclude_reference_link"] = (
                self.sysparm_exclude_reference_link
            )
        if self.sysparm_fields:
            self.api_parameters["sysparm_fields"] = self.sysparm_fields
        if self.sysparm_query:
            self.api_parameters["sysparm_query"] = self.sysparm_query
        if self.sysparm_query_category:
            self.api_parameters["sysparm_query_category"] = self.sysparm_query_category
        if self.sysparm_query_no_domain:
            self.api_parameters["sysparm_query_no_domain"] = (
                self.sysparm_query_no_domain
            )
        if self.sysparm_suppress_pagination_header:
            self.api_parameters["sysparm_suppress_pagination_header"] = (
                self.sysparm_suppress_pagination_header
            )
        if self.sysparm_limit:
            self.api_parameters["sysparm_limit"] = self.sysparm_limit
        if self.sysparm_no_count:
            self.api_parameters["sysparm_no_count"] = self.sysparm_no_count
        if self.sysparm_offset:
            self.api_parameters["sysparm_offset"] = self.sysparm_offset


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
    name_value_pairs: Optional[str] = None
    textSearch: Optional[str] = None
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.name_value_pairs:
            self.api_parameters["name_value_pairs"] = self.name_value_pairs
        if self.textSearch:
            self.api_parameters["textSearch"] = self.textSearch
        if self.sysparm_query:
            self.api_parameters["sysparm_query"] = self.sysparm_query
        if self.sysparm_limit:
            self.api_parameters["sysparm_limit"] = self.sysparm_limit
        if self.sysparm_offset:
            self.api_parameters["sysparm_offset"] = self.sysparm_offset
        if self.sysparm_search_id:
            self.api_parameters["sysparm_search_id"] = self.sysparm_search_id
        if self.sysparm_search_rank:
            self.api_parameters["sysparm_search_rank"] = self.sysparm_search_rank
        if self.sysparm_update_view:
            self.api_parameters["sysparm_update_view"] = self.sysparm_update_view


class TableModel(BaseModel):
    """
    Pydantic model representing a Table.

    Attributes:
    - table (str): Name of the table.
    - table_record_sys_id (Optional[str]): System identifier for the table record.
    - name_value_pairs (Optional[str]]): Dictionary containing name-value pairs.
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

    table: Optional[str] = None
    table_record_sys_id: Optional[str] = None
    name_value_pairs: Optional[str] = None
    sysparm_display_value: Optional[Union[str, bool]] = None
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
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)
    data: Optional[Dict] = Field(
        default=None, description="Table dictionary value to insert"
    )

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
        if value is None:
            return None
        return str(value).lower()

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
        if v not in ["desktop", "mobile", "both", None]:
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
        if v not in [True, False, "all", "true", "false", None]:
            raise ParameterError
        return v

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.name_value_pairs:
            self.api_parameters["name_value_pairs"] = self.name_value_pairs
        if self.sysparm_display_value:
            self.api_parameters["sysparm_display_value"] = self.sysparm_display_value
        if self.sysparm_exclude_reference_link:
            self.api_parameters["sysparm_exclude_reference_link"] = (
                self.sysparm_exclude_reference_link
            )
        if self.sysparm_fields:
            self.api_parameters["sysparm_fields"] = self.sysparm_fields
        if self.sysparm_query:
            self.api_parameters["sysparm_query"] = self.sysparm_query
        if self.sysparm_query_category:
            self.api_parameters["sysparm_query_category"] = self.sysparm_query_category
        if self.sysparm_query_no_domain:
            self.api_parameters["sysparm_query_no_domain"] = (
                self.sysparm_query_no_domain
            )
        if self.sysparm_suppress_pagination_header:
            self.api_parameters["sysparm_suppress_pagination_header"] = (
                self.sysparm_suppress_pagination_header
            )
        if self.sysparm_limit:
            self.api_parameters["sysparm_limit"] = self.sysparm_limit
        if self.sysparm_no_count:
            self.api_parameters["sysparm_no_count"] = self.sysparm_no_count
        if self.sysparm_offset:
            self.api_parameters["sysparm_offset"] = self.sysparm_offset


########################################################################################################################
#                                              Output Models                                                           #
########################################################################################################################
class FieldValue(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    value: Union[str, int] = Field(default=None, description="The value of the field.")
    display_value: str = Field(
        default=None, description="The display value of the field."
    )
    display_value_internal: Optional[str] = Field(
        default=None, description="Time for Display value interval"
    )


class ItemValue(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    sys_id: str = Field(default=None, description="Sys Id of the value")
    name: str = Field(default=None, description="Name of the value")


class BatchItem(BaseModel):
    model_config = ConfigDict(extra="allow")
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
    model_config = ConfigDict(extra="allow")
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
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="BatchInstallResult")
    error: Optional[str] = Field(default=None, description="Error message.")
    batch_items: Optional[List[BatchItem]] = Field(
        default=None,
        description="JSON array, where each object provides details of a "
        "package installation.",
    )
    batch_plan: Optional[BatchPlan] = Field(
        default=None, description="Describes the installation batch plan."
    )


class ConditionDetail(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    description: Optional[str] = Field(
        default=None, description="Description of the condition."
    )
    name: Optional[str] = Field(default=None, description="Name of the condition.")
    sys_id: Optional[str] = Field(default=None, description="Sys_id of the condition.")


class Condition(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    condition: Optional[ConditionDetail] = Field(
        default=None, description="Values of a specific condition."
    )
    passed: Optional[bool] = Field(
        default=None,
        description="Flag that indicates whether the change request met the associated condition.",
    )


class StateTransition(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    sys_id: str = Field(default=None, description="Sys_id of the transition state.")
    display_value: str = Field(
        default=None, description="Displayed description of the state."
    )
    from_state: str = Field(
        default=None,
        description="Value of the state that the change request is transitioning from.",
    )
    to_state: str = Field(
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


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    detail: Optional[str] = Field(
        None, description="Additional information about the error."
    )
    message: Optional[str] = Field(
        None, description="Message that identifies the error."
    )
    status: Optional[str] = Field(None, description="Status of the error.")


class Messages(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    errorMessages: Optional[List[str]] = Field(
        None, description="Error messages encountered while processing the request."
    )
    infoMessages: Optional[List[str]] = Field(
        None,
        description="Information messages encountered while processing the request.",
    )
    warningMessages: Optional[List[str]] = Field(
        None, description="Warning messages encountered while processing the request."
    )


class Worker(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Worker")
    link: Optional[str] = Field(None, description="Link for retrieving time slot data.")
    sysId: Optional[str] = Field(
        None, description="Sys_id of the worker associated with the change request."
    )


class State(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="State")
    available_states: List[str] = Field(
        default=None,
        description="Values for the states that are available for the specified change request, including the current "
        "state.",
    )
    state_transitions: List[List[StateTransition]] = Field(
        default=None,
        description="Information on what is required to transition to each available state. Each distinct available "
        '"to state" is in its own Array with each differing set of conditions for that to state being in '
        "its own Object.",
    )
    state_label: Dict = Field(
        default=None,
        description="Key-value pairs that associate labels with the available states.",
    )


class ChangeRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="ChangeRequest")
    action_status: Optional[Union[FieldValue, int]] = Field(
        default=None,
        description="Current action status of the associated change request.",
    )
    active: Optional[Union[FieldValue, str]] = Field(
        default=True,
        description="Flag that indicates whether the change request is active.",
    )
    activity_due: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time for which the associated case is expected to "
        "be completed.",
    )
    additional_assignee_list: Optional[Union[FieldValue, str, List[str]]] = Field(
        default=None,
        description="List of sys_ids of additional persons "
        "assigned to work on the change request.",
    )
    approval: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Type of approval process required."
    )
    approval_history: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Most recent approval history journal entry."
    )
    approval_set: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that the associated action was approved.",
    )
    assigned_to: Union[FieldValue, str] = Field(
        default=None, description="Sys_id of the user assigned to the change request."
    )
    assignment_group: Union[FieldValue, str] = Field(
        default=None, description="Sys_id of the group assigned to the change request."
    )
    backout_plan: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Description of the plan to execute if the change must be "
        "reversed.",
    )
    business_duration: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Length in scheduled work hours, work days, and work "
        "weeks that it took to complete the change.",
    )
    business_service: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the business service associated with the "
        "change request.",
    )
    cab_date: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Date on which the Change Advisory Board (CAB) meets."
    )
    cab_delegate: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the user that can substitute for the CAB manager "
        "during a CAB meeting.",
    )
    cab_recommendation: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Description of the CAB recommendations for the change request.",
    )
    cab_required: Optional[Union[FieldValue, bool]] = Field(
        False, description="Flag that indicates whether the CAB is required."
    )
    calendar_duration: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Not currently used by Change Management."
    )
    category: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Category of the change, for example hardware, network, or software.",
    )
    change_plan: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Activities and roles for managing and controlling the change request.",
    )
    chg_model: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the change model that the associated change request was based on.",
    )
    ci_class: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the change model that the associated change request was based on.",
    )
    closed_at: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that the associated change request was closed.",
    )
    closed_by: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Sys_id of the person that closed the change request."
    )
    close_code: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Code assigned to the change request when it was closed.",
    )
    close_notes: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Notes that the person entered when closing the change request.",
    )
    cmdb_ci: Union[FieldValue, str] = Field(
        default=None,
        description="Sys_id of the configuration item associated with the change request.",
    )
    comments: Optional[Union[FieldValue, str, List[str]]] = Field(
        default=None,
        description="List of customer-facing work notes entered in the associated change request.",
    )
    comments_and_work_notes: Optional[Union[FieldValue, str, List[str]]] = Field(
        default=None,
        description="List of both internal and customer-facing work notes entered for the associated change request.",
    )
    company: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the company associated with the change request.",
    )
    conflict_last_run: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that the conflict detection script was last run on the change request.",
    )
    conflict_status: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Current conflict status as detected by the conflict detection script.",
    )
    contact_type: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Method in which the change request was initially requested.",
    )
    contract: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the contract associated with the change request.",
    )
    correlation_display: Optional[Union[FieldValue, str]] = Field(
        default=None, description="User-friendly name for the correlation_id."
    )
    correlation_id: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Globally unique ID (GUID) of a matching change request record in a third-party system.",
    )
    delivery_plan: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="No longer in use. Sys_id of the delivery plan associated with the change request.",
    )
    delivery_task: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="No longer in use. Sys_id of the delivery task associated with the change request.",
    )
    description: Union[FieldValue, str] = Field(
        default=None, description="Detailed description of the change request."
    )
    due_date: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Task due date. Not used by change request process."
    )
    end_date: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time when the change request is to be completed.",
    )
    escalation: Optional[Union[FieldValue, int]] = Field(
        default=None, description="Current escalation level."
    )
    expected_start: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time when the task is to start. Not used by the change request process.",
    )
    follow_up: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time when a user followed-up with the person requesting the change request.",
    )
    group_list: Optional[Union[FieldValue, str, List[str]]] = Field(
        default=None,
        description="List of sys_ids and names of the groups associated with the change request.",
    )
    impact: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Impact on the change request will have on the customer.",
    )
    implementation_plan: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sequential steps to execute to implement this change.",
    )
    is_bulk: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Bulk change",
    )
    justification: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Benefits of implementing this change and the impact if this change is not implemented.",
    )
    knowledge: Optional[Union[FieldValue, str]] = Field(
        False,
        description="Flag that indicates whether there are any knowledge base (KB) articles associated with the "
        "change request.",
    )
    location: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id and name of the location of the equipment referenced in the change request.",
    )
    made_sla: Optional[Union[FieldValue, bool]] = Field(
        default=None,
        description="No longer used. Flag that indicates whether the change request was implemented in alignment with "
        "the associated service level agreement.",
    )
    needs_attention: Optional[Union[FieldValue, bool]] = Field(
        False,
        description="Flag that indicates whether the change request needs attention.",
    )
    number: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Change number assigned to the change request by the system.",
    )
    on_hold: Optional[Union[FieldValue, bool]] = Field(
        False,
        description="Flag that indicates whether the change request is currently on hold.",
    )
    on_hold_reason: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="If the on_hold parameter is 'true', description of the reason why the change request is being "
        "held up.",
    )
    on_hold_task: Optional[Union[FieldValue, str, List[str]]] = Field(
        default=None,
        description="If the on_hold parameter is 'true', list of the sys_ids of the tasks that must be completed "
        "before the hold is released.",
    )
    opened_at: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Date and time that the change release was created."
    )
    opened_by: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id and name of the user that created the change release.",
    )
    order: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Not used by Change Management. Optional numeric field by which to order records.",
    )
    outside_maintenance_schedule: Optional[Union[FieldValue, bool]] = Field(
        False,
        description="Flag that indicates whether maintenance by an outside company has been scheduled for the change "
        "request.",
    )
    parent: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id and name of the parent task to this change request, if any.",
    )
    phase: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Current phase of the change request."
    )
    phase_state: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Change_phase records that should be created for a change.",
    )
    priority: Optional[Union[FieldValue, int, str]] = Field(
        4, description="Priority of the change request."
    )
    production_system: Optional[Union[FieldValue, bool]] = Field(
        False,
        description="Flag that indicates whether the change request is for a ServiceNow instance that is in a "
        "production environment.",
    )
    proposed_change: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Proposed change reason"
    )
    reason: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Description of why the change request was initiated."
    )
    reassignment_count: Optional[Union[FieldValue, int]] = Field(
        default=None,
        description="Number of times that the change request has been reassigned to a new owner.",
    )
    rejection_goto: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the task to perform if the change request is rejected.",
    )
    requested_by: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Sys_id of the user that requested the change."
    )
    requested_by_date: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time when the change is requested to be implemented by.",
    )
    review_comments: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Comments entered when the change request was reviewed.",
    )
    review_date: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Date that the change request was reviewed."
    )
    review_status: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Current status of the requested change request review.",
    )
    risk: Optional[Union[FieldValue, int]] = Field(
        default=None, description="Level of risk associated with the change request."
    )
    risk_value: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Risk value associated with the change request."
    )
    risk_impact_analysis: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Description of the risk and analysis of implementing the change request.",
    )
    route_reason: Optional[Union[FieldValue, int]] = Field(
        default=None, description="Reason that the change request was transferred."
    )
    scope: Optional[Union[FieldValue, int]] = Field(
        default=None, description="Size of the change request."
    )
    service_offering: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the service offering associated with the change request.",
    )
    short_description: Union[FieldValue, str] = Field(
        default=None, description="Description of the change request."
    )
    skills: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="List of the sys_ids of all of the skills required to implement the change request.",
    )
    sla_due: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that the change request must be completed based on the associated service level "
        "agreement.",
    )
    sn_esign_document: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of any E-signed document attached to the change request.",
    )
    sn_esign_esignature_configuration: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the E-signed signature template used for the associated document.",
    )
    start_date: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that the change request is planned to start implementation.",
    )
    state: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Current state of the change request."
    )
    std_change_producer_version: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the record producer and change proposal associated with the change request.",
    )
    sys_class_name: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Name of the table in which the change request is located.",
    )
    sys_created_by: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Name of the user that initially created the change request.",
    )
    sys_created_on: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that the associated change request record was originally created.",
    )
    sys_domain: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Name of the domain to which the change module record is associated.",
    )
    sys_domain_path: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Domain path in which the associated change module record resides.",
    )
    sys_id: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Unique identifier of the associated change request record.",
    )
    sys_mod_count: Optional[Union[FieldValue, int]] = Field(
        default=None,
        description="Number of updates to the case since it was initially created.",
    )
    sys_tags: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Tags associated to the change."
    )
    sys_updated_by: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Person that last updated the case."
    )
    sys_updated_on: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Date and time when the case was last updated."
    )
    task_effective_number: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Universal request number."
    )
    task_for: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Sys_id of the user that the task was created for."
    )
    test_plan: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Description of the associated test plan for the change.",
    )
    time_worked: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Total amount of time worked on the change request."
    )
    type: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Change request type."
    )
    unauthorized: Optional[Union[FieldValue, bool]] = Field(
        default=None,
        description="Flag that indicates whether the change request is unauthorized.",
    )
    universal_request: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the Parent Universal request to which this change request is a part of.",
    )
    upon_approval: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Action to take if the change request is approved."
    )
    upon_reject: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Action to take if the change request is rejected."
    )
    urgency: Optional[Union[FieldValue, int]] = Field(
        default=None, description="Urgency of the change request."
    )
    user_input: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Additional user input."
    )
    variables: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Name-value pairs of variables associated with the change request.",
    )
    watch_list: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="List of sys_ids of the users who receive notifications about this change request.",
    )
    wf_activity: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Sys_id of the workflow activity record associated with the change request.",
    )
    work_end: Optional[Union[FieldValue, str]] = Field(
        default=None, description="Date and time work ended on the change request."
    )
    work_notes: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Information about how to resolve the change request, or steps taken to resolve it.",
    )
    work_notes_list: Optional[Union[FieldValue, List[str]]] = Field(
        default=None,
        description="List of sys_ids of the internal users who receive notifications about this change request when "
        "work notes are added.",
    )
    work_start: Optional[Union[FieldValue, str]] = Field(
        default=None,
        description="Date and time that work started on the change request.",
    )


class Task(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Task")
    sys_id: FieldValue = Field(
        default=None, description="Sys_id information for the change request task."
    )
    parent: FieldValue = Field(
        default=None,
        description="Information for the change request associated to the task.",
    )
    short_description: FieldValue = Field(
        default=None, description="Short description of the change request task."
    )
    active: Optional[bool] = Field(
        default=None,
        description="Specifies whether work is still being done on a task or whether the work for the task is complete.",
    )
    comments: Optional[str] = Field(
        default=None,
        description="Displays and allows the entry of comments about the task record.",
    )
    approval_history: Optional[str] = Field(
        default=None, description="Displays the history of approvals for the record."
    )
    assigned_to: Optional[FieldValue] = Field(
        default=None, description="Specifies the user assigned to complete the task."
    )
    sys_created_on: Optional[str] = Field(
        default=None,
        description="Displays the date and time when the task record was created.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Displays and allows the entry of a multi-line description of the work to be done.",
    )
    escalation: Optional[int] = Field(
        default=None,
        description="Indicates how long the task has been open, with states from Normal to Overdue.",
    )
    number: Optional[str] = Field(
        default=None, description="Displays an identifying number for each task record."
    )
    opened_at: Optional[str] = Field(
        default=None,
        description="Displays the date and time when a human opened the task record for the first time.",
    )
    priority: Optional[int] = Field(
        default=None,
        description="Specifies how high a priority the task should be for the assignee.",
    )
    state: Optional[int] = Field(
        default=None, description="Displays a choice list for status of the task."
    )
    sys_class_name: Optional[str] = Field(
        default=None,
        description="Specifies the type of task, which corresponds to the child class.",
    )
    time_worked: Optional[str] = Field(
        default=None,
        description="Displays a timer which measures how long a record is open in the form view.",
    )
    watch_list: Optional[List[FieldValue]] = Field(
        default=None,
        description="Specifies users who receive notifications when the record is updated.",
    )
    work_notes: Optional[str] = Field(
        default=None,
        description="Displays and allows the entry of comments viewable only by ITIL users.",
    )
    work_notes_list: Optional[List[FieldValue]] = Field(
        default=None,
        description="Specifies users who receive notifications when work notes are added to the record.",
    )


class ReferenceField(BaseModel):
    """
    Model for ServiceNow choice fields (e.g., state, priority).
    Handles dictionary structure with value, link, and optional display_value.
    """

    model_config = ConfigDict(extra="allow")
    value: Optional[Union[str, int]] = Field(
        default=None, description="Internal value of the choice"
    )
    link: Optional[str] = Field(
        default=None, description="API URL to the choice definition"
    )
    display_value: Optional[Union[str, int]] = Field(
        default=None,
        description="Human-readable label of the choice (when sysparm_display_value=true)",
    )


class Incident(BaseModel):
    model_config = ConfigDict(extra="allow")
    base_type: str = Field(default="Incident")
    __hash__ = object.__hash__
    sys_id: Optional[str] = Field(
        default=None, description="Unique identifier of the incident record"
    )
    number: Optional[str] = Field(
        default=None, description="Incident number (e.g., INC0012345)"
    )
    state: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="State of the incident (e.g., {value: '1', display_value: 'New'})",
    )
    priority: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Priority level (e.g., {value: '3', display_value: 'Moderate'})",
    )
    short_description: Optional[str] = Field(
        default=None, description="Brief description of the incident"
    )
    description: Optional[str] = Field(
        default=None, description="Detailed description of the incident"
    )
    impact: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Impact level (e.g., {value: '2', display_value: 'Medium'})",
    )
    urgency: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Urgency level (e.g., {value: '2', display_value: 'Medium'})",
    )
    category: Optional[str] = Field(
        default=None, description="Category of the incident (e.g., Hardware, Software)"
    )
    subcategory: Optional[str] = Field(
        default=None, description="Subcategory of the incident"
    )
    caller_id: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the caller (sys_user)"
    )
    assigned_to: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the assigned user (sys_user)"
    )
    assignment_group: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the assignment group (sys_user_group)"
    )
    opened_at: Optional[str] = Field(
        default=None, description="Timestamp when the incident was opened"
    )
    opened_by: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Reference to the user who opened the incident (sys_user)",
    )
    closed_at: Optional[str] = Field(
        default=None, description="Timestamp when the incident was closed"
    )
    close_code: Optional[str] = Field(
        default=None, description="Closure code (e.g., Resolved, Cancelled)"
    )
    close_notes: Optional[str] = Field(
        default=None, description="Notes provided upon incident closure"
    )
    incident_state: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Detailed incident state"
    )
    sys_created_on: Optional[str] = Field(
        default=None, description="Timestamp when the record was created"
    )
    sys_updated_on: Optional[str] = Field(
        default=None, description="Timestamp when the record was last updated"
    )
    sys_updated_by: Optional[str] = Field(
        default=None, description="User who last updated the record"
    )
    sys_created_by: Optional[str] = Field(
        default=None, description="User who created the record"
    )
    company: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the associated company (core_company)"
    )
    location: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the location (cmn_location)"
    )
    cmdb_ci: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Reference to the related configuration item (cmdb_ci)",
    )
    problem_id: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the related problem (problem)"
    )
    change_request: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Reference to the related change request (change_request)",
    )
    comments: Optional[str] = Field(
        default=None, description="Additional comments added to the incident"
    )
    work_notes: Optional[str] = Field(
        default=None, description="Work notes added to the incident"
    )
    active: Optional[bool] = Field(
        default=None, description="Whether the incident is active"
    )
    severity: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Severity level of the incident"
    )
    notify: Optional[str] = Field(default=None, description="Notification preference")
    contact_type: Optional[str] = Field(
        default=None, description="How the incident was reported (e.g., phone, email)"
    )
    parent: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Reference to the parent incident, if any (incident)"
    )
    escalation: Optional[Union[ReferenceField, str]] = Field(
        default=None, description="Escalation level of the incident"
    )
    sys_domain: Optional[Union[ReferenceField, str]] = Field(
        default=None,
        description="Reference to the domain for domain separation (sys_domain)",
    )
    sys_mod_count: Optional[int] = Field(
        default=None, description="Number of times the record was modified"
    )
    custom_fields: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dictionary for custom fields (e.g., u_custom_field)",
    )


class ConfigurationItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    base_type: str = Field(default="ConfigurationItem")
    __hash__ = object.__hash__
    sys_id: Optional[Union[FieldValue, str]] = None
    ci_item: Optional[Union[FieldValue, str]] = None
    cmdb_ci_service: Optional[Union[FieldValue, str]] = None
    record_fields: Optional[Dict] = None


class TimeSpan(BaseModel):
    model_config = ConfigDict(extra="allow")
    base_type: str = Field(default="TimeSpan")
    __hash__ = object.__hash__
    start: Optional[FieldValue] = Field(None, description="Start time of the span.")
    end: Optional[FieldValue] = Field(None, description="End time of the span.")


class Payload(BaseModel):
    model_config = ConfigDict(extra="allow")
    base_type: str = Field(default="Payload")
    __hash__ = object.__hash__
    spans: Optional[List[TimeSpan]] = Field(
        None, description="List of time spans associated with the payload."
    )


class Schedule(BaseModel):
    model_config = ConfigDict(extra="allow")
    base_type: str = Field(default="Schedule")
    __hash__ = object.__hash__
    error: Optional[ErrorDetail] = Field(
        None,
        description="Information on any errors encountered while processing the endpoint request.",
    )
    messages: Optional[Messages] = Field(None, description="Message information.")
    request: Optional[str] = Field(None, description="Original endpoint request.")
    state: Optional[FieldValue] = Field(
        None, description="Information on the current state of the worker."
    )
    type: Optional[str] = Field(
        None, description="Indicates the type of request. Valid value: schedule."
    )
    worker: Optional[Worker] = Field(
        None, description="Information about the associated worker."
    )
    payload: Optional[Payload] = Field(None, description="Payload information.")


class FieldDetail(BaseModel):
    display_value: Optional[str] = Field(
        None, description="Display value of the requested field."
    )
    label: Optional[str] = Field(
        None,
        description="Label representing the requested field. For example, Knowledge.",
    )
    name: Optional[str] = Field(
        None, description="Name of the requested field. Matches field name."
    )
    type: Optional[str] = Field(None, description="Data type of the requested field.")
    value: Optional[str] = Field(None, description="Value of the requested field.")


class Attachment(BaseModel):
    sys_id: Optional[str] = Field(
        None, description="Unique identifier for the attachment."
    )
    file_name: Optional[str] = Field(None, description="Name of the attached file.")
    size_bytes: Optional[int] = Field(None, description="Size of the file in bytes.")
    state: Optional[str] = Field(
        None, description="State of the attachment, e.g., available_conditionally."
    )


class ArticleFields(BaseModel):
    fields: Optional[Dict[str, FieldDetail]] = Field(
        None, description="Values of requested fields, if any."
    )


class Article(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Article")
    fields: Optional[Dict[str, FieldDetail]] = Field(
        None, description="Values of requested fields, if any."
    )
    link: Optional[str] = Field(None, description="Link to the article.")
    id: Optional[str] = Field(
        None,
        description="Knowledge article sys_id from the Knowledge [kb_knowledge] table.",
    )
    number: Optional[str] = Field(None, description="Knowledge article number.")
    rank: Optional[float] = Field(
        None, description="Search rank of article specific to this search."
    )
    score: Optional[float] = Field(
        None,
        description="Relevancy score, results sorted in descending order by score.",
    )
    snippet: Optional[str] = Field(
        None, description="Text showing a small portion of the knowledge article."
    )
    title: Optional[str] = Field(
        None, description="Short description or title of the knowledge article."
    )
    tags: Optional[List[str]] = Field(
        None, description="List of tags associated with the article."
    )
    content: Optional[str] = Field(None, description="Content the article.")
    template: Optional[bool] = Field(None, description="Template of article.")
    sys_id: Optional[str] = Field(None, description="Sys ID of article.")
    short_description: Optional[str] = Field(
        None, description="Short description of article."
    )
    display_attachments: Optional[bool] = Field(
        None, description="Display attachments flag."
    )
    attachments: Optional[List[Attachment]] = Field(
        None, description="List of attachments."
    )
    embedded_content: Optional[List] = Field(
        None, description="Additional embedded content."
    )


class Meta(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Meta")
    count: Optional[int] = Field(None, description="Number of available KB articles.")
    end: Optional[int] = Field(None, description="Ending index of the result set.")
    fields: Optional[str] = Field(None, description="Fields in the article.")
    filter: Optional[str] = Field(None, description="Filter used to acquire the data.")
    kb: Optional[str] = Field(
        None, description="List of knowledge base article sys_ids."
    )
    language: Optional[str] = Field(
        None,
        description="List of comma-separated languages of the KB articles that were requested.",
    )
    query: Optional[str] = Field(None, description="Specified request query.")
    start: Optional[int] = Field(None, description="Starting index of result set.")
    status: Optional[Dict[str, Any]] = Field(None, description="Status of the call.")
    ts_query_id: Optional[str] = Field(None, description="Sys_id of the query.")


class KnowledgeManagement(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="KnowledgeManagement")
    meta: Meta = Field(
        None, description="Meta information of the results and request parameters."
    )
    articles: List[Article] = Field(
        None, description="List of articles returned in response."
    )


class Item(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Item")
    className: Optional[str] = Field(
        default=None, description="Name of the class that contains the CI."
    )
    values: Optional[ItemValue] = Field(
        default=None, description="Information to use to locate an associated CI."
    )


class Relation(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Relation")
    parent: Optional[str] = Field(
        default=None, description="Name of a parent CI related to the CI."
    )
    child: Optional[str] = Field(
        default=None, description="Name of a child CI related to the CI."
    )


class Attribute(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Attribute")
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
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="RelationshipRule")
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
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="RelatedRule")
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
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="IdentificationRule")
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
    condition: Optional[str] = Field(
        None, description="Condition for the identification rule."
    )
    exact_count_match: Optional[bool] = Field(
        None, description="Indicates if an exact count match is required."
    )
    referenced_field: Optional[str] = Field(
        None, description="Referenced field for the identification rule."
    )
    attributes: Optional[str] = Field(
        None, description="Attributes involved in the identification rule."
    )
    allow_fallback: Optional[bool] = Field(
        None, description="Indicates if fallback is allowed."
    )
    table: Optional[str] = Field(
        None, description="Table involved in the identification rule."
    )
    order: Optional[int] = Field(None, description="Order of the identification rule.")
    allow_null_attribute: Optional[bool] = Field(
        None, description="Indicates if null attributes are allowed."
    )


class Link(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Link")
    id: Optional[str] = Field(
        default=None, description="Unique identifier of the results information."
    )
    url: Optional[str] = Field(
        default=None,
        description="URL to retrieve a list of records that violated the checks.",
    )
    link: Optional[str] = Field(
        default=None,
        description="Link to records.",
    )
    value: Optional[str] = Field(
        default=None,
        description="Link to records.",
    )
    label: Optional[str] = Field(
        default=None,
        description="Additional information about the instance scan findings.",
    )


class Rollback(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Rollback")
    id: str = Field(
        default=None,
        description="Sys_id of the rollback details for the installed packages.",
    )


class Links(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Links")
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
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    __hash__ = object.__hash__
    child_suite_results: Optional[List["TestSuiteResults"]] = Field(
        default=[], description="Results of nested test suites."
    )
    error: Optional[str] = Field(default=None, description="Error message.")


class CICD(BaseModel):
    """
    Pydantic model for parsing CI/CD API responses.

    Attributes:
    - base_type (str): Type of the response, defaults to "CICD".
    - error (Optional[str]): Error message.
    - links (Optional[Links]): Links and sys_ids associated with the response.
    - percent_complete (Optional[float]): Percentage of the request that is complete.
    - status (Optional[str]): Numeric execution state (e.g., "0" for Pending).
    - status_detail (Optional[str]): Detailed message about the execution status.
    - status_label (Optional[str]): Execution state description (e.g., "Pending").
    - status_message (Optional[str]): Additional description of the action's state.
    - rolledup_test_error_count (Optional[int]): Number of tests with errors.
    - rolledup_test_failure_count (Optional[int]): Number of tests that failed.
    - rolledup_test_skip_count (Optional[int]): Number of tests that were skipped.
    - rolledup_test_success_count (Optional[int]): Number of tests that ran successfully.
    - test_suite_duration (Optional[str]): Time taken to execute the test suite.
    - test_suite_name (Optional[str]): Name of the test suite.
    - test_suite_status (Optional[str]): State of the test suite.
    - rollback_version (Optional[str]): Version to rollback the application.
    - child_suite_results (Optional[List[TestSuiteResults]]): Child test suite results.
    - update_set_id (Optional[str]): Sys_id of the created update set.
    """

    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="CICD")
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
    child_suite_results: Optional[List[TestSuiteResults]] = Field(
        default=None, description="Child tests"
    )
    update_set_id: Optional[str] = Field(
        default=None, description="Sys_id of the created update set."
    )

    @property
    def is_successful(self):
        return self.status == "2" and self.test_suite_status == "success"


class CMDB(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="CMDB")
    icon_url: Optional[str] = Field(default=None, description="Class icon URL.")
    is_extendable: Optional[bool] = Field(
        default=None, description="Indicates if the class can be extended."
    )
    parent: Optional[str] = Field(default=None, description="Parent class.")
    children: Optional[List[str]] = Field(
        default=None, description="List of classes extended from the specified class."
    )
    name: str = Field(default=None, description="Table/class name.")
    icon: Optional[str] = Field(default=None, description="Class icon sys_id.")
    attributes: Optional[List[Attribute]] = Field(
        default=None, description="Available fields in the specified class table."
    )
    relationship_rules: List[RelationshipRule] = Field(
        default=None,
        description="Relationships between the specified class and other classes in the CMDB.",
    )
    label: str = Field(default=None, description="Specified class display name.")
    identification_rules: IdentificationRule = Field(
        default=None,
        description="Attributes associated with the configuration item identification rules for the specified class.",
    )


class CMDBService(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="CMDBService")
    items: List[Item] = Field(
        default=None, description="CIs within the application service."
    )
    relations: List[Relation] = Field(
        default=None, description="Relationship data for associated CIs."
    )


class ServiceRelation(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="ServiceRelation")
    parent: str = Field(
        default=None, description="Name of a parent CI related to the CI."
    )
    child: str = Field(
        default=None, description="Name of a child CI related to the CI."
    )


class Table(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Table")


class ImportSet(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="ImportSet")
    import_set: Optional[str] = Field(None, description="Name of the import set.")
    staging_table: Optional[str] = Field(
        None, description="Name of the import staging table."
    )


class ImportSetResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="ImportSetResult")
    display_name: Optional[str] = Field(
        None, description="Display name of the import set."
    )
    display_value: Optional[str] = Field(None, description="Value of the import set.")
    record_link: Optional[str] = Field(
        None, description="Table API GET request for the imported record."
    )
    status: Optional[str] = Field(None, description="Status of the import.")
    sys_id: Optional[str] = Field(None, description="Sys_id of the import record.")
    table: Optional[str] = Field(
        None, description="Name of the table in which the data was imported."
    )
    transform_map: Optional[str] = Field(None, description="Name of the transform map.")


class Authentication(BaseModel):
    model_config = ConfigDict(extra="allow")
    __hash__ = object.__hash__
    base_type: str = Field(default="Authentication")
    scope: str = Field(
        default=None,
        description="Amount of access granted by the access token. The scope is always user account, meaning that the "
        "access token has the same rights as the user account that authorized the token. For example, "
        "if Abel Tuter authorizes an application by providing login credentials, then the resulting "
        "access token grants the token bearer the same access privileges as Abel Tuter.",
    )
    token_type: str = Field(
        default=None,
        description="Type of token issued by the request as defined in the OAuth RFC. The token type is always "
        "Bearer, meaning that anyone in possession of the access token can access a protected resource "
        "without providing a cryptographic key.",
    )
    expires_in: Optional[int] = Field(
        default=None, description="Lifespan of the access token in seconds."
    )
    refresh_token: str = Field(
        default=None, description="String value of the refresh token."
    )
    access_token: str = Field(
        default=None,
        description="String value of the access token. Access requests made within the access token expiration time "
        "always return the current access token.",
    )
    format: str = Field(default=None, description="Output Format type. Always JSON")


class BatchRequestItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(description="ID for identifying the request in the batch.")
    method: str = Field(description="HTTP method (GET, POST, etc).")
    url: str = Field(description="Relative URL of the endpoint.")
    headers: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Request headers."
    )
    body: Optional[str] = Field(
        default=None, description="Base64 encoded body for POST/PUT/PATCH."
    )
    exclude_response_headers: Optional[bool] = Field(
        default=False, description="Exclude response headers."
    )


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    batch_request_id: Optional[str] = Field(
        default=None, description="Client provided batch ID."
    )
    rest_requests: List[BatchRequestItem] = Field(
        description="List of requests to execute."
    )


class BatchResponseItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(description="Matching ID from request.")
    status_code: int = Field(description="HTTP status code.")
    status_text: Optional[str] = Field(default=None, description="HTTP status text.")
    headers: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Response headers."
    )
    body: Optional[str] = Field(
        default=None, description="Base64 encoded response body."
    )
    execution_time: Optional[int] = Field(
        default=None, description="Execution time in ms."
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed."
    )


class BatchResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    batch_request_id: Optional[str] = Field(
        default=None, description="Matching batch ID."
    )
    serviced_requests: List[BatchResponseItem] = Field(
        default=[], description="Processed requests."
    )
    unserviced_requests: Optional[List[str]] = Field(
        default=None, description="IDs of unprocessed requests."
    )


class CILifecycleActionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    actionName: str = Field(description="Name of the CI action.")
    requestorId: str = Field(
        description="Sys_id of workflow context or registered operator."
    )
    sysIds: Optional[str] = Field(
        default=None, description="Comma-separated list of CI sys_ids."
    )
    leaseTime: Optional[str] = Field(
        default=None, description="Lease duration HH:MM:SS."
    )
    oldActionNames: Optional[str] = Field(
        default=None, description="Comma-separated list of old actions."
    )
    oldOpsLabels: Optional[str] = Field(
        default=None, description="Comma-separated list of old ops labels."
    )
    opsLabel: Optional[str] = Field(
        default=None, description="Operational state label."
    )


class CILifecycleResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    result: Union[bool, str, Dict] = Field(description="Result of the operation.")
    errors: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Errors if any."
    )
    ciActions: Optional[Union[List[str], str]] = Field(
        default=None, description="List of active actions."
    )
    operationalState: Optional[str] = Field(
        default=None, description="Operational state."
    )
    requestorId: Optional[str] = Field(
        default=None, description="Registered operator ID."
    )


class DevOpsSchemaRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    resource: str = Field(description="Type of resource schema to return.")
    toolId: Optional[str] = Field(default=None, description="Tool ID.")


class DevOpsOnboardingStatusResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    code: Optional[str] = Field(default=None, description="HTTP status code.")
    status: Optional[str] = Field(default=None, description="Status of onboarding.")
    messageDetails: Optional[Dict] = Field(
        default=None, description="Detailed status messages."
    )


class DevOpsChangeControlResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    changeControl: bool = Field(description="Flag indicating change control status.")


class DevOpsArtifactRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    artifacts: List[Dict[str, str]] = Field(
        description="List of artifacts to register."
    )
    orchestrationToolId: Optional[str] = Field(
        default=None, description="Orchestration tool ID."
    )
    toolId: Optional[str] = Field(default=None, description="Artifact tool ID.")
    branchName: Optional[str] = Field(default=None, description="Branch name.")
    pipelineName: Optional[str] = Field(default=None, description="Pipeline name.")
    projectName: Optional[str] = Field(default=None, description="Project name.")
    stageName: Optional[str] = Field(default=None, description="Stage name.")
    taskExecutionNumber: Optional[str] = Field(
        default=None, description="Task execution number."
    )


class EmailModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    to: Optional[Union[str, List[str]]] = Field(
        default=None, description="Recipient email addresses."
    )
    subject: Optional[str] = Field(default=None, description="Email subject.")
    text: Optional[str] = Field(default=None, description="Email body text.")
    html: Optional[str] = Field(default=None, description="Email body HTML.")
    sys_id: Optional[str] = Field(default=None, description="Email record Sys ID.")


class DataClassificationModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    table_name: Optional[str] = Field(default=None, description="Table name.")
    column_name: Optional[str] = Field(default=None, description="Column name.")
    classification: Optional[str] = Field(
        default=None, description="Classification level."
    )
    sys_id: Optional[str] = Field(
        default=None, description="Classification record Sys ID."
    )


class AttachmentModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    table_name: Optional[str] = Field(
        default=None, description="Table name associated with the attachment."
    )
    table_sys_id: Optional[str] = Field(
        default=None, description="Sys ID of the record in the table."
    )
    file_name: Optional[str] = Field(default=None, description="Name of the file.")
    content_type: Optional[str] = Field(
        default=None, description="MIME type of the file."
    )
    sys_id: Optional[str] = Field(default=None, description="Attachment Sys ID.")
    encryption_context: Optional[str] = Field(
        default=None, description="Encryption context."
    )


class AggregateModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    table_name: str = Field(description="Table name to aggregate on.")
    query: Optional[str] = Field(default=None, description="Encoded query string.")
    groupby: Optional[str] = Field(default=None, description="Field to group by.")
    stats: Optional[str] = Field(
        default=None, description="Statistics function (e.g., COUNT, MIN, MAX)."
    )
    fields: Optional[str] = Field(default=None, description="Fields to include.")


class ActivitySubscriptionModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    sys_id: Optional[str] = Field(
        default=None, description="Activity Subscription Sys ID."
    )
    name_value_pairs: Optional[str] = None
    sysparm_display_value: Optional[Union[str, bool]] = None
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
    table_name: Optional[str] = Field(default=None, description="Table name.")
    document_id: Optional[str] = Field(default=None, description="Document Sys ID.")
    api_parameters: Optional[Dict] = Field(description="API Parameters", default=None)
    data: Optional[Dict] = Field(
        default=None, description="Table dictionary value to insert"
    )

    def model_post_init(self, __context):
        """
        Build the API parameters
        """
        self.api_parameters = {}
        if self.name_value_pairs:
            self.api_parameters["name_value_pairs"] = self.name_value_pairs
        if self.sysparm_display_value:
            self.api_parameters["sysparm_display_value"] = self.sysparm_display_value
        if self.sysparm_exclude_reference_link:
            self.api_parameters["sysparm_exclude_reference_link"] = (
                self.sysparm_exclude_reference_link
            )
        if self.sysparm_fields:
            self.api_parameters["sysparm_fields"] = self.sysparm_fields
        if self.sysparm_query:
            self.api_parameters["sysparm_query"] = self.sysparm_query
        if self.sysparm_query_category:
            self.api_parameters["sysparm_query_category"] = self.sysparm_query_category
        if self.sysparm_query_no_domain:
            self.api_parameters["sysparm_query_no_domain"] = (
                self.sysparm_query_no_domain
            )
        if self.sysparm_suppress_pagination_header:
            self.api_parameters["sysparm_suppress_pagination_header"] = (
                self.sysparm_suppress_pagination_header
            )
        if self.sysparm_limit:
            self.api_parameters["sysparm_limit"] = self.sysparm_limit
        if self.sysparm_no_count:
            self.api_parameters["sysparm_no_count"] = self.sysparm_no_count
        if self.sysparm_offset:
            self.api_parameters["sysparm_offset"] = self.sysparm_offset


class AccountModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    sys_id: Optional[str] = Field(default=None, description="Account Sys ID.")
    name: Optional[str] = Field(default=None, description="Account name.")
    number: Optional[str] = Field(default=None, description="Account number.")


class HRProfileModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    sys_id: Optional[str] = Field(default=None, description="HR Profile Sys ID.")
    user: Optional[str] = Field(default=None, description="User Sys ID.")


class MetricBaseTimeSeriesModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    table_name: Optional[str] = Field(default=None, description="Table name.")
    sys_id: Optional[str] = Field(default=None, description="Record Sys ID.")
    metric_name: Optional[str] = Field(default=None, description="Metric name.")
    start_time: Optional[str] = Field(default=None, description="Start time for range.")
    end_time: Optional[str] = Field(default=None, description="End time for range.")
    values: Optional[List[Any]] = Field(default=None, description="Values to insert.")


# Service Qualification Models


class RelatedParty(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(description="Sys_id or external_id of the related party.")
    name: Optional[str] = Field(default=None, description="Name of the party.")
    referredType: str = Field(
        alias="@referredType",
        description="Type of related party (Customer, CustomerContact, Consumer).",
    )
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


class Place(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(description="Sys_id or external id of the location.")
    name: Optional[str] = Field(default=None, description="Name of the location.")
    referredType: Optional[str] = Field(
        default=None,
        alias="@referredType",
        description="Type of location (e.g., GeographicSite).",
    )
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


class ServiceCharacteristic(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(description="Name of the characteristic.")
    value: Optional[str] = Field(
        default=None, description="Value of the characteristic."
    )
    valueType: Optional[str] = Field(
        default=None, description="Data type of the value."
    )


class ServiceSpecification(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(
        description="External ID or Initial Version of the service specification."
    )
    name: Optional[str] = Field(
        default=None, description="Name of the service specification."
    )
    version: Optional[str] = Field(default=None, description="External Version.")
    internalVersion: Optional[str] = Field(
        default=None, description="Internal Version."
    )
    internalId: Optional[str] = Field(default=None, description="Internal ID.")
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


class Service(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(default=None, description="Name of the application service.")
    url: str = Field(
        default=None, description="Relative path to the application service."
    )
    service_relations: Optional[List[ServiceRelation]] = Field(
        default=None,
        description="Hierarchy data for the CIs within the application service.",
    )
    place: Optional[List[Place]] = Field(
        default=None, description="Location information."
    )
    serviceCharacteristic: Optional[List[ServiceCharacteristic]] = Field(
        default=None, description="List of service characteristics."
    )
    serviceSpecification: Optional[ServiceSpecification] = Field(
        default=None, description="Service specification details."
    )
    referenceServiceInventory: Optional[Dict[str, str]] = Field(
        default=None, description="Reference to existing service inventory."
    )
    serviceInventory: Optional[Dict[str, str]] = Field(
        default=None, description="Service inventory for upgrade/downgrade."
    )
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


class QualificationItemRelationship(BaseModel):
    model_config = ConfigDict(extra="allow")
    relationshipType: str = Field(
        description="Type of relationship (HasChild, HasParent)."
    )
    id: str = Field(description="ID of the target qualification item.")


class AlternateServiceProposal(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = Field(default=None, description="ID of the alternate proposal.")
    alternateServiceAvailabilityDate: Optional[str] = Field(
        default=None, description="Available date."
    )
    alternateService: Optional[Service] = Field(
        default=None, description="Service info for alternate proposal."
    )
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


class EligibilityUnavailabilityReason(BaseModel):
    model_config = ConfigDict(extra="allow")
    code: Optional[str] = Field(default=None, description="Reason code.")
    label: str = Field(description="Reason label.")


class ServiceQualificationItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(description="ID of the qualification item (external_id).")
    action: Optional[str] = Field(default=None, description="Action (e.g., add).")
    quantity: Optional[int] = Field(default=1, description="Quantity.")
    qualificationResult: Optional[str] = Field(
        default=None, description="Result (qualified, unqualified, etc.)."
    )
    state: Optional[str] = Field(default=None, description="State of the item.")
    expectedServiceAvailabilityDate: Optional[str] = Field(
        default=None, description="Expected availability date."
    )
    service: Optional[Service] = Field(
        default=None, description="Service capabilities."
    )
    qualificationItemRelationship: Optional[List[QualificationItemRelationship]] = (
        Field(default=None, description="Relationships to other items.")
    )
    alternateServiceProposal: Optional[
        Union[List[AlternateServiceProposal], AlternateServiceProposal]
    ] = Field(default=None, description="Alternate proposals.")
    eligibilityUnavailabilityReason: Optional[List[EligibilityUnavailabilityReason]] = (
        Field(default=None, description="Unavailability reasons.")
    )
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


class CheckServiceQualificationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    description: Optional[str] = Field(
        default=None, description="Description of the request."
    )
    checkServiceQualificationDate: Optional[str] = Field(
        default=None, description="Creation date."
    )
    effectiveQualificationDate: Optional[str] = Field(
        default=None, description="Effective date."
    )
    expectedQualificationDate: Optional[str] = Field(
        default=None, description="Expected date."
    )
    externalId: Optional[str] = Field(default=None, description="External ID.")
    relatedParty: List[RelatedParty] = Field(description="List of related parties.")
    serviceQualificationItem: List[ServiceQualificationItem] = Field(
        description="List of qualification items."
    )
    type: Optional[str] = Field(
        default=None, alias="@type", description="TMF Open API type annotation."
    )


# PPM Models


class CostPlan(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(description="Name of the cost plan.")
    resource_type: str = Field(description="Sys_id of the resource type.")
    start_fiscal_period: str = Field(
        description="Sys_id of the starting fiscal period."
    )
    end_fiscal_period: str = Field(description="Sys_id of the ending fiscal period.")
    task: str = Field(description="Sys_id of the project or demand.")
    unit_cost: float = Field(description="Unit cost.")


class ProjectTask(BaseModel):
    model_config = ConfigDict(extra="allow")
    short_description: str = Field(description="Short description.")
    external_id: Optional[str] = Field(default=None, description="External ID.")
    start_date: Optional[str] = Field(default=None, description="Start date.")
    end_date: Optional[str] = Field(default=None, description="End date.")
    child_tasks: Optional[List["ProjectTask"]] = Field(
        default=None, description="Recursive child tasks."
    )
    dependencies: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Dependencies."
    )


# Product Inventory Models


class ProductCharacteristic(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(description="Name of the characteristic.")
    value: str = Field(description="Value of the characteristic.")
    valueType: Optional[str] = Field(
        default=None, description="Type of characteristic value."
    )


class ProductOfferingRef(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = Field(
        default=None, description="Initial version or external ID."
    )
    internalId: Optional[str] = Field(default=None, description="Internal version.")
    internalVersion: Optional[str] = Field(default=None, description="Version.")
    name: Optional[str] = Field(default=None, description="Name.")
    version: Optional[str] = Field(default=None, description="External version.")


class ProductSpecificationRef(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = Field(
        default=None, description="Initial version or external ID."
    )
    internalId: Optional[str] = Field(default=None, description="Internal version.")
    internalVersion: Optional[str] = Field(default=None, description="Version.")
    version: Optional[str] = Field(default=None, description="External version.")


class ProductRelationship(BaseModel):
    model_config = ConfigDict(extra="allow")
    productId: str = Field(description="Sys_id of the related product.")
    relationshipType: str = Field(description="Type of relationship.")


class ProductInventory(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str] = Field(
        default=None, description="Sys_id of the product inventory."
    )
    name: Optional[str] = Field(
        default=None, description="Name of the product inventory."
    )
    place: Optional[List[Place]] = Field(
        default=None, description="Location of the product."
    )
    productCharacteristic: Optional[List[ProductCharacteristic]] = Field(
        default=None, description="List of product characteristics."
    )
    productId: Optional[str] = Field(
        default=None, description="Sys_id of the product model."
    )
    productOffering: Optional[ProductOfferingRef] = Field(
        default=None, description="Product offering."
    )
    productRelationship: Optional[List[ProductRelationship]] = Field(
        default=None, description="List of related products."
    )
    productSpecification: Optional[ProductSpecificationRef] = Field(
        default=None, description="Product specification."
    )
    realizingResource: Optional[Dict[str, str]] = Field(
        default=None, description="Realizing resource."
    )
    realizingService: Optional[Dict[str, str]] = Field(
        default=None, description="Realizing service."
    )
    relatedParty: Optional[List[RelatedParty]] = Field(
        default=None, description="List of related parties."
    )
    status: Optional[str] = Field(default=None, description="Status.")


class ProductInventoryQueryParams(BaseModel):
    model_config = ConfigDict(extra="allow")
    customer: Optional[str] = Field(
        default=None, description="Filter by customer sys_id or external ID."
    )
    fields: Optional[str] = Field(default=None, description="List of fields to return.")
    limit: Optional[int] = Field(
        default=20, le=100, description="Max number of records."
    )
    offset: Optional[int] = Field(default=0, description="Pagination offset.")
    place_id: Optional[str] = Field(default=None, description="Filter by location ID.")
    status: Optional[str] = Field(default=None, description="Filter by status.")


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """
    A wrapper class to hold the original requests.Response along with the parsed Pydantic data.
    This allows access to response metadata (e.g., status_code, headers) while providing
    the parsed result in Pydantic models.
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    base_type: str = Field(default="Response")
    response: requests.Response = Field(
        default=None, description="The original requests.Response object", exclude=True
    )
    result: Optional[Union[T, List[T]]] = Field(
        default=None, description="The Pydantic models converted from the response"
    )
