#!/usr/bin/python
# coding: utf-8
from typing import Dict, Any, Optional, List

import requests
import urllib3
from urllib.parse import urlencode
from base64 import b64encode
from pydantic import ValidationError

from servicenow_api.servicenow_models import (
    ApplicationServiceModel,
    CMDBModel,
    CMDBInstanceModel,
    CMDBIngestModel,
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
    CheckServiceQualificationRequest,
    ServiceQualificationItem,
    CostPlan,
    ProjectTask,
    ProductInventory,
    ProductInventoryQueryParams,
    Response,
    Article,
    BatchRequest,
    BatchResponse,
    CILifecycleActionRequest,
    CILifecycleResult,
    DevOpsSchemaRequest,
    DevOpsOnboardingStatusResponse,
    DevOpsChangeControlResponse,
    DevOpsArtifactRegistrationRequest,
    EmailModel,
    DataClassificationModel,
    AttachmentModel,
    Attachment,
    AggregateModel,
    ActivitySubscriptionModel,
    AccountModel,
    HRProfileModel,
    MetricBaseTimeSeriesModel,
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

    @require_auth
    def delete_cmdb_relation(self, **kwargs) -> Response:
        """
        Deletes the relation for the specified configuration item (CI).

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param rel_sys_id: Sys_id of the relation to remove.
        :type rel_sys_id: str

        :return: Response containing the operation result.
        :rtype: Response

        :raises MissingParameterError: If className, sys_id, or rel_sys_id is not provided.
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.rel_sys_id is None:
                raise MissingParameterError

            response = self._session.delete(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}/relation/{cmdb.rel_sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            # Delete usually returns 204 No Content, check if there is content to parse
            if response.content:
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                # No specific response model for delete, likely just success confirmation
                return Response(response=response, result=result_data)
            return Response(response=response, result={"status": "deleted"})
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_cmdb_instances(self, **kwargs) -> Response:
        """
        Returns the available configuration items (CI) for a specified CMDB class.

        :param className: CMDB class name.
        :type className: str
        :param sysparm_limit: Maximum number of records to return.
        :type sysparm_limit: int or str
        :param sysparm_offset: Starting record index.
        :type sysparm_offset: int or str
        :param sysparm_query: Encoded query used to filter the result set.
        :type sysparm_query: str

        :return: Response containing list of CIs.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}",
                params=cmdb.api_parameters,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            # Response is a list of simple dicts usually (sys_id, name)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_cmdb_instance(self, **kwargs) -> Response:
        """
        Returns attributes and relationship information for a specified CI record.

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI record to retrieve.
        :type sys_id: str

        :return: Response containing parsed Pydantic model with CI information.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def create_cmdb_instance(self, **kwargs) -> Response:
        """
        Creates a single configuration item (CI).

        :param className: CMDB class name.
        :type className: str
        :param attributes: Data attributes to define in the CI record.
        :type attributes: dict
        :param source: Discovery source.
        :type source: str
        :param inbound_relations: List of inbound relations.
        :type inbound_relations: list
        :param outbound_relations: List of outbound relations.
        :type outbound_relations: list

        :return: Response containing created CI.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def update_cmdb_instance(self, **kwargs) -> Response:
        """
        Updates the specified CI record (PUT).

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param attributes: Data attributes to replace.
        :type attributes: dict
        :param source: Discovery source.
        :type source: str

        :return: Response containing updated CI.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.put(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def patch_cmdb_instance(self, **kwargs) -> Response:
        """
        Replaces attributes in the specified CI record (PATCH).

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param attributes: Data attributes to replace.
        :type attributes: dict
        :param source: Discovery source.
        :type source: str

        :return: Response containing updated CI.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.patch(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def create_cmdb_relation(self, **kwargs) -> Response:
        """
        Adds an inbound and/or outbound relation to the specified CI.

        :param className: CMDB class name.
        :type className: str
        :param sys_id: Sys_id of the CI.
        :type sys_id: str
        :param inbound_relations: List of inbound relations.
        :type inbound_relations: list
        :param outbound_relations: List of outbound relations.
        :type outbound_relations: list
        :param source: Discovery source.
        :type source: str

        :return: Response containing updated CI relations.
        :rtype: Response
        """
        try:
            cmdb = CMDBInstanceModel(**kwargs)
            if cmdb.className is None or cmdb.sys_id is None or cmdb.source is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/now/cmdb/instance/{cmdb.className}/{cmdb.sys_id}/relation",
                headers=self.headers,
                json=cmdb.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                           CMDB Data Ingestion API                                                #
    ####################################################################################################################
    @require_auth
    def ingest_cmdb_data(self, **kwargs) -> Response:
        """
        Inserts records into the Import Set table associated with the data source.

        :param data_source_sys_id: Sys_id of the data source record.
        :type data_source_sys_id: str
        :param records: Array of objects to ingest.
        :type records: list

        :return: Response containing ingestion result.
        :rtype: Response
        """
        try:
            ingest = CMDBIngestModel(**kwargs)
            if ingest.data_source_sys_id is None or ingest.records is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/now/cmdb/ingest/{ingest.data_source_sys_id}",
                headers=self.headers,
                json=ingest.data,
                verify=self.verify,
                proxies=self.proxies,
            )
            # Status codes 201 and 202 are success
            if response.status_code not in [201, 202]:
                response.raise_for_status()

            json_response = response.json()
            result_data = json_response.get("result", json_response)
            return Response(response=response, result=result_data)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                                  Batch API                                                       #
    ####################################################################################################################
    @require_auth
    def batch_request(self, **kwargs) -> Response:
        """
        Sends multiple REST API requests in a single call.

        :param batch_request_id: ID that identifies the batch of requests.
        :type batch_request_id: str
        :param rest_requests: List of request objects to include in the batch request.
        :type rest_requests: list

        :return: Response containing the batch results.
        :rtype: Response
        """
        try:
            batch = BatchRequest(**kwargs)
            if batch.rest_requests is None:
                raise MissingParameterError

            response = self._session.post(
                url=f"{self.url}/api/now/v1/batch",
                headers=self.headers,
                json=batch.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            json_response = response.json()
            # The response body for batch is at the root, not inside 'result'
            return Response(
                response=response, result=BatchResponse.model_validate(json_response)
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
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
    #                                           CI Lifecycle Management API                                            #
    ####################################################################################################################
    @require_auth
    def delete_ci_lifecycle_action(self, **kwargs) -> Response:
        """
        Removes a configuration item (CI) action for a list of CIs.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            if not req.actionName or not req.requestorId or not req.sysIds:
                raise MissingParameterError

            params = {
                "actionName": req.actionName,
                "requestorId": req.requestorId,
                "sysIds": req.sysIds,
            }
            response = self._session.delete(
                url=f"{self.url}/api/now/cilifecyclemgmt/actions",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def unregister_ci_lifecycle_operator(self, **kwargs) -> Response:
        """
        Unregisters an operator for non-workflow users.
        """
        try:
            req_id = kwargs.get("req_id")
            if not req_id:
                raise MissingParameterError

            response = self._session.delete(
                url=f"{self.url}/api/now/cilifecyclemgmt/operators/{req_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_ci_lifecycle_active_actions(self, **kwargs) -> Response:
        """
        Returns a list of active CI actions for the specified CI.
        """
        try:
            sys_id = kwargs.get("sys_id")
            if not sys_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/actions/{sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_ci_lifecycle_compat_actions(self, **kwargs) -> Response:
        """
        Determines whether two specified CI actions are compatible.
        """
        try:
            actionName = kwargs.get("actionName")
            otherActionName = kwargs.get("otherActionName")
            if not actionName or not otherActionName:
                raise MissingParameterError

            params = {"actionName": actionName, "otherActionName": otherActionName}
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/compatActions",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_ci_lifecycle_lease_expired(self, **kwargs) -> Response:
        """
        Determines whether the lease has expired for the requester.
        """
        try:
            sys_id = kwargs.get("sys_id")
            actionName = kwargs.get("actionName")
            requestorId = kwargs.get("requestorId")
            if not sys_id or not actionName or not requestorId:
                raise MissingParameterError

            params = {"actionName": actionName, "requestorId": requestorId}
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/leases/{sys_id}/expired",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_ci_lifecycle_not_allowed_action(self, **kwargs) -> Response:
        """
        Determines whether a specified CI action is not allowed.
        """
        try:
            actionName = kwargs.get("actionName")
            ciClass = kwargs.get("ciClass")
            opsLabel = kwargs.get("opsLabel")
            if not actionName or not ciClass or not opsLabel:
                raise MissingParameterError

            params = {
                "actionName": actionName,
                "ciClass": ciClass,
                "opsLabel": opsLabel,
            }
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/notAllowedAction",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_ci_lifecycle_not_allowed_ops_transition(self, **kwargs) -> Response:
        """
        Determines whether an operational state transition is allowed.
        """
        try:
            ciClass = kwargs.get("ciClass")
            opsLabel = kwargs.get("opsLabel")
            transitionOpsLabel = kwargs.get("transitionOpsLabel")
            if not ciClass or not opsLabel or not transitionOpsLabel:
                raise MissingParameterError

            params = {
                "ciClass": ciClass,
                "opsLabel": opsLabel,
                "transitionOpsLabel": transitionOpsLabel,
            }
            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/notAllowedOpsTransition",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_ci_lifecycle_requestor_valid(self, **kwargs) -> Response:
        """
        Determines whether the specified user is a valid requester.
        """
        try:
            req_id = kwargs.get("req_id")
            if not req_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/requestors/{req_id}/valid",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_ci_lifecycle_status(self, **kwargs) -> Response:
        """
        Returns the current operational state for the specified CI.
        """
        try:
            sys_id = kwargs.get("sys_id")
            if not sys_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/api/now/cilifecyclemgmt/statuses/{sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def extend_ci_lifecycle_lease(self, **kwargs) -> Response:
        """
        Extends the specified CI action's lease expiration time.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            # The sys_id, actionName, leaseTime, requestorId are needed
            # For patch sys_id is usually a path param, but here it's about the lease for a CI sys_id
            sys_id = kwargs.get("sys_id")
            if (
                not sys_id
                or not req.actionName
                or not req.leaseTime
                or not req.requestorId
            ):
                raise MissingParameterError

            params = {
                "actionName": req.actionName,
                "leaseTime": req.leaseTime,
                "requestorId": req.requestorId,
            }
            response = self._session.patch(
                url=f"{self.url}/api/now/cilifecyclemgmt/leases/{sys_id}",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def add_ci_lifecycle_action(self, **kwargs) -> Response:
        """
        Adds a specified CI action to a specified list of CIs.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            if not req.actionName or not req.requestorId or not req.sysIds:
                raise MissingParameterError

            params = {
                "actionName": req.actionName,
                "requestorId": req.requestorId,
                "sysIds": req.sysIds,
            }
            if req.leaseTime:
                params["leaseTime"] = req.leaseTime
            if req.oldActionNames:
                params["oldActionNames"] = req.oldActionNames

            response = self._session.post(
                url=f"{self.url}/api/now/cilifecyclemgmt/actions",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def register_ci_lifecycle_operator(self, **kwargs) -> Response:
        """
        Registers an operator for a non-workflow user.
        """
        try:
            response = self._session.post(
                url=f"{self.url}/api/now/cilifecyclemgmt/operators",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def set_ci_lifecycle_status(self, **kwargs) -> Response:
        """
        Sets the operational state for a specified list of CIs.
        """
        try:
            req = CILifecycleActionRequest(**kwargs)
            if not req.opsLabel or not req.requestorId or not req.sysIds:
                raise MissingParameterError

            params = {
                "opsLabel": req.opsLabel,
                "requestorId": req.requestorId,
                "sysIds": req.sysIds,
            }
            if req.oldOpsLabels:
                params["oldOpsLabels"] = req.oldOpsLabels

            response = self._session.post(
                url=f"{self.url}/api/now/cilifecyclemgmt/statuses",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CILifecycleResult.model_validate(response.json()),
            )
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
        :type name_value_pairs: str or None
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
        :type name_value_pairs: str or None
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
        :type name_value_pairs: str or None
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
        :type name_value_pairs: str or None
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
        :type name_value_pairs: str or None
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
        :type name_value_pairs: str or None
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
        :type name_value_pairs: str or None

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
        :type name_value_pairs: str
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
        :type name_value_pairs: str
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
    #                                                  DevOps API                                                      #
    ####################################################################################################################
    @require_auth
    def get_devops_code_schema(self, **kwargs) -> Response:
        """
        Returns the schema object for a specified code resource.
        """
        try:
            req = DevOpsSchemaRequest(**kwargs)
            if not req.resource:
                raise MissingParameterError

            params = {"resource": req.resource}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/code/schema",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json())
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_devops_onboarding_status(self, **kwargs) -> Response:
        """
        Returns the current status of the specified onboarding event.
        """
        try:
            id_ = kwargs.get("id")
            if not id_:
                raise MissingParameterError

            params = {"id": id_}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/onboarding/status",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=DevOpsOnboardingStatusResponse.model_validate(
                    response.json().get("result", {})
                ),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_devops_change_control(self, **kwargs) -> Response:
        """
        Checks if the orchestration task is under change control.
        """
        try:
            toolId = kwargs.get("toolId")
            orchestrationTaskName = kwargs.get("orchestrationTaskName")
            if not toolId:
                raise MissingParameterError

            params = {
                "toolId": toolId,
                "toolType": kwargs.get(
                    "toolType", "jenkins"
                ),  # Default to jenkins if not provided? Spec says toolType valid value jenkins
            }
            if orchestrationTaskName:
                params["orchestrationTaskName"] = orchestrationTaskName
            if "testConnection" in kwargs:
                params["testConnection"] = str(kwargs.get("testConnection")).lower()
            if "orchestrationTaskURL" in kwargs:
                params["orchestrationTaskURL"] = kwargs.get("orchestrationTaskURL")

            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/changeControl",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=DevOpsChangeControlResponse.model_validate(
                    response.json().get("result", {})
                ),
            )
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_devops_change_info(self, **kwargs) -> Response:
        """
        Retrieves change request details for a specified orchestration pipeline execution.
        """
        try:
            toolId = kwargs.get("toolId")
            buildNumber = kwargs.get("buildNumber")
            if not toolId or not buildNumber:
                raise MissingParameterError

            params = {"toolId": toolId, "buildNumber": buildNumber}
            if "stageName" in kwargs:
                params["stageName"] = kwargs.get("stageName")
            if "pipelineName" in kwargs:
                params["pipelineName"] = kwargs.get("pipelineName")
            if "projectName" in kwargs:
                params["projectName"] = kwargs.get("projectName")
            if "branchName" in kwargs:
                params["branchName"] = kwargs.get("branchName")

            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/changeInfo",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result", {}))
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_devops_orchestration_schema(self, **kwargs) -> Response:
        """
        Returns the schema object for a specified orchestration resource.
        """
        try:
            resource = kwargs.get("resource")
            if not resource:
                raw_req = DevOpsSchemaRequest(**kwargs)  # Try to use model
                resource = raw_req.resource

            if not resource:
                raise MissingParameterError

            params = {"resource": resource}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/schema",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json())
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def check_devops_step_mapping(self, **kwargs) -> Response:
        """
        Verifies that the information being passed is valid for the creation of an orchestration task.
        """
        try:
            toolId = kwargs.get("toolId")
            orchestrationTaskName = kwargs.get("orchestrationTaskName")
            orchestrationTaskURL = kwargs.get("orchestrationTaskURL")
            toolType = kwargs.get("toolType", "jenkins")

            if not toolId or not orchestrationTaskName or not orchestrationTaskURL:
                raise MissingParameterError

            params = {
                "toolId": toolId,
                "orchestrationTaskName": orchestrationTaskName,
                "orchestrationTaskURL": orchestrationTaskURL,
                "toolType": toolType,
            }
            # Add optional params
            for k in [
                "branchName",
                "isMultiBranch",
                "parentStageName",
                "parentStageURL",
                "testConnection",
            ]:
                if k in kwargs:
                    params[k] = kwargs[k]

            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/orchestration/stepMapping",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result", {}))
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_devops_plan_schema(self, **kwargs) -> Response:
        """
        Returns the schema object for a specific plan.
        """
        try:
            resource = kwargs.get("resource")
            if not resource:
                raise MissingParameterError

            params = {"resource": resource}
            response = self._session.get(
                url=f"{self.url}/api/sn_devops/devops/plan/schema",
                params=params,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json())
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def register_devops_artifact(self, **kwargs) -> Response:
        """
        Enables orchestration tools to register artifacts into a ServiceNow instance.
        """
        try:
            req = DevOpsArtifactRegistrationRequest(**kwargs)
            if not req.artifacts:
                raise MissingParameterError

            params = {}
            if req.orchestrationToolId:
                params["orchestrationToolId"] = req.orchestrationToolId
            if req.toolId:
                params["toolId"] = req.toolId

            response = self._session.post(
                url=f"{self.url}/api/sn_devops/devops/artifact/registration",
                params=params,
                headers=self.headers,
                json=req.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result", {}))
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                             Email API                                                            #
    ####################################################################################################################
    @require_auth
    def send_email(self, **kwargs) -> Response:
        try:
            email = EmailModel(**kwargs)
            response = self._session.post(
                url=f"{self.url}/now/email",
                headers=self.headers,
                json=email.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                       Data Classification API                                                    #
    ####################################################################################################################
    @require_auth
    def get_data_classification(self, **kwargs) -> Response:
        try:
            dc = DataClassificationModel(**kwargs)
            url = f"{self.url}/now/data_classification/classification"
            if dc.sys_id:
                url = f"{url}/{dc.sys_id}"

            response = self._session.get(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                           Attachment API                                                         #
    ####################################################################################################################
    @require_auth
    def get_attachment(self, **kwargs) -> Response:
        try:
            att = AttachmentModel(**kwargs)
            if not att.sys_id:
                raise MissingParameterError

            response = self._session.get(
                url=f"{self.url}/now/attachment/{att.sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=Attachment.model_validate(response.json().get("result")),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def upload_attachment(self, file_path: str, **kwargs) -> Response:
        try:
            att = AttachmentModel(**kwargs)
            if not att.table_name or not att.table_sys_id or not att.file_name:
                raise MissingParameterError

            with open(file_path, "rb") as f:
                headers = self.headers.copy()
                headers.pop("Content-Type", None)

                params = {
                    "table_name": att.table_name,
                    "table_sys_id": att.table_sys_id,
                    "file_name": att.file_name,
                }

                response = self._session.post(
                    url=f"{self.url}/now/attachment/file",
                    headers=headers,
                    params=params,
                    data=f,
                    verify=self.verify,
                    proxies=self.proxies,
                )
            response.raise_for_status()
            return Response(
                response=response,
                result=Attachment.model_validate(response.json().get("result")),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def delete_attachment(self, **kwargs) -> Response:
        try:
            att = AttachmentModel(**kwargs)
            if not att.sys_id:
                raise MissingParameterError

            response = self._session.delete(
                url=f"{self.url}/now/attachment/{att.sys_id}",
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result={"status": "deleted"})
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                           Aggregate API                                                          #
    ####################################################################################################################
    @require_auth
    def get_stats(self, **kwargs) -> Response:
        try:
            agg = AggregateModel(**kwargs)
            params = {}
            if agg.query:
                params["sysparm_query"] = agg.query
            if agg.groupby:
                params["sysparm_group_by"] = agg.groupby
            if agg.stats:
                params["sysparm_count"] = "true"

            response = self._session.get(
                url=f"{self.url}/now/stats/{agg.table_name}",
                headers=self.headers,
                params=params,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                      Activity Subscriptions API                                                  #
    ####################################################################################################################
    @require_auth
    def get_activity_subscriptions(self, **kwargs) -> Response:
        try:
            sub = ActivitySubscriptionModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/now/ui/activity_subscription",
                headers=self.headers,
                params=sub.api_parameters,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                            Account API                                                           #
    ####################################################################################################################
    @require_auth
    def get_account(self, **kwargs) -> Response:
        try:
            acc = AccountModel(**kwargs)
            url = f"{self.url}/now/csm/account"
            if acc.sys_id:
                url = f"{url}/{acc.sys_id}"
            response = self._session.get(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                               HR API                                                             #
    ####################################################################################################################
    @require_auth
    def get_hr_profile(self, **kwargs) -> Response:
        try:
            hr = HRProfileModel(**kwargs)
            url = f"{self.url}/now/hr/profile"
            if hr.sys_id:
                url = f"{url}/{hr.sys_id}"

            response = self._session.get(
                url=url,
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                       MetricBase Time Series API                                                 #
    ####################################################################################################################
    @require_auth
    def metricbase_insert(self, **kwargs) -> Response:
        try:
            mb = MetricBaseTimeSeriesModel(**kwargs)
            response = self._session.post(
                url=f"{self.url}/now/metricbase/insert",
                headers=self.headers,
                json=mb.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
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

    ####################################################################################################################
    #                                     Technical Service Qualification Open API                                     #
    ####################################################################################################################
    @require_auth
    def check_service_qualification(self, **kwargs) -> Response:
        """
        Creates a technical service qualification request.
        """
        try:
            req = CheckServiceQualificationRequest(**kwargs)
            # dump payload excluding None to avoid sending nulls
            payload = req.model_dump(exclude_none=True, by_alias=True)

            response = self._session.post(
                url=f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification",
                headers=self.headers,
                json=payload,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            # The response body for create is CheckServiceQualificationRequest structure (with ID etc)
            return Response(
                response=response,
                result=CheckServiceQualificationRequest.model_validate(response.json()),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def get_service_qualification(self, **kwargs) -> Response:
        """
        Retrieves a technical qualification request by ID or list all.
        """
        try:
            # Reusing CheckServiceQualificationRequest to hold params like externalId or just passing id as arg
            # But here we might just need 'id' or query params.
            # Let's support 'id' in kwargs for specific fetch, else list.
            sys_id = kwargs.get("id") or kwargs.get("sys_id")

            if sys_id:
                url = f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification/{sys_id}"
                params = {}
            else:
                url = f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification"
                # Support filtering params from kwargs
                params = {
                    k: v
                    for k, v in kwargs.items()
                    if k
                    in [
                        "state",
                        "description",
                        "qualificationResult",
                        "limit",
                        "offset",
                    ]
                }

            response = self._session.get(
                url=url,
                headers=self.headers,
                params=params,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            data = response.json()
            # If list, it returns a list. If single, returns object.
            if isinstance(data, list):
                result = [
                    CheckServiceQualificationRequest.model_validate(item)
                    for item in data
                ]
            else:
                result = CheckServiceQualificationRequest.model_validate(data)

            return Response(response=response, result=result)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def process_service_qualification_result(self, **kwargs) -> Response:
        """
        Processes a technical service qualification result.
        """
        try:
            # This endpoint takes 'serviceQualificationItem' list in body.
            # Reuse CheckServiceQualificationRequest partially or just construct body.
            # The requirement says "Request body parameters: serviceQualificationItem"

            items = kwargs.get("serviceQualificationItem")
            if not items:
                raise MissingParameterError("serviceQualificationItem is required")

            # Validate items using the model
            valid_items = [
                ServiceQualificationItem(**item) if isinstance(item, dict) else item
                for item in items
            ]

            payload = {
                "serviceQualificationItem": [
                    item.model_dump(exclude_none=True, by_alias=True)
                    for item in valid_items
                ],
                "description": kwargs.get("description"),
                "@type": "CheckServiceQualification",
            }
            # Add description if present

            response = self._session.post(
                url=f"{self.url}/api/sn_ord_qual_mgmt/qualification/checkServiceQualification/processResult",
                headers=self.headers,
                json=payload,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(
                response=response,
                result=CheckServiceQualificationRequest.model_validate(response.json()),
            )
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                     Project Portfolio Management (PPM) API                                       #
    ####################################################################################################################
    @require_auth
    def insert_cost_plans(self, plans: List[Dict[str, Any]], **kwargs) -> Response:
        """
        Creates cost plans.
        """
        try:
            # Validate list of plans
            valid_plans = [CostPlan(**p) for p in plans]
            payload = [p.model_dump() for p in valid_plans]

            response = self._session.post(
                url=f"{self.url}/api/now/ppm/insert_cost_plans",
                headers=self.headers,
                json=payload,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def insert_project_tasks(self, **kwargs) -> Response:
        """
        Creates a project and associated project tasks.
        """
        try:
            # Top level is project properties + child_tasks
            # Validate using ProjectTask model (assuming top level structure matches or is similar)
            # The API doc says: start_date, end_date, short_description, external_id, child_tasks.
            # ProjectTask model covers this.
            project = ProjectTask(**kwargs)

            response = self._session.post(
                url=f"{self.url}/api/now/ppm/insert_project_tasks",
                headers=self.headers,
                json=project.model_dump(exclude_none=True),
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result=response.json().get("result"))
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    ####################################################################################################################
    #                                     Product Inventory Open API                                                   #
    ####################################################################################################################
    @require_auth
    def get_product_inventory(self, **kwargs) -> Response:
        """
        Retrieves a list of all product inventories.
        """
        try:
            qp = ProductInventoryQueryParams(**kwargs)
            params = qp.model_dump(exclude_none=True)
            # 'place' in params is an Object in doc "place": {"id": "String"}, but requests params need flattening or specific format
            # if place_id is passed, we might need to format it as place.id or check how SN expects it.
            # Query parameters section says:
            # place: Filter by location. "place": { "id": "String" }
            # Usually in SN API, objects in query params are stringified JSON or dot notation.
            # Doc says Data type: Object.

            if qp.place_id:
                # Constructing the object structure if needed, or maybe it expects sysparm_query
                # But here it describes specific query parameters.
                # Let's try to pass it as direct param if library supports it, or stringified json.
                # Common SN pattern for object params in GET is often not standard.
                # However, the doc "Supported request parameters" lists `place` as a query parameter of type Object.
                # We will handle it by excluding place_id from direct params and adding 'place'
                params.pop("place_id")
                params["place"] = str({"id": qp.place_id}).replace(
                    "'", '"'
                )  # Primitive JSON stringify

            response = self._session.get(
                url=f"{self.url}/api/sn_prd_invt/product",
                headers=self.headers,
                params=params,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()

            # Returns list of ProductInventory
            # Handle pagination headers if needed, but for now return parsed body.
            # Body itself is a list? Doc says "Response body parameters (JSON)" lists fields like href, id...
            # Usually "Retrieves a list" implies a JSON array.
            data = response.json()
            if isinstance(data, list):
                result = [ProductInventory.model_validate(item) for item in data]
            else:
                result = ProductInventory.model_validate(data)

            return Response(response=response, result=result)
        except ValidationError as ve:
            print(f"Invalid parameters: {ve.errors()}")
            raise
        except Exception as e:
            print(f"Error during API call: {e}")
            raise

    @require_auth
    def delete_product_inventory(self, **kwargs) -> Response:
        """
        Deletes a specified product inventory record.
        """
        try:
            sys_id = kwargs.get("id") or kwargs.get("sys_id")
            if not sys_id:
                raise MissingParameterError("product inventory id is required")

            response = self._session.delete(
                url=f"{self.url}/api/sn_prd_invt/order/product/{sys_id}",  # Doc says /api/sn_prd_invt/order/product/{id} AND /api/sn_prd_invt/product/{id} in example?
                # "Product Inventory Open API – DELETE /sn_prd_invt/order/product/{id}" -> Header
                # "Default URL: /api/sn_prd_invt/order/product/{id}"
                # "cURL request ... DELETE ... /api/sn_prd_invt/product/..." -> Example URL is different!
                # I will trust the Default URL header: /api/sn_prd_invt/order/product/{id}
                headers=self.headers,
                verify=self.verify,
                proxies=self.proxies,
            )
            response.raise_for_status()
            return Response(response=response, result={"status": "deleted"})
        except Exception as e:
            print(f"Error during API call: {e}")
            raise
