#!/usr/bin/python
# coding: utf-8
from typing import Dict, Any, Optional

import requests
import urllib3
from urllib.parse import urlencode
from base64 import b64encode
from pydantic import ValidationError

from servicenow_api.servicenow_models import (
    ApplicationServiceModel,
    CMDBModel,
    CICDModel,
    ChangeManagementModel,
    IncidentModel,
    ImportSetModel,
    KnowledgeManagementModel,
    TableModel,
    Authentication,
    ChangeRequest,
    CICD,
    CMDB,
    CMDBService,
    Table,
    ImportSet,
    Incident,
    Task,
    Attachment,
    Article,
    Response,
)
from servicenow_api.decorators import require_auth
from servicenow_api.exceptions import (
    AuthError,
    UnauthorizedError,
    ParameterError,
    MissingParameterError,
)


class Api(object):

    def __init__(
        self,
        url: str = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
        grant_type: Optional[str] = "password",
        proxies: Optional[dict] = None,
        verify: Optional[bool] = True,
    ):
        if url is None:
            raise MissingParameterError

        self._session = requests.Session()
        self.base_url = url
        self.auth_url = f"{self.base_url}/oauth_token.do"
        self.url = ""
        self.headers = None
        self.auth_headers = None
        self.auth_data = None
        self.encoded_auth_data = None
        self.token = None
        self.verify = verify
        self.proxies = proxies

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if token:
            self.token = token
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        elif username and password and client_id and client_secret:
            self.auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
            self.auth_data = {
                "grant_type": grant_type,
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password,
            }
            encoded_data_str = urlencode(self.auth_data)
            response = None
            try:
                response = requests.post(
                    url=self.auth_url,
                    data=encoded_data_str,
                    headers=self.auth_headers,
                )
                response = response.json()
                self.token = response["access_token"]
            except Exception as e:
                print(
                    f"Error Authenticating with OAuth: \n\n{e}\n\nResponse: {response}"
                )
                raise e
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        elif username and password:
            user_pass = f"{username}:{password}".encode()
            user_pass_encoded = b64encode(user_pass).decode()
            self.headers = {
                "Authorization": f"Basic {user_pass_encoded}",
                "Content-Type": "application/json",
            }
        else:
            raise MissingParameterError

        self.url = f"{self.base_url}/api"

        response = self._session.get(
            url=f"{self.url}/subscribers",
            headers=self.headers,
            verify=self.verify,
            proxies=self.proxies,
        )

        if response.status_code == 403:
            raise UnauthorizedError
        elif response.status_code == 401:
            raise AuthError
        elif response.status_code == 404:
            raise ParameterError

    @require_auth
    def refresh_auth_token(self) -> Response:
        """
        Refresh the authentication token
        :return:
        Response with new refreshed token.
        """
        refresh_data = {
            "grant_type": "refresh_token",
            "client_id": self.auth_data["client_id"],
            "client_secret": self.auth_data["client_secret"],
            "refresh_token": self.token,
        }
        encoded_data_str = urlencode(refresh_data)
        try:
            response = requests.post(
                url=self.auth_url, data=encoded_data_str, headers=self.auth_headers
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            self.token = json_response["access_token"]
            parsed_data = Authentication.model_validate(json_response)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during token refresh: {e}")
            raise

    ####################################################################################################################
    #                                         Application Service API                                                  #
    ####################################################################################################################
    @require_auth
    def get_application(self, **kwargs) -> Response:
        """
        Get information about an application.

        :param application_id: The unique identifier of the application.
        :type application_id: str

        :return: Response containing parsed Pydantic model with information about the application.
        :rtype: Response

        :raises MissingParameterError: If the required parameter `application_id` is not provided.
        """
        try:
            application = ApplicationServiceModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/cmdb/app_service/{application.application_id}/getContent",
                params=application.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            # Assuming ServiceNow APIs often wrap data in "result" key; adjust if direct
            result_data = json_response.get("result", json_response)
            parsed_data = CMDBService.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                                   CMDB API                                                       #
    ####################################################################################################################
    @require_auth
    def get_cmdb(self, **kwargs) -> Response:
        """
        Get Configuration Management Database (CMDB) information based on specified parameters.

        :param cmdb_id: The unique identifier of the CMDB record
        :type cmdb_id: str

        :return: Response containing parsed Pydantic model with CMDB information.
        :rtype: Response

        :raises ParameterError: If the provided parameters are invalid.
        """
        try:
            cmdb = CMDBModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/cmdb/meta/{cmdb.cmdb_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CMDB.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                                  CI/CD API                                                       #
    ####################################################################################################################
    @require_auth
    def batch_install_result(self, **kwargs) -> Response:
        """
        Get the result of a batch installation based on the provided result ID.

        :param result_id: The ID associated with the batch installation result.
        :type result_id: str

        :return: Response containing parsed Pydantic model with batch installation result.
        :rtype: Response

        :raises MissingParameterError: If result_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.result_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/app/batch/results/{cicd.result_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def instance_scan_progress(self, **kwargs) -> Response:
        """
        Get progress information for an instance scan based on the provided progress ID.

        :param progress_id: The ID associated with the instance scan progress.
        :type progress_id: str

        :return: Response containing parsed Pydantic model with instance scan progress.
        :rtype: Response

        :raises MissingParameterError: If progress_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.progress_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/instance_scan/result/{cicd.progress_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def progress(self, **kwargs) -> Response:
        """
        Get progress information based on the provided progress ID.

        :param progress_id: The ID associated with the progress.
        :type progress_id: str

        :return: Response containing parsed Pydantic model with progress information.
        :rtype: Response

        :raises MissingParameterError: If progress_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.progress_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/progress/{cicd.progress_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def batch_install(self, **kwargs) -> Response:
        """
        Initiate a batch installation with the provided parameters.

        :param name: The name of the batch installation.
        :type name: str
        :param notes: Additional notes for the batch installation.
        :type notes: str
        :param packages: The packages to be installed in the batch.
        :type packages: str

        :return: Response containing parsed Pydantic model with information about the batch installation.
        :rtype: Response

        :raises MissingParameterError: If name or packages are not provided.
        :raises ParameterError: If notes is not a string.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.name is None or cicd.packages is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app/batch/install",
                headers=self.headers,
                verify=self.verify,
                json=cicd.data,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def batch_rollback(self, **kwargs) -> Response:
        """
        Rollback a batch installation based on the provided rollback ID.

        :param rollback_id: The ID associated with the batch rollback.
        :type rollback_id: str

        :return: Response containing parsed Pydantic model with information about the batch rollback.
        :rtype: Response

        :raises MissingParameterError: If rollback_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.rollback_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_cicd/app/batch/rollback/{cicd.rollback_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def app_repo_install(self, **kwargs) -> Response:
        """
        Install an application from the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be installed.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param auto_upgrade_base_app: Flag indicating whether to auto-upgrade the base app.
        :type auto_upgrade_base_app: bool
        :param base_app_version: The version of the base app.
        :type base_app_version: str
        :param version: The version of the application to be installed.
        :type version: str

        :return: Response containing parsed Pydantic model with information about the installation.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.sys_id is None and cicd.scope is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app_repo/install",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def app_repo_publish(self, **kwargs) -> Response:
        """
        Publish an application to the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be published.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param dev_notes: Development notes for the published version.
        :type dev_notes: str
        :param version: The version of the application to be published.
        :type version: str

        :return: Response containing parsed Pydantic model with information about the publication.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.sys_id is None and cicd.scope is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app_repo/publish",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def app_repo_rollback(self, **kwargs) -> Response:
        """
        Rollback an application in the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be rolled back.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param version: The version of the application to be rolled back.
        :type version: str

        :return: Response containing parsed Pydantic model with information about the rollback.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id, scope, or version is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.sys_id is None and cicd.scope is None or cicd.version is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/app_repo/rollback",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def full_scan(self) -> Response:
        """
        Initiate a full instance scan.

        :return: Response containing parsed Pydantic model with information about the full scan.
        :rtype: Response
        """
        try:
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/full_scan",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def point_scan(self, **kwargs) -> Response:
        """
        Initiate a point instance scan based on the provided parameters.

        :param target_sys_id: The sys_id of the target instance.
        :type target_sys_id: str
        :param target_table: The table of the target instance.
        :type target_table: str

        :return: Response containing parsed Pydantic model with information about the point scan.
        :rtype: Response

        :raises MissingParameterError: If target_sys_id or target_table is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.target_sys_id is None or cicd.target_table is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/point_scan",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def combo_suite_scan(self, **kwargs) -> Response:
        """
        Initiate a suite scan for a combo based on the provided combo_sys_id.

        :param combo_sys_id: The sys_id of the combo to be scanned.
        :type combo_sys_id: str

        :return: Response containing parsed Pydantic model with information about the combo suite scan.
        :rtype: Response

        :raises MissingParameterError: If combo_sys_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.combo_sys_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/suite_scan/combo/{cicd.combo_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def suite_scan(self, **kwargs) -> Response:
        """
        Initiate a suite scan based on the provided suite_sys_id and sys_ids.

        :param suite_sys_id: The sys_id of the suite to be scanned.
        :type suite_sys_id: str
        :param sys_ids: List of sys_ids representing app_scope_sys_ids for the suite scan.
        :type sys_ids: list
        :param scan_type: Type of scan to be performed (default is "scoped_apps").
        :type scan_type: str

        :return: Response containing parsed Pydantic model with information about the suite scan.
        :rtype: Response

        :raises MissingParameterError: If suite_sys_id or sys_ids is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.suite_sys_id is None or cicd.app_scope_sys_ids is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/instance_scan/suite_scan/{cicd.suite_sys_id}/{cicd.scan_type}",
                headers=self.headers,
                json=cicd.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def activate_plugin(self, **kwargs) -> Response:
        """
        Activate a plugin based on the provided plugin_id.

        :param plugin_id: The ID of the plugin to be activated.
        :type plugin_id: str

        :return: Response containing parsed Pydantic model with information about the activation.
        :rtype: Response

        :raises MissingParameterError: If plugin_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.plugin_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/plugin/{cicd.plugin_id}/activate",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def rollback_plugin(self, **kwargs) -> Response:
        """
        Rollback a plugin based on the provided plugin_id.

        :param plugin_id: The ID of the plugin to be rolled back.
        :type plugin_id: str

        :return: Response containing parsed Pydantic model with information about the rollback.
        :rtype: Response

        :raises MissingParameterError: If plugin_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.plugin_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/plugin/{cicd.plugin_id}/rollback",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def apply_remote_source_control_changes(self, **kwargs) -> Response:
        """
        Apply remote source control changes based on the provided parameters.

        :param app_sys_id: The sys_id of the application for which changes should be applied.
        :type app_sys_id: str
        :param scope: The scope of the changes.
        :type scope: str
        :param branch_name: The name of the branch containing the changes.
        :type branch_name: str
        :param auto_upgrade_base_app: Flag indicating whether to auto-upgrade the base app.
        :type auto_upgrade_base_app: bool

        :return: Response containing parsed Pydantic model with information about the applied changes.
        :rtype: Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.app_sys_id is None and cicd.scope is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/sc/apply_changes",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def import_repository(self, **kwargs) -> Response:
        """
        Import a repository based on the provided parameters.

        :param credential_sys_id: The sys_id of the credential to be used for the import.
        :type credential_sys_id: str
        :param mid_server_sys_id: The sys_id of the MID Server to be used for the import.
        :type mid_server_sys_id: str
        :param repo_url: The URL of the repository to be imported.
        :type repo_url: str
        :param branch_name: The name of the branch to be imported.
        :type branch_name: str
        :param auto_upgrade_base_app: Flag indicating whether to auto-upgrade the base app.
        :type auto_upgrade_base_app: bool

        :return: Response containing parsed Pydantic model with information about the repository import.
        :rtype: Response

        :raises MissingParameterError: If repo_url is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.repo_url is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/sc/import",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def run_test_suite(self, **kwargs) -> Response:
        """
        Run a test suite based on the provided parameters.

        :param test_suite_sys_id: The sys_id of the test suite to be run.
        :type test_suite_sys_id: str
        :param test_suite_name: The name of the test suite to be run.
        :type test_suite_name: str
        :param browser_name: The name of the browser for the test run.
        :type browser_name: str
        :param browser_version: The version of the browser for the test run.
        :type browser_version: str
        :param os_name: The name of the operating system for the test run.
        :type os_name: str
        :param os_version: The version of the operating system for the test run.
        :type os_version: str

        :return: Response containing parsed Pydantic model with information about the test run.
        :rtype: Response

        :raises MissingParameterError: If test_suite_sys_id or test_suite_name is not provided.
        :raises ParameterError: If browser_name is not a valid string.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.test_suite_sys_id is None and cicd.test_suite_name is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/testsuite/run",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_set_create(self, **kwargs) -> Response:
        """
        Creates a new update set and inserts the new record in the Update Sets [sys_update_set] table.

        :param update_set_name: Name to give the update set.
        :type update_set_name: str
        :param description: Description of the update set.
        :type description: str
        :param scope: The scope name of the application in which to create the new update set.
        :type scope: str
        :param sys_id: Sys_id of the application in which to create the new update set.
        :type sys_id: str

        :return: Response containing parsed Pydantic model with information about the created update set.
        :rtype: Response

        :raises MissingParameterError: If update_set_name is not provided or both sys_id and scope are not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.update_set_name is None or (
                cicd.sys_id is None and cicd.scope is None
            ):
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/create",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_set_retrieve(self, **kwargs) -> Response:
        """
        Retrieves an update set with a given sys_id and allows you to remove the existing retrieved update set from the instance.

        :param update_set_id: Sys_id of the update set on the source instance from where the update set was retrieved.
        :type update_set_id: str
        :param update_source_id: Sys_id of the remote instance record.
        :type update_source_id: str
        :param update_source_instance_id: Instance ID of the remote instance.
        :type update_source_instance_id: str
        :param auto_preview: Flag that indicates whether to automatically preview the update set after retrieval.
        :type auto_preview: bool
        :param cleanup_retrieved: Flag that indicates whether to remove the existing retrieved update set from the instance.
        :type cleanup_retrieved: bool

        :return: Response containing parsed Pydantic model with progress information about the retrieval.
        :rtype: Response

        :raises MissingParameterError: If update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/retrieve",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_set_preview(self, **kwargs) -> Response:
        """
        Previews an update set to check for any conflicts and retrieve progress information about the update set operation.

        :param remote_update_set_id: Sys_id of the update set to preview.
        :type remote_update_set_id: str

        :return: Response containing parsed Pydantic model with progress information about the preview.
        :rtype: Response

        :raises MissingParameterError: If remote_update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.remote_update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/preview/{cicd.remote_update_set_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_set_commit(self, **kwargs) -> Response:
        """
        Commits an update set with a given sys_id.

        :param remote_update_set_id: Sys_id of the update set to commit.
        :type remote_update_set_id: str
        :param force_commit: Flag that indicates whether to force commit the update set.
        :type force_commit: str

        :return: Response containing parsed Pydantic model with progress information about the commit.
        :rtype: Response

        :raises MissingParameterError: If remote_update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.remote_update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/commit/{cicd.remote_update_set_id}",
                json=cicd.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_set_commit_multiple(self, **kwargs) -> Response:
        """
        Commits multiple update sets in a single request according to the order that they're provided.

        :param remote_update_set_ids: List of sys_ids associated with any update sets to commit. Sys_ids are committed in the order given in the request.
        :type remote_update_set_ids: str
        :param force_commit: Flag that indicates whether to force commit the update set.
        :type force_commit: str

        :return: Response containing parsed Pydantic model with progress information about the multiple commits.
        :rtype: Response

        :raises MissingParameterError: If remote_update_set_ids is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.remote_update_set_ids is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/commitMultiple",
                params=cicd.api_parameters,
                json=cicd.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_set_back_out(self, **kwargs) -> Response:
        """
        Backs out an installation operation that was performed on an update set with a given sys_id.

        :param update_set_id: Sys_id of the update set.
        :type update_set_id: str
        :param rollback_installs: Flag that indicates whether to rollback the batch installation performed during the update set commit.
        :type rollback_installs: bool

        :return: Response containing parsed Pydantic model with progress information about the back out.
        :rtype: Response

        :raises MissingParameterError: If update_set_id is not provided.
        """
        try:
            cicd = CICDModel(**kwargs)
            if cicd.update_set_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_cicd/update_set/back_out",
                params=cicd.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()  # Raise if HTTP error
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = CICD.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

        ####################################################################################################################

    #                                        Change Management API                                                     #
    ####################################################################################################################
    @require_auth
    def get_change_requests(self, **kwargs) -> Response:
        """
        Retrieve change requests based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None
        :param change_type: Type of change (emergency, normal, standard, model).
        :type change_type: str or None

        :return: Response containing list of parsed Pydantic models with information about change requests.
        :rtype: Response

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        :raises ParameterError: If unexpected response format is encountered.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            change_requests_data = []

            if change_request.change_type:
                change_type = f"/{change_request.change_type}"
            else:
                change_type = ""

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_requests_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change{change_type}",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    change_requests_data.extend(
                        [ChangeRequest.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_requests_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

            return Response(response=first_response, result=change_requests_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_nextstate(self, **kwargs) -> Response:
        """
        Retrieve the next state of a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the next state.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/nextstate",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_schedule(self, **kwargs) -> Response:
        """
        Retrieve the schedule of a change request based on CI sys ID.

        :param cmdb_ci_sys_id: Sys ID of the CI (Configuration Item).
        :type cmdb_ci_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the change request schedule.
        :rtype: Response

        :raises MissingParameterError: If cmdb_ci_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.cmdb_ci_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/ci/{change_request.cmdb_ci_sys_id}/schedule",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_tasks(self, **kwargs) -> Response:
        """
        Retrieve tasks associated with a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: Response containing list of parsed Pydantic models with information about change request tasks.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            tasks_data = []

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                tasks_data.extend([Task.model_validate(item) for item in result_data])

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    tasks_data.extend(
                        [Task.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                tasks_data.extend([Task.model_validate(item) for item in result_data])

            return Response(response=first_response, result=tasks_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request(self, **kwargs) -> Response:
        """
        Retrieve details of a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None

        :return: Response containing parsed Pydantic model with information about the change request.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            if change_request.change_type in ["emergency", "normal", "standard"]:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_type}/{change_request.change_request_sys_id}"
            else:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}"
            response = self._session.get(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_ci(self, **kwargs) -> Response:
        """
        Retrieve the configuration item (CI) associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the associated CI.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/ci",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_conflict(self, **kwargs) -> Response:
        """
        Retrieve conflict information associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the conflicts.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/conflict",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_standard_change_request_templates(self, **kwargs) -> Response:
        """
        Retrieve standard change request templates based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: Response containing list of parsed Pydantic models with information about standard change request templates.
        :rtype: Response

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            standard_change_templates_data = []

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/standard/template",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                standard_change_templates_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change/standard/template",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    standard_change_templates_data.extend(
                        [ChangeRequest.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/standard/template",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                standard_change_templates_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

            return Response(
                response=first_response, result=standard_change_templates_data
            )
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_models(self, **kwargs) -> Response:
        """
        Retrieve change request models based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: Response containing list of parsed Pydantic models with information about change request models.
        :rtype: Response

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            change_models_data = []
            if change_request.change_type:
                change_type = f"/{change_request.change_type}"
            else:
                change_type = ""

            if change_request.sysparm_offset and change_request.sysparm_limit:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/model{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_models_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

                while (
                    response.content
                    and len(result_data) >= change_request.sysparm_limit
                ):
                    change_request.sysparm_offset = (
                        change_request.sysparm_offset + change_request.sysparm_limit
                    )
                    change_request.model_post_init(change_request)
                    response = self._session.get(
                        url=f"{self.url}/sn_chg_rest/change/model{change_type}",
                        params=change_request.api_parameters,
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies,
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    result_data = json_response.get("result", json_response)
                    change_models_data.extend(
                        [ChangeRequest.model_validate(item) for item in result_data]
                    )
            else:
                response = self._session.get(
                    url=f"{self.url}/sn_chg_rest/change/model{change_type}",
                    params=change_request.api_parameters,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )
                response.raise_for_status()
                first_response = response
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                change_models_data.extend(
                    [ChangeRequest.model_validate(item) for item in result_data]
                )

            return Response(response=first_response, result=change_models_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_standard_change_request_model(self, **kwargs) -> Response:
        """
        Retrieve details of a standard change request model.

        :param model_sys_id: Sys ID of the standard change request model.
        :type model_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the standard change request model.
        :rtype: Response

        :raises MissingParameterError: If model_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.model_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/model/{change_request.model_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_standard_change_request_template(self, **kwargs) -> Response:
        """
        Retrieve details of a standard change request template.

        :param template_sys_id: Sys ID of the standard change request template.
        :type template_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the standard change request template.
        :rtype: Response

        :raises MissingParameterError: If template_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.template_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/standard/template/{change_request.template_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_change_request_worker(self, **kwargs) -> Response:
        """
        Retrieve details of a change request worker.

        :param worker_sys_id: Sys ID of the change request worker.
        :type worker_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the change request worker.
        :rtype: Response

        :raises MissingParameterError: If worker_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.worker_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_chg_rest/change/worker/{change_request.worker_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def create_change_request(self, **kwargs) -> Response:
        """
        Create a new change request.

        :param name_value_pairs: Name-value pairs providing details for the new change request.
        :type name_value_pairs: dict or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None
        :param standard_change_template_id: Sys ID of the standard change request template (if applicable).
        :type standard_change_template_id: str or None

        :return: Response containing parsed Pydantic model with information about the created change request.
        :rtype: Response

        :raises MissingParameterError: If name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.data is None:
                raise MissingParameterError
            standard_change_template_id = (
                f"/{change_request.standard_change_template_id}"
                if change_request.standard_change_template_id
                else ""
            )
            change_type = (
                f"/{change_request.change_type}" if change_request.change_type else ""
            )
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change{change_type}{standard_change_template_id}",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def create_change_request_task(self, **kwargs) -> Response:
        """
        Create a new task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param data: Name-value pairs providing details for the new task.
        :type data: dict or None

        :return: Response containing parsed Pydantic model with information about the created task.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.data is None
            ):
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/task",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Task.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def create_change_request_ci_association(self, **kwargs) -> Response:
        """
        Create associations between a change request and configuration items (CIs).

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param cmdb_ci_sys_ids: List of Sys IDs of CIs to associate with the change request.
        :type cmdb_ci_sys_ids: list or None
        :param association_type: Type of association (affected, impacted, offering).
        :type association_type: str or None
        :param refresh_impacted_services: Flag to refresh impacted services (applicable for 'affected' association).
        :type refresh_impacted_services: bool or None

        :return: Response containing parsed Pydantic model with information about the created associations.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id, cmdb_ci_sys_ids, or association_type is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If association_type is not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.cmdb_ci_sys_ids is None
                or change_request.association_type is None
            ):
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/ci",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def calculate_standard_change_request_risk(self, **kwargs) -> Response:
        """
        Calculate and update the risk of a standard change request.

        :param change_request_sys_id: Sys ID of the standard change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the calculated risk.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/standard/{change_request.change_request_sys_id}/risk",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_change_request_conflict(self, **kwargs) -> Response:
        """
        Check for conflicts in a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about conflicts.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/conflict",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def refresh_change_request_impacted_services(self, **kwargs) -> Response:
        """
        Refresh impacted services for a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the refreshed impacted services.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/refresh_impacted_services",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def approve_change_request(self, **kwargs) -> Response:
        """
        Approve or reject a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param state: State to set the change request to (approved or rejected).
        :type state: str or None

        :return: Response containing parsed Pydantic model with information about the approval/rejection.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id or state is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If state is not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.state is None
            ):
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/approvals",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_change_request(self, **kwargs) -> Response:
        """
        Update details of a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param name_value_pairs: New name-value pairs providing updated details for the change request.
        :type name_value_pairs: dict or None
        :param change_type: Type of change (emergency, normal, standard, model).
        :type change_type: str or None

        :return: Response containing parsed Pydantic model with information about the updated change request.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.data is None
            ):
                raise MissingParameterError
            change_type = (
                f"/{change_request.change_type}" if change_request.change_type else ""
            )
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change{change_type}/{change_request.change_request_sys_id}",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_change_request_first_available(self, **kwargs) -> Response:
        """
        Update the schedule of a change request to the first available slot.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the updated schedule.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/schedule/first_available",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_change_request_task(self, **kwargs) -> Response:
        """
        Update details of a task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_request_task_sys_id: Sys ID of the change request task.
        :type change_request_task_sys_id: str or None
        :param name_value_pairs: New name-value pairs providing updated details for the task.
        :type name_value_pairs: dict or None

        :return: Response containing parsed Pydantic model with information about the updated task.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id, change_request_task_sys_id, or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.change_request_task_sys_id is None
                or change_request.data is None
            ):
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task/{change_request.change_request_task_sys_id}",
                headers=self.headers,
                json=change_request.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Task.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def delete_change_request(self, **kwargs) -> Response:
        """
        Delete a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None

        :return: Response containing parsed Pydantic model with information about the deleted change request.
        :rtype: Response

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if change_request.change_request_sys_id is None:
                raise MissingParameterError
            if change_request.change_type in ["emergency", "normal", "standard"]:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_type}/{change_request.change_request_sys_id}"
            else:
                url = f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}"
            response = self._session.delete(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def delete_change_request_task(self, **kwargs) -> Response:
        """
        Delete a task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param task_sys_id: Sys ID of the task associated with the change request.
        :type task_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the deleted task.
        :rtype: Response

        :raises MissingParameterError: If either change_request_sys_id or task_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.task_sys_id is None
            ):
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/task/{change_request.task_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Task.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def delete_change_request_conflict_scan(self, **kwargs) -> Response:
        """
        Delete conflict scan information associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param task_sys_id: Sys ID of the task associated with the change request.
        :type task_sys_id: str or None

        :return: Response containing parsed Pydantic model with information about the deleted conflict scan.
        :rtype: Response

        :raises MissingParameterError: If either change_request_sys_id or task_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        try:
            change_request = ChangeManagementModel(**kwargs)
            if (
                change_request.change_request_sys_id is None
                or change_request.task_sys_id is None
            ):
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/sn_chg_rest/change/{change_request.change_request_sys_id}/conflict",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ChangeRequest.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                             Import Set API                                                       #
    ####################################################################################################################
    @require_auth
    def get_import_set(self, **kwargs) -> Response:
        """
        Get details of a specific import set record.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param import_set_sys_id: The sys_id of the import set record.
        :type import_set_sys_id: str

        :return: Response containing parsed Pydantic model with information about the import set record.
        :rtype: Response

        :raises ParameterError: If import_set_sys_id or table is not provided.
        """
        try:
            import_set = ImportSetModel(**kwargs)
            if import_set.import_set_sys_id is None or import_set.table is None:
                raise ParameterError
            response = self._session.get(
                url=f"{self.url}/now/import/{import_set.table}/{import_set.import_set_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ImportSet.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def insert_import_set(self, **kwargs) -> Response:
        """
        Insert a new record into the specified import set.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param data: Dictionary containing the field values for the new import set record.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the inserted import set record.
        :rtype: Response

        :raises ParameterError: If data or table is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            import_set = ImportSetModel(**kwargs)
            if import_set.data is None or import_set.table is None:
                raise ParameterError
            response = self._session.post(
                url=f"{self.url}/now/import/{import_set.table}",
                headers=self.headers,
                json=import_set.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = ImportSet.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def insert_multiple_import_sets(self, **kwargs) -> Response:
        """
        Insert multiple records into the specified import set.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param data: Dictionary containing the field values for multiple new import set records.
        :type data: dict

        :return: Response containing list of parsed Pydantic models with information about the inserted import set records.
        :rtype: Response

        :raises ParameterError: If data or table is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            import_set = ImportSetModel(**kwargs)
            if import_set.data is None or import_set.table is None:
                raise ParameterError
            response = self._session.post(
                url=f"{self.url}/now/import/{import_set.table}/insertMultiple",
                headers=self.headers,
                json=import_set.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [ImportSet.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                               Incident API                                                       #
    ####################################################################################################################
    @require_auth
    def get_incidents(self, **kwargs) -> Response:
        """
        Retrieve details of incident records.

        :param name_value_pairs: Dictionary of name-value pairs for filtering records.
        :type name_value_pairs: dict
        :param sysparm_display_value: Display values for reference fields ('True', 'False', or 'all').
        :type sysparm_display_value: str
        :param sysparm_exclude_reference_link: Exclude reference links in the response.
        :type sysparm_exclude_reference_link: bool
        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_no_count: Do not include the total number of records in the response.
        :type sysparm_no_count: bool
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param sysparm_query: Encoded query string for filtering records.
        :type sysparm_query: str
        :param sysparm_query_category: Category to which the query belongs.
        :type sysparm_query_category: str
        :param sysparm_query_no_domain: Exclude records based on domain separation.
        :type sysparm_query_no_domain: bool
        :param sysparm_suppress_pagination_header: Suppress pagination headers in the response.
        :type sysparm_suppress_pagination_header: bool
        :param sysparm_view: Display style ('desktop', 'mobile', or 'both').
        :type sysparm_view: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises MissingParameterError: If table is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            incident = IncidentModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/now/table/incident",
                params=incident.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Incident.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_incident(self, **kwargs) -> Response:
        """
        Retrieve details of a specific incident record.

        :param incident_id: The sys_id of the incident record.
        :type incident_id: str

        :param name_value_pairs: Dictionary of name-value pairs for filtering records.
        :type name_value_pairs: dict
        :param sysparm_display_value: Display values for reference fields ('True', 'False', or 'all').
        :type sysparm_display_value: str
        :param sysparm_exclude_reference_link: Exclude reference links in the response.
        :type sysparm_exclude_reference_link: bool
        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_no_count: Do not include the total number of records in the response.
        :type sysparm_no_count: bool
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param sysparm_query: Encoded query string for filtering records.
        :type sysparm_query: str
        :param sysparm_query_category: Category to which the query belongs.
        :type sysparm_query_category: str
        :param sysparm_query_no_domain: Exclude records based on domain separation.
        :type sysparm_query_no_domain: bool
        :param sysparm_suppress_pagination_header: Suppress pagination headers in the response.
        :type sysparm_suppress_pagination_header: bool
        :param sysparm_view: Display style ('desktop', 'mobile', or 'both').
        :type sysparm_view: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises MissingParameterError: If table is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            incident = IncidentModel(**kwargs)
            if incident.incident_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/now/table/incident/{incident.incident_id}",
                params=incident.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Incident.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def create_incident(self, **kwargs) -> Response:
        """
        Create a new incident record.

        :param kwargs: Keyword arguments to initialize an IncidentModel instance.
        :type kwargs: dict

        :return: Response containing parsed Pydantic model with information about the created incident record.
        :rtype: Response

        :raises MissingParameterError: If data for the incident is not provided.
        :raises ParameterError: If JSON serialization of incident data fails.
        :raises ParameterError: If validation of parameters fails.
        """
        try:
            incident = IncidentModel(**kwargs)
            if incident.data is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/now/table/incident",
                headers=self.headers,
                json=incident.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Incident.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                       Knowledge Management API                                                   #
    ####################################################################################################################
    @require_auth
    def get_knowledge_articles(self, **kwargs) -> Response:
        """
        Get all Knowledge Base articles.

        :param filter: Encoded query to use to filter the result set.
        :type filter: str
        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param sysparm_query: Encoded query string for filtering records.
        :type sysparm_query: str
        :param sysparm_query_category: Category to which the query belongs.
        :type sysparm_query_category: str
        :param kb: Comma-separated list of knowledge base sys_ids from the Knowledge Bases [kb_knowledge_base]
            table to restrict results to.
        :type kb: str
        :param language: List of comma-separated languages in two-letter ISO 639-1
            language code format to restrict results to.
            Alternatively type 'all' to search in all valid installed languages on an instance.
        :type language: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises MissingParameterError: If table is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            knowledge_base = KnowledgeManagementModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/sn_km_api/knowledge/articles",
                params=knowledge_base.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Article.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_knowledge_article(self, **kwargs) -> Response:
        """
        Get Knowledge Base article.

        :param article_sys_id: The sys_id of the knowledge article.
        :type article_sys_id: str
        :param filter: Encoded query to use to filter the result set.
        :type filter: str
        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_search_id: Unique identifier of search that returned this article
        :type sysparm_search_id: str
        :param sysparm_search_rank: Article search rank by click-rate
        :type sysparm_search_rank: str
        :param sysparm_update_view: Update view count and record an entry for the article
        :type sysparm_update_view: bool
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param sysparm_query: Encoded query string for filtering records.
        :type sysparm_query: str
        :param sysparm_query_category: Category to which the query belongs.
        :type sysparm_query_category: str
        :param kb: Comma-separated list of knowledge base sys_ids from the Knowledge Bases [kb_knowledge_base]
            table to restrict results to.
        :type kb: str
        :param language: List of comma-separated languages in two-letter ISO 639-1
            language code format to restrict results to.
            Alternatively type 'all' to search in all valid installed languages on an instance.
        :type language: str

        :return: Response containing parsed Pydantic model with information about the retrieved record.
        :rtype: Response

        :raises MissingParameterError: If article_sys_id is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            knowledge_base = KnowledgeManagementModel(**kwargs)
            if knowledge_base.article_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_km_api/knowledge/articles/{knowledge_base.article_sys_id}",
                params=knowledge_base.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Article.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_knowledge_article_attachment(self, **kwargs) -> Response:
        """
        Get Knowledge Base article attachment.

        :param article_sys_id: The Article Sys ID to search attachments for
        :type article_sys_id: str
        :param attachment_sys_id: The Attachment Sys ID
        :type attachment_sys_id: str

        :return: Response containing parsed Pydantic model with information about the retrieved attachment.
        :rtype: Response

        :raises MissingParameterError: If article_sys_id or attachment_sys_id is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            knowledge_base = KnowledgeManagementModel(**kwargs)
            if (
                knowledge_base.article_sys_id is None
                or knowledge_base.attachment_sys_id is None
            ):
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/sn_km_api/knowledge/articles/{knowledge_base.article_sys_id}/attachments/{knowledge_base.attachment_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Attachment.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_featured_knowledge_article(self, **kwargs) -> Response:
        """
        Get featured Knowledge Base articles.

        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param kb: Comma-separated list of knowledge base sys_ids from the Knowledge Bases [kb_knowledge_base]
            table to restrict results to.
        :type kb: str
        :param language: List of comma-separated languages in two-letter ISO 639-1
            language code format to restrict results to.
            Alternatively type 'all' to search in all valid installed languages on an instance.
        :type language: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises ParameterError: If input parameters are invalid.
        """
        try:
            knowledge_base = KnowledgeManagementModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/sn_km_api/knowledge/articles/featured",
                params=knowledge_base.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Article.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_most_viewed_knowledge_articles(self, **kwargs) -> Response:
        """
        Get most viewed Knowledge Base articles.

        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param kb: Comma-separated list of knowledge base sys_ids from the Knowledge Bases [kb_knowledge_base]
            table to restrict results to.
        :type kb: str
        :param language: List of comma-separated languages in two-letter ISO 639-1
            language code format to restrict results to.
            Alternatively type 'all' to search in all valid installed languages on an instance.
        :type language: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises ParameterError: If input parameters are invalid.
        """
        try:
            knowledge_base = KnowledgeManagementModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/sn_km_api/knowledge/articles/most_viewed",
                params=knowledge_base.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Article.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                                  Table API                                                       #
    ####################################################################################################################
    @require_auth
    def delete_table_record(self, **kwargs) -> Response:
        """
        Delete a record from the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be deleted.
        :type table_record_sys_id: str

        :return: Response containing parsed Pydantic model with information about the deletion.
        :rtype: Response

        :raises MissingParameterError: If table or table_record_sys_id is not provided.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None or table_model.table_record_sys_id is None:
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_table(self, **kwargs) -> Response:
        """
        Get records from the specified table based on provided parameters.

        :param table: The name of the table.
        :type table: str
        :param name_value_pairs: Dictionary of name-value pairs for filtering records.
        :type name_value_pairs: dict
        :param sysparm_display_value: Display values for reference fields ('True', 'False', or 'all').
        :type sysparm_display_value: str
        :param sysparm_exclude_reference_link: Exclude reference links in the response.
        :type sysparm_exclude_reference_link: bool
        :param sysparm_fields: Comma-separated list of field names to include in the response.
        :type sysparm_fields: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int
        :param sysparm_no_count: Do not include the total number of records in the response.
        :type sysparm_no_count: bool
        :param sysparm_offset: Number of records to skip before starting the retrieval.
        :type sysparm_offset: int
        :param sysparm_query: Encoded query string for filtering records.
        :type sysparm_query: str
        :param sysparm_query_category: Category to which the query belongs.
        :type sysparm_query_category: str
        :param sysparm_query_no_domain: Exclude records based on domain separation.
        :type sysparm_query_no_domain: bool
        :param sysparm_suppress_pagination_header: Suppress pagination headers in the response.
        :type sysparm_suppress_pagination_header: bool
        :param sysparm_view: Display style ('desktop', 'mobile', or 'both').
        :type sysparm_view: str

        :return: Response containing list of parsed Pydantic models with information about the retrieved records.
        :rtype: Response

        :raises MissingParameterError: If table is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/now/table/{table_model.table}",
                params=table_model.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Table.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_table_record(self, **kwargs) -> Response:
        """
        Get a specific record from the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be retrieved.
        :type table_record_sys_id: str

        :return: Response containing parsed Pydantic model with information about the retrieved record.
        :rtype: Response

        :raises MissingParameterError: If table or table_record_sys_id is not provided.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None or table_model.table_record_sys_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def patch_table_record(self, **kwargs) -> Response:
        """
        Partially update a record in the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be updated.
        :type table_record_sys_id: str
        :param data: Dictionary containing the fields to be updated.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the updated record.
        :rtype: Response

        :raises MissingParameterError: If table, table_record_sys_id, or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            table_model = TableModel(**kwargs)
            if (
                table_model.table is None
                or table_model.table_record_sys_id is None
                or table_model.data is None
            ):
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                json=table_model.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_table_record(self, **kwargs) -> Response:
        """
        Fully update a record in the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be updated.
        :type table_record_sys_id: str
        :param data: Dictionary containing the fields to be updated.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the updated record.
        :rtype: Response

        :raises MissingParameterError: If table, table_record_sys_id, or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            table_model = TableModel(**kwargs)
            if (
                table_model.table is None
                or table_model.table_record_sys_id is None
                or table_model.data is None
            ):
                raise MissingParameterError
            response = self._session.put(
                url=f"{self.url}/now/table/{table_model.table}/{table_model.table_record_sys_id}",
                json=table_model.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def add_table_record(self, **kwargs) -> Response:
        """
        Add a new record to the specified table.

        :param table: The name of the table.
        :type table: str
        :param data: Dictionary containing the field values for the new record.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the added record.
        :rtype: Response

        :raises MissingParameterError: If table or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        try:
            table_model = TableModel(**kwargs)
            if table_model.table is None or table_model.data is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/now/table/{table_model.table}",
                json=table_model.data,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Table.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                                 Custom API                                                       #
    ####################################################################################################################
    @require_auth
    def api_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
    ) -> Response:
        if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method.upper()}")
        try:
            request_func = getattr(self._session, method.lower())
            response = request_func(
                url=f"{self.url}/{endpoint}",
                headers=self.headers,
                data=data,
                json=json,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            parsed_data = (
                response.json()
                if response.content
                and "application/json" in response.headers.get("Content-Type", "")
                else None
            )
            return Response(response=response, result=parsed_data)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        except Exception as e:
            print(f"Request Error: {str(e)}")
            raise
