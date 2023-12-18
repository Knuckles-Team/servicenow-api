#!/usr/bin/python
# coding: utf-8

import json
import requests
import urllib3
from base64 import b64encode
from pydantic import ValidationError

try:
    from servicenow_api.servicenow_models import (ApplicationServiceModel, CMDBModel, CICDModel, ChangeManagementModel,
                                                  IncidentModel, ImportSetModel, TableModel)
except ModuleNotFoundError:
    from servicenow_models import (ApplicationServiceModel, CMDBModel, CICDModel, ChangeManagementModel,
                                   IncidentModel, ImportSetModel, TableModel)
try:
    from servicenow_api.decorators import require_auth
except ModuleNotFoundError:
    from decorators import require_auth
try:
    from servicenow_api.exceptions import (AuthError, UnauthorizedError, ParameterError, MissingParameterError)
except ModuleNotFoundError:
    from exceptions import (AuthError, UnauthorizedError, ParameterError, MissingParameterError)


class Api(object):

    def __init__(self, url: str = None, username: str = None, password: str = None, proxies: dict = None,
                 verify: bool = True):
        if url is None:
            raise MissingParameterError

        self._session = requests.Session()
        self.url = url
        self.headers = None
        self.verify = verify
        self.proxies = proxies

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if username and password:
            user_pass = f'{username}:{password}'.encode()
            user_pass_encoded = b64encode(user_pass).decode()
            self.headers = {
                'Authorization': f'Basic {user_pass_encoded}',
                'Content-Type': 'application/json'
            }
        else:
            raise MissingParameterError

        response = self._session.get(url=f'{self.url}/subscribers',
                                     headers=self.headers,
                                     verify=self.verify,
                                     proxies=self.proxies)

        if response.status_code == 403:
            raise UnauthorizedError
        elif response.status_code == 401:
            raise AuthError
        elif response.status_code == 404:
            raise ParameterError

    ####################################################################################################################
    #                                         Application Service API                                                  #
    ####################################################################################################################
    @require_auth
    def get_application(self, **kwargs):
        """
        Get information about an application.

        :param application_id: The unique identifier of the application.
        :type application_id: str

        :return: JSON response containing information about the application.
        :rtype: dict

        :raises MissingParameterError: If the required parameter `application_id` is not provided.
        """
        application = ApplicationServiceModel(**kwargs)
        try:
            response = self._session.get(url=f'{self.url}/cmdb/app_service/'
                                             f'{application.application_id}/getContent?mode=full',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                                   CMDB API                                                       #
    ####################################################################################################################
    @require_auth
    def get_cmdb(self, **kwargs):
        """
        Get Configuration Management Database (CMDB) information based on specified parameters.

        :param cmdb_id: The unique identifier of the CMDB record
        :type cmdb_id: str

        :return: JSON response containing CMDB information.
        :rtype: requests.models.Response

        :raises ParameterError: If the provided parameters are invalid.
        """
        cmdb = CMDBModel(**kwargs)
        try:
            response = self._session.get(url=f'{self.url}/cmdb/meta/{cmdb.cmdb_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                                  CI/CD API                                                       #
    ####################################################################################################################
    @require_auth
    def batch_install_result(self, **kwargs):
        """
        Get the result of a batch installation based on the provided result ID.

        :param result_id: The ID associated with the batch installation result.
        :type result_id: str

        :return: JSON response containing batch installation result.
        :rtype: requests.models.Response

        :raises MissingParameterError: If result_id is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.result_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_cicd/app/batch/results/{cicd.result_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def instance_scan_progress(self, **kwargs):
        """
        Get progress information for an instance scan based on the provided progress ID.

        :param progress_id: The ID associated with the instance scan progress.
        :type progress_id: str

        :return: JSON response containing instance scan progress.
        :rtype: requests.models.Response

        :raises MissingParameterError: If progress_id is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.progress_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_cicd/instance_scan/result/{cicd.progress_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def progress(self, **kwargs):
        """
        Get progress information based on the provided progress ID.

        :param progress_id: The ID associated with the progress.
        :type progress_id: str

        :return: JSON response containing progress information.
        :rtype: requests.models.Response

        :raises MissingParameterError: If progress_id is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.progress_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_cicd/progress/{cicd.progress_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def batch_install(self, **kwargs):
        """
        Initiate a batch installation with the provided parameters.

        :param name: The name of the batch installation.
        :type name: str
        :param notes: Additional notes for the batch installation.
        :type notes: str
        :param packages: The packages to be installed in the batch.
        :type packages: str

        :return: JSON response containing information about the batch installation.
        :rtype: requests.models.Response

        :raises MissingParameterError: If name or packages are not provided.
        :raises ParameterError: If notes is not a string.
        """
        cicd = CICDModel(**kwargs)
        if cicd.name is None or cicd.packages is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/app/batch/install',
                                          headers=self.headers,
                                          verify=self.verify,
                                          data=cicd.data,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def batch_rollback(self, **kwargs):
        """
       Rollback a batch installation based on the provided rollback ID.

       :param rollback_id: The ID associated with the batch rollback.
       :type rollback_id: str

       :return: JSON response containing information about the batch rollback.
       :rtype: requests.models.Response

       :raises MissingParameterError: If rollback_id is not provided.
       """
        cicd = CICDModel(**kwargs)
        if cicd.rollback_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_cicd/app/batch/rollback/{cicd.rollback_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def app_repo_install(self, **kwargs):
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

        :return: JSON response containing information about the installation.
        :rtype: requests.models.Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/app_repo/install{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def app_repo_publish(self, **kwargs):
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

        :return: JSON response containing information about the publication.
        :rtype: requests.models.Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/app_repo/publish{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def app_repo_rollback(self, **kwargs):
        """
        Rollback an application in the repository based on the provided parameters.

        :param app_sys_id: The sys_id of the application to be rolled back.
        :type app_sys_id: str
        :param scope: The scope of the application.
        :type scope: str
        :param version: The version of the application to be rolled back.
        :type version: str

        :return: JSON response containing information about the rollback.
        :rtype: requests.models.Response

        :raises MissingParameterError: If app_sys_id, scope, or version is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None or cicd.version is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/app_repo/rollback{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def full_scan(self):
        """
        Initiate a full instance scan.

        :return: JSON response containing information about the full scan.
        :rtype: requests.models.Response
        """
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/instance_scan/full_scan',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def point_scan(self, **kwargs):
        """
        Initiate a point instance scan based on the provided parameters.

        :param target_sys_id: The sys_id of the target instance.
        :type target_sys_id: str
        :param target_table: The table of the target instance.
        :type target_table: str

        :return: JSON response containing information about the point scan.
        :rtype: requests.models.Response

        :raises MissingParameterError: If target_sys_id or target_table is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.target_sys_id is None or cicd.target_table is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/instance_scan/point_scan{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def combo_suite_scan(self, **kwargs):
        """
        Initiate a suite scan for a combo based on the provided combo_sys_id.

        :param combo_sys_id: The sys_id of the combo to be scanned.
        :type combo_sys_id: str

        :return: JSON response containing information about the combo suite scan.
        :rtype: requests.models.Response

        :raises MissingParameterError: If combo_sys_id is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.combo_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/instance_scan/suite_scan/combo/{cicd.combo_sys_id}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def suite_scan(self, **kwargs):
        """
        Initiate a suite scan based on the provided suite_sys_id and sys_ids.

        :param suite_sys_id: The sys_id of the suite to be scanned.
        :type suite_sys_id: str
        :param sys_ids: List of sys_ids representing app_scope_sys_ids for the suite scan.
        :type sys_ids: list
        :param scan_type: Type of scan to be performed (default is "scoped_apps").
        :type scan_type: str

        :return: JSON response containing information about the suite scan.
        :rtype: requests.models.Response

        :raises MissingParameterError: If suite_sys_id or sys_ids is not provided.
        :raises ParameterError: If JSON serialization fails.
        """

        cicd = CICDModel(**kwargs)
        if cicd.suite_sys_id is None or cicd.sys_ids is None:
            raise MissingParameterError
        try:
            response = self._session.post(
                url=f'{self.url}/sn_cicd/instance_scan/suite_scan/{cicd.suite_sys_id}/{cicd.scan_type}',
                headers=self.headers,
                data=cicd.data,
                verify=self.verify,
                proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def activate_plugin(self, **kwargs):
        """
        Activate a plugin based on the provided plugin_id.

        :param plugin_id: The ID of the plugin to be activated.
        :type plugin_id: str

        :return: JSON response containing information about the activation.
        :rtype: requests.models.Response

        :raises MissingParameterError: If plugin_id is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.plugin_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/plugin/{cicd.plugin_id}/activate',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def rollback_plugin(self, **kwargs):
        """
        Rollback a plugin based on the provided plugin_id.

        :param plugin_id: The ID of the plugin to be rolled back.
        :type plugin_id: str

        :return: JSON response containing information about the rollback.
        :rtype: requests.models.Response

        :raises MissingParameterError: If plugin_id is not provided.
        """
        cicd = CICDModel(**kwargs)
        if cicd.plugin_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/plugin/{cicd.plugin_id}/rollback',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def apply_remote_source_control_changes(self, **kwargs):
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

        :return: JSON response containing information about the applied changes.
        :rtype: requests.models.Response

        :raises MissingParameterError: If app_sys_id or scope is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/sc/apply_changes{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def import_repository(self, **kwargs):
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

        :return: JSON response containing information about the repository import.
        :rtype: requests.models.Response

        :raises MissingParameterError: If repo_url is not provided.
        :raises ParameterError: If auto_upgrade_base_app is not a boolean.
        """
        cicd = CICDModel(**kwargs)
        if cicd.repo_url is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/sc/import{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def run_test_suite(self, **kwargs):
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

        :return: JSON response containing information about the test run.
        :rtype: requests.models.Response

        :raises MissingParameterError: If test_suite_sys_id or test_suite_name is not provided.
        :raises ParameterError: If browser_name is not a valid string.
        """
        cicd = CICDModel(**kwargs)
        if cicd.test_suite_sys_id is None and cicd.test_suite_name is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_cicd/testsuite/run{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                        Change Management API                                                     #
    ####################################################################################################################
    @require_auth
    def get_change_requests(self, **kwargs):
        """
        Retrieve change requests based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param max_pages: Maximum number of pages to retrieve (0 for unlimited).
        :type max_pages: int
        :param per_page: Number of results per page.
        :type per_page: int
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None
        :param change_type: Type of change (emergency, normal, standard, model).
        :type change_type: str or None

        :return: JSON response containing information about change requests.
        :rtype: dict

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        :raises ParameterError: If unexpected response format is encountered.
        """
        change_request = ChangeManagementModel(**kwargs)
        page = 0
        responses = None

        while change_request.response_length > 1:
            if not change_request.api_parameters:
                change_request.api_parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                     f'/change{change_request.change_type}'
                                                     f'{change_request.api_parameters}{offset}',
                                                 headers=self.headers,
                                                 verify=self.verify,
                                                 proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    response_length = len(verified_response['result'])
                    if response_length > 1 and page < change_request.max_pages \
                            or response_length > 1 and change_request.max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    raise ParameterError
            else:
                responses = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                  f'/change{change_request.change_type}'
                                                  f'{change_request.api_parameters}{offset}',
                                              headers=self.headers,
                                              verify=self.verify,
                                              proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + change_request.per_page
        return responses

    @require_auth
    def get_change_request_nextstate(self, **kwargs):
        """
        Retrieve the next state of a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about the next state.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/{change_request.change_request_sys_id}/nextstate',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_schedule(self, **kwargs):
        """
        Retrieve the schedule of a change request based on CI sys ID.

        :param cmdb_ci_sys_id: Sys ID of the CI (Configuration Item).
        :type cmdb_ci_sys_id: str or None

        :return: JSON response containing information about the change request schedule.
        :rtype: dict

        :raises MissingParameterError: If cmdb_ci_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.cmdb_ci_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/ci/{change_request.cmdb_ci_sys_id}/schedule',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_tasks(self, **kwargs):
        """
        Retrieve tasks associated with a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param max_pages: Maximum number of pages to retrieve (0 for unlimited).
        :type max_pages: int
        :param per_page: Number of results per page.
        :type per_page: int
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: JSON response containing information about change request tasks.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        page = 0
        responses = None
        while change_request.response_length > 1:
            if not change_request.api_parameters:
                parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                     f'/change/{change_request.change_request_sys_id}/'
                                                     f'task{change_request.api_parameters}{offset}',
                                                 headers=self.headers,
                                                 verify=self.verify,
                                                 proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    response_length = len(verified_response['result'])
                    if response_length > 1 and page < change_request.max_pages \
                            or response_length > 1 and change_request.max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    raise ParameterError
            else:
                responses = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                  f'/change/{change_request.change_request_sys_id}/'
                                                  f'task{change_request.api_parameters}{offset}',
                                              headers=self.headers,
                                              verify=self.verify,
                                              proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + change_request.per_page
        return responses

    @require_auth
    def get_change_request(self, **kwargs):
        """
        Retrieve details of a specific change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None

        :return: JSON response containing information about the change request.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        if (change_request.change_type and isinstance(change_request.change_type, str)
                and change_request.change_type == 'emergency'):
            try:
                response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                 f'/change/emergency/{change_request.change_request_sys_id}',
                                             headers=self.headers,
                                             verify=self.verify,
                                             proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif (change_request.change_type and isinstance(change_request.change_type, str)
              and change_request.change_type == 'normal'):
            try:
                response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                 f'/change/normal/{change_request.change_request_sys_id}',
                                             headers=self.headers,
                                             verify=self.verify,
                                             proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif (change_request.change_type and isinstance(change_request.change_type, str)
              and change_request.change_type == 'standard'):
            try:
                response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                 f'/change/standard/{change_request.change_request_sys_id}',
                                             headers=self.headers,
                                             verify=self.verify,
                                             proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        else:
            try:
                response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                 f'/change/{change_request.change_request_sys_id}',
                                             headers=self.headers,
                                             verify=self.verify,
                                             proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_ci(self, **kwargs):
        """
        Retrieve the configuration item (CI) associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about the associated CI.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/{change_request.change_request_sys_id}/ci',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_ci(self, **kwargs):
        """
        Retrieve conflict information associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about the conflicts.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/{change_request.change_request_sys_id}/conflict',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_standard_change_request_templates(self, **kwargs):
        """
        Retrieve standard change request templates based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param max_pages: Maximum number of pages to retrieve (0 for unlimited).
        :type max_pages: int
        :param per_page: Number of results per page.
        :type per_page: int
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: JSON response containing information about standard change request templates.
        :rtype: dict

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        page = 0
        responses = None
        verified_response = None
        response_length = 10
        while response_length > 1:
            if not change_request.api_parameters:
                change_request.api_parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(
                        url=f'{self.url}/sn_chg_rest/change/standard/template{change_request.api_parameters}{offset}',
                        headers=self.headers,
                        verify=self.verify,
                        proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    if 'result' in verified_response:
                        response_length = len(verified_response['result'])
                    else:
                        return verified_response
                    if response_length > 1 and page < change_request.max_pages \
                            or response_length > 1 and change_request.max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    return verified_response
            else:
                responses = self._session.get(
                    url=f'{self.url}/sn_chg_rest/change/standard/template{change_request.api_parameters}{offset}',
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + change_request.per_page
        return responses

    @require_auth
    def get_change_request_models(self, **kwargs):
        """
        Retrieve change request models based on specified parameters.

        :param order: Ordering parameter for sorting results.
        :type order: str or None
        :param name_value_pairs: Additional name-value pairs for filtering.
        :type name_value_pairs: dict or None
        :param max_pages: Maximum number of pages to retrieve (0 for unlimited).
        :type max_pages: int
        :param per_page: Number of results per page.
        :type per_page: int
        :param sysparm_query: Query parameter for filtering results.
        :type sysparm_query: str or None
        :param text_search: Text search parameter for searching results.
        :type text_search: str or None

        :return: JSON response containing information about change request models.
        :rtype: dict

        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        responses = None
        page = 0
        while change_request.response_length > 1:
            if not change_request.api_parameters:
                change_request.api_parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                     f'/change/model{change_request.api_parameters}{offset}',
                                                 headers=self.headers,
                                                 verify=self.verify,
                                                 proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    response_length = len(verified_response['result'])
                    if response_length > 1 and page < change_request.max_pages \
                            or response_length > 1 and change_request.max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    raise ParameterError
            else:
                responses = self._session.get(url=f'{self.url}/sn_chg_rest'
                                                  f'/change/model{change_request.api_parameters}{offset}',
                                              headers=self.headers,
                                              verify=self.verify,
                                              proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + change_request.per_page
        return responses

    @require_auth
    def get_standard_change_request_model(self, **kwargs):
        """
        Retrieve details of a standard change request model.

        :param model_sys_id: Sys ID of the standard change request model.
        :type model_sys_id: str or None

        :return: JSON response containing information about the standard change request model.
        :rtype: dict

        :raises MissingParameterError: If model_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.model_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/model/{change_request.model_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_standard_change_request_template(self, **kwargs):
        """
        Retrieve details of a standard change request template.

        :param template_sys_id: Sys ID of the standard change request template.
        :type template_sys_id: str or None

        :return: JSON response containing information about the standard change request template.
        :rtype: dict

        :raises MissingParameterError: If template_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.template_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/standard/template/{change_request.template_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_worker(self, **kwargs):
        """
        Retrieve details of a change request worker.

        :param worker_sys_id: Sys ID of the change request worker.
        :type worker_sys_id: str or None

        :return: JSON response containing information about the change request worker.
        :rtype: dict

        :raises MissingParameterError: If worker_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.worker_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/sn_chg_rest'
                                             f'/change/worker/{change_request.worker_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_change_request(self, **kwargs):
        """
        Create a new change request.

        :param name_value_pairs: Name-value pairs providing details for the new change request.
        :type name_value_pairs: dict or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None
        :param standard_change_template_id: Sys ID of the standard change request template (if applicable).
        :type standard_change_template_id: str or None

        :return: JSON response containing information about the created change request.
        :rtype: dict

        :raises MissingParameterError: If name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.name_value_pairs is None:
            raise MissingParameterError
        if change_request.standard_change_template_id:
            standard_change_template_id = f'/{change_request.standard_change_template_id}'
        else:
            standard_change_template_id = ''
        if change_request.change_type:
            change_type = f'/{change_request.change_type}'
        else:
            change_type = ''
        print(f"URI: {self.url}/sn_chg_rest/change{change_type}{standard_change_template_id}")
        try:
            response = self._session.post(url=f'{self.url}/sn_chg_rest'
                                              f'/change{change_type}{standard_change_template_id}',
                                          headers=self.headers,
                                          data=change_request.data,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_change_request_task(self, **kwargs):
        """
        Create a new task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param name_value_pairs: Name-value pairs providing details for the new task.
        :type name_value_pairs: dict or None

        :return: JSON response containing information about the created task.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.name_value_pairs is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_chg_rest/change/task',
                                          headers=self.headers,
                                          data=change_request.data,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_change_request_ci_association(self, **kwargs):
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

        :return: JSON response containing information about the created associations.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id, cmdb_ci_sys_ids, or association_type is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If association_type is not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if (change_request.change_request_sys_id is None
                or change_request.cmdb_ci_sys_ids is None
                or change_request.association_type is None):
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_chg_rest'
                                              f'/change/{change_request.change_request_sys_id}/ci',
                                          headers=self.headers,
                                          data=change_request.data,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def calculate_standard_change_request_risk(self, **kwargs):
        """
        Calculate and update the risk of a standard change request.

        :param change_request_sys_id: Sys ID of the standard change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about the calculated risk.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.patch(url=f'{self.url}/sn_chg_rest'
                                               f'/change/standard/{change_request.change_request_sys_id}/risk',
                                           headers=self.headers,
                                           verify=self.verify,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def check_change_request_conflict(self, **kwargs):
        """
        Check for conflicts in a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about conflicts.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_chg_rest'
                                              f'/change/{change_request.change_request_sys_id}/conflict',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def refresh_change_request_impacted_services(self, **kwargs):
        """
        Refresh impacted services for a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about the refreshed impacted services.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/sn_chg_rest'
                                              f'/change/{change_request.change_request_sys_id}/refresh_impacted_services',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def approve_change_request(self, **kwargs):
        """
        Approve or reject a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param state: State to set the change request to (approved or rejected).
        :type state: str or None

        :return: JSON response containing information about the approval/rejection.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id or state is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If state is not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.state is None:
            raise MissingParameterError
        try:
            response = self._session.patch(url=f'{self.url}/sn_chg_rest'
                                               f'/change/{change_request.change_request_sys_id}/approvals',
                                           headers=self.headers,
                                           verify=self.verify,
                                           data=change_request.data,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_change_request(self, **kwargs):
        """
        Update details of a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param name_value_pairs: New name-value pairs providing updated details for the change request.
        :type name_value_pairs: dict or None
        :param change_type: Type of change (emergency, normal, standard, model).
        :type change_type: str or None

        :return: JSON response containing information about the updated change request.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If change_type is specified but not valid.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.name_value_pairs is None:
            raise MissingParameterError
        if change_request.change_type:
            change_type = f'/{change_request.change_type}'
        elif change_request.change_type is None:
            change_type = ''
        else:
            raise ParameterError
        try:
            response = self._session.patch(url=f'{self.url}/sn_chg_rest'
                                               f'/change{change_type}/{change_request.change_request_sys_id}',
                                           headers=self.headers,
                                           data=change_request.data,
                                           verify=self.verify,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_change_request_first_available(self, **kwargs):
        """
        Update the schedule of a change request to the first available slot.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None

        :return: JSON response containing information about the updated schedule.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.patch(url=f'{self.url}'
                                               f'/sn_chg_rest/change/{change_request.change_request_sys_id}'
                                               f'/schedule/first_available',
                                           headers=self.headers,
                                           verify=self.verify,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_change_request_task(self, **kwargs):
        """
        Update details of a task associated with a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_request_task_sys_id: Sys ID of the change request task.
        :type change_request_task_sys_id: str or None
        :param name_value_pairs: New name-value pairs providing updated details for the task.
        :type name_value_pairs: dict or None

        :return: JSON response containing information about the updated task.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id, change_request_task_sys_id, or name_value_pairs is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON serialization or deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if (change_request.change_request_sys_id is None
                or change_request.change_request_task_sys_id is None
                or change_request.name_value_pairs is None):
            raise MissingParameterError
        try:
            response = self._session.patch(url=f'{self.url}'
                                               f'/sn_chg_rest/change/{change_request.change_request_sys_id}'
                                               f'/task/{change_request.change_request_task_sys_id}',
                                           headers=self.headers,
                                           data=change_request.data,
                                           verify=self.verify,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def delete_change_request(self, **kwargs):
        """
        Delete a change request.

        :param change_request_sys_id: Sys ID of the change request.
        :type change_request_sys_id: str or None
        :param change_type: Type of change (emergency, normal, standard).
        :type change_type: str or None

        :return: JSON response containing information about the deleted change request.
        :rtype: dict

        :raises MissingParameterError: If change_request_sys_id is not provided.
        :raises ParameterError: If invalid parameters or responses are encountered.
        :raises ParameterError: If JSON deserialization fails.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_type:
            try:
                response = self._session.delete(url=f'{self.url}/sn_chg_rest'
                                                    f'/change/emergency/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif (change_request.change_type
              and change_request.change_type == 'normal'):
            try:
                response = self._session.delete(url=f'{self.url}/sn_chg_rest'
                                                    f'/change/normal/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif (change_request.change_type
              and change_request.change_type == 'standard'):
            try:
                response = self._session.delete(url=f'{self.url}/sn_chg_rest'
                                                    f'/change/standard/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        else:
            try:
                response = self._session.delete(url=f'{self.url}/sn_chg_rest'
                                                    f'/change/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def delete_change_request_task(self, **kwargs):
        """
        Delete a task associated with a change request.

        Args:
            change_request_sys_id (str): The system ID of the change request.
            task_sys_id (str): The system ID of the task associated with the change request.

        Raises:
            MissingParameterError: If either `change_request_sys_id` or `task_sys_id` is None.

        Returns:
            dict: JSON response from the deletion request.

        Note:
            This function requires authentication through the @require_auth decorator.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.task_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.delete(url=f'{self.url}/sn_chg_rest'
                                                f'/change/{change_request.change_request_sys_id}'
                                                f'/task/{change_request.task_sys_id}',
                                            headers=self.headers,
                                            verify=self.verify,
                                            proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def delete_change_request_conflict_scan(self, **kwargs):
        """
        Delete conflict scan information associated with a change request.

        Args:
            change_request_sys_id (str): The system ID of the change request.
            task_sys_id (str): The system ID of the task associated with the change request.

        Raises:
            MissingParameterError: If either `change_request_sys_id` or `task_sys_id` is None.

        Returns:
            dict: JSON response from the deletion request.

        Note:
            This function requires authentication through the @require_auth decorator.
        """
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.task_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.delete(url=f'{self.url}/sn_chg_rest'
                                                f'/change/{change_request.change_request_sys_id}/conflict',
                                            headers=self.headers,
                                            verify=self.verify,
                                            proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                             Import Set API                                                       #
    ####################################################################################################################
    @require_auth
    def get_import_set(self, **kwargs):
        """
        Get details of a specific import set record.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param import_set_sys_id: The sys_id of the import set record.
        :type import_set_sys_id: str

        :return: JSON response containing information about the import set record.
        :rtype: requests.models.Response

        :raises ParameterError: If import_set_sys_id or table is not provided.
        """
        import_set = ImportSetModel(**kwargs)
        if import_set.import_set_sys_id is None or import_set.table is None:
            raise ParameterError
        try:
            response = self._session.get(url=f'{self.url}/now/import/'
                                             f'{import_set.table}/{import_set.import_set_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def insert_import_set(self, **kwargs):
        """
        Insert a new record into the specified import set.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param data: Dictionary containing the field values for the new import set record.
        :type data: dict

        :return: JSON response containing information about the inserted import set record.
        :rtype: requests.models.Response

        :raises ParameterError: If data or table is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        import_set = ImportSetModel(**kwargs)
        if import_set.data is None or import_set.table is None:
            raise ParameterError
        try:
            response = self._session.post(url=f'{self.url}/now/import/{import_set.table}',
                                          headers=self.headers,
                                          data=import_set.data,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def insert_multiple_import_sets(self, **kwargs):
        """
        Insert multiple records into the specified import set.

        :param table: The name of the table associated with the import set.
        :type table: str
        :param data: Dictionary containing the field values for multiple new import set records.
        :type data: dict

        :return: JSON response containing information about the inserted import set records.
        :rtype: requests.models.Response

        :raises ParameterError: If data or table is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        import_set = ImportSetModel(**kwargs)
        if import_set.data is None or import_set.table is None:
            raise ParameterError
        try:
            response = self._session.post(url=f'{self.url}/now/import/{import_set.table}/insertMultiple',
                                          headers=self.headers,
                                          data=import_set.data,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                               Incident API                                                       #
    ####################################################################################################################
    @require_auth
    def get_incident(self, **kwargs):
        """
        Retrieve details of a specific incident record.

        :param kwargs: Keyword arguments to initialize an IncidentModel instance.
        :type kwargs: dict

        :return: JSON response containing information about the incident record.
        :rtype: requests.models.Response

        :raises MissingParameterError: If the incident_id is not provided.
        :raises ParameterError: If validation of parameters fails.
        """
        incident = IncidentModel(**kwargs)
        if incident.incident_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/now/table/incident/{incident.incident_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_incident(self, **kwargs):
        """
        Create a new incident record.

        :param kwargs: Keyword arguments to initialize an IncidentModel instance.
        :type kwargs: dict

        :return: JSON response containing information about the created incident record.
        :rtype: requests.models.Response

        :raises MissingParameterError: If data for the incident is not provided.
        :raises ParameterError: If JSON serialization of incident data fails.
        :raises ParameterError: If validation of parameters fails.
        """
        incident = IncidentModel(**kwargs)
        try:
            response = self._session.post(url=f'{self.url}/now/table/incident',
                                          headers=self.headers,
                                          verify=self.verify,
                                          data=incident.data)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                                  Table API                                                       #
    ####################################################################################################################
    @require_auth
    def delete_table_record(self, **kwargs):
        """
        Delete a record from the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be deleted.
        :type table_record_sys_id: str

        :return: JSON response containing information about the deletion.
        :rtype: requests.models.Response

        :raises MissingParameterError: If table or table_record_sys_id is not provided.
        """
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.delete(url=f'{self.url}/now/table/{table.table}/{table.table_record_sys_id}',
                                            headers=self.headers,
                                            verify=self.verify,
                                            proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_table(self, **kwargs):
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

        :return: JSON response containing information about the retrieved records.
        :rtype: requests.models.Response

        :raises MissingParameterError: If table is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        table = TableModel(**kwargs)
        if table is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/now/table/{table.table}{table.api_parameters}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_table_record(self, **kwargs):
        """
        Get a specific record from the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be retrieved.
        :type table_record_sys_id: str

        :return: JSON response containing information about the retrieved record.
        :rtype: requests.models.Response

        :raises MissingParameterError: If table or table_record_sys_id is not provided.
        """
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(url=f'{self.url}/now/table/{table.table}/{table.table_record_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def patch_table_record(self, **kwargs):
        """
        Partially update a record in the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be updated.
        :type table_record_sys_id: str
        :param data: Dictionary containing the fields to be updated.
        :type data: dict

        :return: JSON response containing information about the update.
        :rtype: requests.models.Response

        :raises MissingParameterError: If table, table_record_sys_id, or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """

        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None or table.data is None:
            raise MissingParameterError
        try:
            response = self._session.patch(url=f'{self.url}/now/table/{table.table}/{table.table_record_sys_id}',
                                           data=table.data,
                                           headers=self.headers,
                                           verify=self.verify,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_table_record(self, **kwargs):
        """
        Fully update a record in the specified table.

        :param table: The name of the table.
        :type table: str
        :param table_record_sys_id: The sys_id of the record to be updated.
        :type table_record_sys_id: str
        :param data: Dictionary containing the fields to be updated.
        :type data: dict

        :return: JSON response containing information about the update.
        :rtype: requests.models.Response

        :raises MissingParameterError: If table, table_record_sys_id, or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None or table.data is None:
            raise MissingParameterError
        try:
            response = self._session.put(url=f'{self.url}/now/table/{table}/{table.table_record_sys_id}',
                                         data=table.data,
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def add_table_record(self, **kwargs):
        """
        Add a new record to the specified table.

        :param table: The name of the table.
        :type table: str
        :param data: Dictionary containing the field values for the new record.
        :type data: dict

        :return: JSON response containing information about the added record.
        :rtype: requests.models.Response

        :raises MissingParameterError: If table or data is not provided.
        :raises ParameterError: If JSON serialization fails.
        """
        table = TableModel(**kwargs)
        if table.table is None or table.data is None:
            raise MissingParameterError
        try:
            response = self._session.post(url=f'{self.url}/now/table/{table}',
                                          data=table.data,
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response
