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

        response = self._session.get(f'{self.url}/subscribers',
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
        application = ApplicationServiceModel(**kwargs)
        try:
            response = self._session.get(f'{self.url}/cmdb/app_service/'
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
        cmdb = CMDBModel(**kwargs)
        try:
            response = self._session.get(f'{self.url}/cmdb/meta/{cmdb.cmdb_id}',
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
        cicd = CICDModel(**kwargs)
        if cicd.result_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_cicd/app/batch/results/{cicd.result_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def instance_scan_progress(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.progress_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_cicd/instance_scan/result/{cicd.progress_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def progress(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.progress_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_cicd/progress/{cicd.progress_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def batch_install(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.name is None or cicd.packages is None:
            raise MissingParameterError
        data = {'name': cicd.name, 'packages': cicd.packages}
        try:
            response = self._session.post(f'{self.url}/sn_cicd/app/batch/install',
                                          headers=self.headers,
                                          verify=self.verify,
                                          data=cicd.data,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def batch_rollback(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.rollback_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_cicd/app/batch/rollback/{cicd.rollback_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def app_repo_install(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None:
            raise MissingParameterError
        if cicd.app_sys_id:
            parameters = f'?sys_id={cicd.app_sys_id}'
        else:
            parameters = f'?scope={cicd.scope}'
        if cicd.auto_upgrade_base_app:
            if isinstance(cicd.auto_upgrade_base_app, bool):
                parameters = f'{parameters}&auto_upgrade_base_app={str(cicd.auto_upgrade_base_app).lower()}'
            else:
                raise ParameterError
        if cicd.base_app_version:
            parameters = f'{parameters}&base_app_version={cicd.base_app_version}'
        if cicd.version:
            parameters = f'{parameters}&version={cicd.version}'
        try:
            response = self._session.post(f'{self.url}/sn_cicd/app_repo/install{parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def app_repo_publish(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None:
            raise MissingParameterError
        if cicd.app_sys_id:
            parameters = f'?sys_id={cicd.app_sys_id}'
        else:
            parameters = f'?scope={cicd.scope}'
        if cicd.dev_notes:
            parameters = f'{parameters}&dev_notes={cicd.dev_notes}'
        if cicd.version:
            parameters = f'{parameters}&version={cicd.version}'
        try:
            response = self._session.post(f'{self.url}/sn_cicd/app_repo/publish{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def app_repo_rollback(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None or cicd.version is None:
            raise MissingParameterError
        if cicd.app_sys_id:
            parameters = f'?sys_id={cicd.app_sys_id}'
        else:
            parameters = f'?scope={cicd.scope}'
        if cicd.version:
            parameters = f'{parameters}&version={cicd.version}'
        try:
            response = self._session.post(f'{self.url}/sn_cicd/app_repo/rollback{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def full_scan(self):
        try:
            response = self._session.post(f'{self.url}/sn_cicd/instance_scan/full_scan',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def point_scan(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.target_sys_id is None or cicd.target_table is None:
            raise MissingParameterError
        parameters = f"?target_table={cicd.target_table}&target_sys_id={cicd.target_sys_id}"
        try:
            response = self._session.post(f'{self.url}/sn_cicd/instance_scan/point_scan{parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def combo_suite_scan(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.combo_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(f'{self.url}/sn_cicd/instance_scan/suite_scan/combo/{cicd.combo_sys_id}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def suite_scan(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.suite_sys_id is None or cicd.sys_ids is None:
            raise MissingParameterError
        data = {"app_scope_sys_ids": cicd.sys_ids}
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        try:
            response = self._session.post(
                f'{self.url}/sn_cicd/instance_scan/suite_scan/{cicd.suite_sys_id}/{cicd.scan_type}',
                headers=self.headers,
                data=cicd.data,
                verify=self.verify,
                proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def activate_plugin(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.plugin_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(f'{self.url}/sn_cicd/plugin/{cicd.plugin_id}/activate',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def rollback_plugin(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.plugin_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(f'{self.url}/sn_cicd/plugin/{cicd.plugin_id}/rollback',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def apply_remote_source_control_changes(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.app_sys_id is None and cicd.scope is None:
            raise MissingParameterError
        if cicd.app_sys_id:
            parameters = f'?app_sys_id={cicd.app_sys_id}'
        else:
            parameters = f'?scope={cicd.scope}'
        if cicd.auto_upgrade_base_app:
            if isinstance(cicd.auto_upgrade_base_app, bool):
                parameters = f'{parameters}&auto_upgrade_base_app={str(cicd.auto_upgrade_base_app).lower()}'
            else:
                raise ParameterError
        if cicd.branch_name:
            parameters = f'{parameters}&branch_name={cicd.branch_name}'
        try:
            response = self._session.post(f'{self.url}/sn_cicd/sc/apply_changes{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def import_repository(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.repo_url is None:
            raise MissingParameterError
        parameters = f'?repo_url={cicd.repo_url}'
        if cicd.auto_upgrade_base_app:
            if isinstance(cicd.auto_upgrade_base_app, bool):
                parameters = f'{parameters}&auto_upgrade_base_app={str(cicd.auto_upgrade_base_app).lower()}'
            else:
                raise ParameterError
        if cicd.branch_name:
            parameters = f'{parameters}&branch_name={cicd.branch_name}'
        if cicd.credential_sys_id:
            parameters = f'{parameters}&credential_sys_id={cicd.credential_sys_id}'
        if cicd.mid_server_sys_id:
            parameters = f'{parameters}&mid_server_sys_id={cicd.mid_server_sys_id}'
        try:
            response = self._session.post(f'{self.url}/sn_cicd/sc/import{cicd.api_parameters}',
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def run_test_suite(self, **kwargs):
        cicd = CICDModel(**kwargs)
        if cicd.test_suite_sys_id is None and cicd.test_suite_name is None:
            raise MissingParameterError
        if cicd.test_suite_sys_id:
            parameters = f'?test_suite_sys_id={cicd.test_suite_sys_id}'
        else:
            parameters = f'?test_suite_name={cicd.test_suite_name}'
        if cicd.browser_name:
            if isinstance(cicd.browser_name, str) and cicd.browser_name in ['any', 'chrome', 'firefox', 'edge', 'ie',
                                                                            'safari']:
                parameters = f'{parameters}&browser_name={cicd.browser_name}'
            else:
                raise ParameterError
        if cicd.browser_version:
            parameters = f'{parameters}&browser_version={cicd.browser_version}'
        if cicd.os_name:
            parameters = f'{parameters}&os_name={cicd.os_name}'
        if cicd.os_version:
            parameters = f'{parameters}&os_version={cicd.os_version}'
        try:
            response = self._session.post(f'{self.url}/sn_cicd/testsuite/run{cicd.api_parameters}',
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
        change_request = ChangeManagementModel(**kwargs)
        parameters = None
        page = 0
        if name_value_pairs:
            if parameters:
                parameters = f'{parameters}&{name_value_pairs}'
            else:
                parameters = f'?{name_value_pairs}'
        if sysparm_query:
            if order:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}ORDERBY{order}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}ORDERBY{order}'
            else:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}'
        elif order:
            if parameters:
                parameters = f'{parameters}&sysparm_query=ORDERBY{order}'
            else:
                parameters = f'?sysparm_query=ORDERBY{order}'
        if text_search:
            parameters = f'{parameters}&textSearch={text_search}'
        responses = None
        response_length = 10
        if change_type and isinstance(change_type, str) and change_type.lower() in ['emergency', 'normal', 'standard',
                                                                                    'model']:
            change_type = f'/{change_type.lower()}'
        elif change_type is None:
            change_type = ''
        else:
            raise ParameterError
        while response_length > 1:
            if not parameters:
                parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(f'{self.url}/sn_chg_rest/change{change_type}{parameters}{offset}',
                                                 headers=self.headers, verify=self.verify, proxies=self.proxies)
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
                responses = self._session.get(f'{self.url}/sn_chg_rest/change{change_request.change_type}'
                                              f'{change_request.api_parameters}{change_request.offset}',
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
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/nextstate',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_schedule(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if cmdb_ci_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/ci/{cmdb_ci_sys_id}/schedule',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_tasks(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        parameters = None
        page = 0
        if name_value_pairs:
            if parameters:
                parameters = f'{parameters}&{name_value_pairs}'
            else:
                parameters = f'?{name_value_pairs}'
        if sysparm_query:
            if order:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}ORDERBY{order}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}ORDERBY{order}'
            else:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}'
        elif order:
            if parameters:
                parameters = f'{parameters}&sysparm_query=ORDERBY{order}'
            else:
                parameters = f'?sysparm_query=ORDERBY{order}'
        if text_search:
            parameters = f'{parameters}&textSearch={text_search}'

        responses = None
        response_length = 10
        while response_length > 1:
            if not parameters:
                parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/'
                                                 f'task{parameters}{offset}',
                                                 headers=self.headers, verify=self.verify, proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    response_length = len(verified_response['result'])
                    if response_length > 1 and page < max_pages \
                            or response_length > 1 and max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    raise ParameterError
            else:
                responses = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/'
                                              f'task{parameters}{offset}',
                                              headers=self.headers, verify=self.verify, proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + per_page
        return responses

    @require_auth
    def get_change_request(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        if change_type and isinstance(change_type, str) and change_type.lower() == 'emergency':
            try:
                response = self._session.get(f'{self.url}/sn_chg_rest/change/emergency/{change_request_sys_id}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif change_type and isinstance(change_type, str) and change_type.lower() == 'normal':
            try:
                response = self._session.get(f'{self.url}/sn_chg_rest/change/normal/{change_request_sys_id}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif change_type and isinstance(change_type, str) and change_type.lower() == 'standard':
            try:
                response = self._session.get(f'{self.url}/sn_chg_rest/change/standard/{change_request_sys_id}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        else:
            try:
                response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_ci(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/ci',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_ci(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/conflict',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_standard_change_request_templates(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        parameters = None
        page = 0
        if name_value_pairs:
            if parameters:
                parameters = f'{parameters}&{name_value_pairs}'
            else:
                parameters = f'?{name_value_pairs}'
        if sysparm_query:
            if order:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}ORDERBY{order}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}ORDERBY{order}'
            else:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}'
        elif order:
            if parameters:
                parameters = f'{parameters}&sysparm_query=ORDERBY{order}'
            else:
                parameters = f'?sysparm_query=ORDERBY{order}'
        if text_search:
            parameters = f'{parameters}&textSearch={text_search}'
        responses = None
        response_length = 10
        while response_length > 1:
            if not parameters:
                parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(f'{self.url}/sn_chg_rest/change/standard/template{parameters}{offset}',
                                                 headers=self.headers, verify=self.verify, proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    if 'result' in verified_response:
                        response_length = len(verified_response['result'])
                    else:
                        return verified_response
                    if response_length > 1 and page < max_pages \
                            or response_length > 1 and max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    return verified_response
            else:
                responses = self._session.get(f'{self.url}/sn_chg_rest/change/standard/template{parameters}{offset}',
                                              headers=self.headers, verify=self.verify, proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + per_page
        return responses

    @require_auth
    def get_change_request_models(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        parameters = None
        page = 0
        if name_value_pairs:
            if parameters:
                parameters = f'{parameters}&{name_value_pairs}'
            else:
                parameters = f'?{name_value_pairs}'
        if sysparm_query:
            if order:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}ORDERBY{order}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}ORDERBY{order}'
            else:
                if parameters:
                    parameters = f'{parameters}&sysparm_query={sysparm_query}'
                else:
                    parameters = f'?sysparm_query={sysparm_query}'
        elif order:
            if parameters:
                parameters = f'{parameters}&sysparm_query=ORDERBY{order}'
            else:
                parameters = f'?sysparm_query=ORDERBY{order}'
        if text_search:
            parameters = f'{parameters}&textSearch={text_search}'
        responses = None
        response_length = 10
        while response_length > 1:
            if not parameters:
                parameters = ''
                offset = f'?sysparm_offset={page}'
            else:
                offset = f'&sysparm_offset={page}'
            if responses:
                try:
                    response = self._session.get(f'{self.url}/sn_chg_rest/change/model{parameters}{offset}',
                                                 headers=self.headers, verify=self.verify, proxies=self.proxies)
                except ValidationError as e:
                    raise ParameterError(f"Invalid parameters: {e.errors()}")
                try:
                    verified_response = response.json()
                    response_length = len(verified_response['result'])
                    if response_length > 1 and page < max_pages \
                            or response_length > 1 and max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    raise ParameterError
            else:
                responses = self._session.get(f'{self.url}/sn_chg_rest/change/model{parameters}{offset}',
                                              headers=self.headers, verify=self.verify, proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + per_page
        return responses

    @require_auth
    def get_standard_change_request_model(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if model_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/model/{model_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_standard_change_request_template(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if template_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/standard/template/{template_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_change_request_worker(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if worker_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/worker/{worker_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_change_request(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if name_value_pairs is None:
            raise MissingParameterError
        try:
            data = json.dumps(name_value_pairs, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        if standard_change_template_id:
            standard_change_template_id = f'/{standard_change_template_id}'
        else:
            standard_change_template_id = ''
        if change_type and isinstance(change_type, str) and change_type.lower() in ['emergency', 'normal', 'standard']:
            change_type = f'/{change_type.lower()}'
        else:
            change_type = ''
        print(f"URI: {self.url}/sn_chg_rest/change{change_type}{standard_change_template_id}")
        try:
            response = self._session.post(f'{self.url}/sn_chg_rest/change{change_type}{standard_change_template_id}',
                                          headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_change_request_task(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None or name_value_pairs is None:
            raise MissingParameterError
        try:
            data = json.dumps(name_value_pairs, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        try:
            response = self._session.post(f'{self.url}/sn_chg_rest/change/task', headers=self.headers, data=data,
                                          verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_change_request_ci_association(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None or cmdb_ci_sys_ids is None or association_type is None:
            raise MissingParameterError
        data = {}
        if isinstance(association_type, str) and association_type in ['affected', 'impacted', 'offering']:
            data['association_type'] = association_type
        else:
            raise ParameterError
        if isinstance(refresh_impacted_services, bool) and association_type == 'affected':
            data['refresh_impacted_services'] = refresh_impacted_services
        data['cmdb_ci_sys_ids'] = cmdb_ci_sys_ids
        try:
            data = json.dumps(data, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        try:
            response = self._session.post(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/ci',
                                          headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def calculate_standard_change_request_risk(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.patch(f'{self.url}/sn_chg_rest/change/standard/{change_request_sys_id}/risk',
                                           headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def check_change_request_conflict(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/conflict',
                                          headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def refresh_change_request_impacted_services(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.post(f'{self.url}'
                                          f'/sn_chg_rest/change/{change_request_sys_id}/refresh_impacted_services',
                                          headers=self.headers, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def approve_change_request(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None or state is None:
            raise MissingParameterError
        data = {}
        if isinstance(state, str) and state.lower() in ['approved', 'rejected']:
            data['state'] = state
        else:
            raise ParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        try:
            response = self._session.patch(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/approvals',
                                           headers=self.headers, verify=self.verify, data=data, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_change_request(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request_sys_id is None or name_value_pairs is None:
            raise MissingParameterError
        try:
            data = json.dumps(name_value_pairs, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        if change_type and isinstance(change_type, str) and change_type.lower() in ['emergency', 'normal', 'standard',
                                                                                    'model']:
            change_type = f'/{change_type.lower()}'
        elif change_type is None:
            change_type = ''
        else:
            raise ParameterError
        try:
            response = self._session.patch(f'{self.url}/sn_chg_rest/change{change_type}/{change_request_sys_id}',
                                           headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_change_request_first_available(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.patch(f'{self.url}'
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
        change_request = ChangeManagementModel(**kwargs)
        if (change_request.change_request_sys_id is None
                or change_request.change_request_task_sys_id is None
                or change_request.name_value_pairs is None):
            raise MissingParameterError
        try:
            data = json.dumps(change_request.name_value_pairs, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        try:
            response = self._session.patch(f'{self.url}'
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
        change_request = ChangeManagementModel(**kwargs)
        if (change_request.change_type and isinstance(change_request.change_type, str)
                and change_request.change_type.lower() == 'emergency'):
            try:
                response = self._session.delete(f'{self.url}/sn_chg_rest'
                                                f'/change/emergency/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif (change_request.change_type and isinstance(change_request.change_type, str)
              and change_request.change_type.lower() == 'normal'):
            try:
                response = self._session.delete(f'{self.url}/sn_chg_rest'
                                                f'/change/normal/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        elif (change_request.change_type and isinstance(change_request.change_type, str)
              and change_request.change_type.lower() == 'standard'):
            try:
                response = self._session.delete(f'{self.url}/sn_chg_rest'
                                                f'/change/standard/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        else:
            try:
                response = self._session.delete(f'{self.url}/sn_chg_rest'
                                                f'/change/{change_request.change_request_sys_id}',
                                                headers=self.headers,
                                                verify=self.verify,
                                                proxies=self.proxies)
            except ValidationError as e:
                raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def delete_change_request_task(self, **kwargs):
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.task_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.delete(f'{self.url}/sn_chg_rest'
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
        change_request = ChangeManagementModel(**kwargs)
        if change_request.change_request_sys_id is None or change_request.task_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.delete(f'{self.url}/sn_chg_rest'
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
        import_set = ImportSetModel(**kwargs)
        if import_set.import_set_sys_id is None or import_set.table is None:
            raise ParameterError
        try:
            response = self._session.get(f'{self.url}/now/import/'
                                         f'{import_set.table}/{import_set.import_set_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def insert_import_set(self, **kwargs):
        import_set = ImportSetModel(**kwargs)
        if import_set.data is None or import_set.table is None:
            raise ParameterError
        try:
            data = json.dumps(import_set.data, indent=4)
        except ValueError:
            raise ParameterError
        try:
            response = self._session.post(f'{self.url}/now/import/{import_set.table}',
                                          headers=self.headers,
                                          data=import_set.data,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def insert_multiple_import_sets(self, **kwargs):
        import_set = ImportSetModel(**kwargs)
        if import_set.data is None or import_set.table is None:
            raise ParameterError
        try:
            data = json.dumps(import_set.data, indent=4)
        except ValueError:
            raise ParameterError
        try:
            response = self._session.post(f'{self.url}/now/import/{import_set.table}/insertMultiple',
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
        incident = IncidentModel(**kwargs)
        if incident.incident_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/now/table/incident/{incident.incident_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def create_incident(self, **kwargs):
        incident = IncidentModel(**kwargs)
        if incident.data:
            try:
                data = json.dumps(incident.data, indent=4)
            except ValueError:
                raise ParameterError
        else:
            raise MissingParameterError
        try:
            response = self._session.post(f'{self.url}/now/table/incident',
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
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.delete(f'{self.url}/now/table/{table.table}/{table.table_record_sys_id}',
                                            headers=self.headers,
                                            verify=self.verify,
                                            proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_table(self, **kwargs):
        table = TableModel(**kwargs)
        if table is None:
            raise MissingParameterError
        parameters = None
        if table.name_value_pairs:
            if parameters:
                parameters = f'{parameters}&{table.name_value_pairs}'
            else:
                parameters = f'?{table.name_value_pairs}'
        if table.sysparm_display_value:
            if table.sysparm_display_value in [True, False, 'all']:
                if parameters:
                    parameters = f'{parameters}&sysparm_display_value={table.sysparm_display_value}'
                else:
                    parameters = f'?sysparm_display_value={table.sysparm_display_value}'
            else:
                raise ParameterError
        if table.sysparm_exclude_reference_link:
            if isinstance(table.sysparm_exclude_reference_link, bool):
                if parameters:
                    parameters = f'{parameters}&sysparm_exclude_reference_link={str(table.sysparm_display_value).lower()}'
                else:
                    parameters = f'?sysparm_exclude_reference_link={str(table.sysparm_display_value).lower()}'
            else:
                raise ParameterError
        if table.sysparm_fields:
            if isinstance(table.sysparm_fields, str):
                if parameters:
                    parameters = f'{parameters}&sysparm_fields={table.sysparm_fields}'
                else:
                    parameters = f'?sysparm_fields={table.sysparm_fields}'
            else:
                raise ParameterError
        if table.sysparm_limit:
            if isinstance(table.sysparm_limit, int):
                if parameters:
                    parameters = f'{parameters}&sysparm_limit={table.sysparm_limit}'
                else:
                    parameters = f'?sysparm_limit={table.sysparm_limit}'
            else:
                raise ParameterError
        if table.sysparm_no_count:
            if isinstance(table.sysparm_no_count, bool):
                if parameters:
                    parameters = f'{parameters}&sysparm_no_count={str(sysparm_no_count).lower()}'
                else:
                    parameters = f'?sysparm_no_count={str(sysparm_no_count).lower()}'
            else:
                raise ParameterError
        if sysparm_offset:
            if isinstance(sysparm_offset, int):
                if parameters:
                    parameters = f'{parameters}&sysparm_offset={sysparm_offset}'
                else:
                    parameters = f'?sysparm_offset={sysparm_offset}'
            else:
                raise ParameterError
        if sysparm_query:
            if parameters:
                parameters = f'{parameters}&sysparm_query={sysparm_query}'
            else:
                parameters = f'?sysparm_query={sysparm_query}'
        if sysparm_query_category:
            if isinstance(sysparm_query_category, str):
                if parameters:
                    parameters = f'{parameters}&sysparm_query_category={sysparm_query_category}'
                else:
                    parameters = f'?sysparm_query_category={sysparm_query_category}'
            else:
                raise ParameterError
        if sysparm_query_no_domain:
            if isinstance(sysparm_query_no_domain, bool):
                if parameters:
                    parameters = f'{parameters}&sysparm_query_no_domain={str(sysparm_query_no_domain).lower()}'
                else:
                    parameters = f'?sysparm_query_no_domain={str(sysparm_query_no_domain).lower()}'
            else:
                raise ParameterError
        if sysparm_suppress_pagination_header:
            if isinstance(sysparm_suppress_pagination_header, bool):
                if parameters:
                    parameters = f'{parameters}&sysparm_suppress_pagination_header=' \
                                 f'{str(sysparm_suppress_pagination_header).lower()}'
                else:
                    parameters = f'?sysparm_suppress_pagination_header=' \
                                 f'{str(sysparm_suppress_pagination_header).lower()}'
            else:
                raise ParameterError
        if sysparm_view:
            if isinstance(sysparm_view, str) and sysparm_view in ['desktop', 'mobile', 'both']:
                if parameters:
                    parameters = f'{parameters}&sysparm_view={sysparm_view}'
                else:
                    parameters = f'?sysparm_view={sysparm_view}'
            else:
                raise ParameterError
        try:
            response = self._session.get(f'{self.url}/now/table/{table.table}{table.api_parameters}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_table_record(self, **kwargs):
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None:
            raise MissingParameterError
        try:
            response = self._session.get(f'{self.url}/now/table/{table.table}/{table.table_record_sys_id}',
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def patch_table_record(self, **kwargs):
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None or table.data is None:
            raise MissingParameterError
        try:
            data = json.dumps(table.data, indent=4)
        except ValueError:
            raise ParameterError
        try:
            response = self._session.patch(f'{self.url}/now/table/{table.table}/{table.table_record_sys_id}',
                                           data=table.data,
                                           headers=self.headers,
                                           verify=self.verify,
                                           proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def update_table_record(self, **kwargs):
        table = TableModel(**kwargs)
        if table.table is None or table.table_record_sys_id is None or table.data is None:
            raise MissingParameterError
        try:
            data = json.dumps(table.data, indent=4)
        except ValueError:
            raise ParameterError
        try:
            response = self._session.put(f'{self.url}/now/table/{table}/{table.table_record_sys_id}',
                                         data=table.data,
                                         headers=self.headers,
                                         verify=self.verify,
                                         proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def add_table_record(self, **kwargs):
        table = TableModel(**kwargs)
        if table.table is None or table.data is None:
            raise MissingParameterError
        try:
            data = json.dumps(table.data, indent=4)
        except ValueError:
            raise ParameterError
        try:
            response = self._session.post(f'{self.url}/now/table/{table}',
                                          data=table.data,
                                          headers=self.headers,
                                          verify=self.verify,
                                          proxies=self.proxies)
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response
