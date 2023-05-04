#!/usr/bin/python
# coding: utf-8

import json
import requests
import urllib3
from base64 import b64encode

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

        response = self._session.get(f'{self.url}/subscribers', headers=self.headers, verify=self.verify,
                                     proxies=self.proxies)

        if response.status_code == 403:
            raise UnauthorizedError
        elif response.status_code == 401:
            raise AuthError
        elif response.status_code == 404:
            raise ParameterError

    ####################################################################################################################
    #                                               Incident API                                                       #
    ####################################################################################################################
    @require_auth
    def get_incident(self, incident_id: str = None):
        if incident_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/now/table/incident/{incident_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def create_incident(self, data: dict = None):
        if data:
            try:
                data = json.dumps(data, indent=4)
            except ValueError:
                raise ParameterError
        else:
            raise MissingParameterError
        response = self._session.post(f'{self.url}/now/table/incident', headers=self.headers, verify=self.verify,
                                      data=data)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    ####################################################################################################################
    #                                         Application Service API                                                  #
    ####################################################################################################################
    @require_auth
    def get_application(self, application_id: str = None):
        if application_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/cmdb/app_service/{application_id}/getContent?mode=full',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    ####################################################################################################################
    #                                                   CMDB API                                                       #
    ####################################################################################################################
    @require_auth
    def get_cmdb(self, cmdb_id: str = None):
        if cmdb_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/cmdb/meta/{cmdb_id}', headers=self.headers, verify=self.verify,
                                     proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    ####################################################################################################################
    #                                                  CI/CD API                                                       #
    ####################################################################################################################
    @require_auth
    def batch_install_result(self, result_id: str = None):
        if result_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_cicd/app/batch/results/{result_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def instance_scan_progress(self, progress_id: str = None):
        if progress_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_cicd/instance_scan/result/{progress_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def progress(self, progress_id: str = None):
        if progress_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_cicd/progress/{progress_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def batch_install(self, name: str = None, notes: str = None, packages: str = None):
        if name is None or packages is None:
            raise MissingParameterError
        data = {}
        data['name'] = name
        data['packages'] = packages
        if notes:
            if isinstance(notes, str):
                data['notes'] = notes
            else:
                raise ParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.post(f'{self.url}/sn_cicd/app/batch/install', headers=self.headers, verify=self.verify,
                                      data=data, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def batch_rollback(self, rollback_id: str = None):
        if rollback_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_cicd/app/batch/rollback/{rollback_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def app_repo_install(self, app_sys_id: str = None, scope: str = None, auto_upgrade_base_app: bool = None,
                         base_app_version: str = None, version: str = None):
        if app_sys_id is None and scope is None:
            raise MissingParameterError
        if app_sys_id:
            parameters = f'?sys_id={app_sys_id}'
        else:
            parameters = f'?scope={scope}'
        if auto_upgrade_base_app:
            if isinstance(auto_upgrade_base_app, bool):
                parameters = f'{parameters}&auto_upgrade_base_app={str(auto_upgrade_base_app).lower()}'
            else:
                raise ParameterError
        if base_app_version:
            parameters = f'{parameters}&base_app_version={base_app_version}'
        if version:
            parameters = f'{parameters}&version={version}'
        response = self._session.post(f'{self.url}/sn_cicd/app_repo/install{parameters}', headers=self.headers,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def app_repo_publish(self, app_sys_id: str = None, scope: str = None, dev_notes: str = None, version: str = None):
        if app_sys_id is None and scope is None:
            raise MissingParameterError
        if app_sys_id:
            parameters = f'?sys_id={app_sys_id}'
        else:
            parameters = f'?scope={scope}'
        if dev_notes:
            parameters = f'{parameters}&dev_notes={dev_notes}'
        if version:
            parameters = f'{parameters}&version={version}'
        response = self._session.post(f'{self.url}/sn_cicd/app_repo/publish{parameters}', headers=self.headers,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def app_repo_rollback(self, app_sys_id: str = None, scope: str = None, version: str = None):
        if app_sys_id is None and scope is None or version is None:
            raise MissingParameterError
        if app_sys_id:
            parameters = f'?sys_id={app_sys_id}'
        else:
            parameters = f'?scope={scope}'
        if version:
            parameters = f'{parameters}&version={version}'
        response = self._session.post(f'{self.url}/sn_cicd/app_repo/rollback{parameters}',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def full_scan(self):
        response = self._session.post(f'{self.url}/sn_cicd/instance_scan/full_scan', headers=self.headers,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def point_scan(self, target_sys_id: str = None, target_table: str = None):
        if target_sys_id is None or target_table is None:
            raise MissingParameterError
        parameters = f"?target_table={target_table}&target_sys_id={target_sys_id}"
        response = self._session.post(f'{self.url}/sn_cicd/instance_scan/point_scan{parameters}',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def combo_suite_scan(self, combo_sys_id: str = None):
        if combo_sys_id is None:
            raise MissingParameterError
        response = self._session.post(f'{self.url}/sn_cicd/instance_scan/suite_scan/combo/{combo_sys_id}',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def suite_scan(self, suite_sys_id: str = None, sys_ids: list = None, scan_type: str = "scoped_apps"):
        if suite_sys_id is None or sys_ids is None:
            raise MissingParameterError
        data = {"app_scope_sys_ids": sys_ids}
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.post(f'{self.url}/sn_cicd/instance_scan/suite_scan/{suite_sys_id}/{scan_type}',
                                      headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def activate_plugin(self, plugin_id: str = None):
        if plugin_id is None:
            raise MissingParameterError
        response = self._session.post(f'{self.url}/sn_cicd/plugin/{plugin_id}/activate',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def rollback_plugin(self, plugin_id: str = None):
        if plugin_id is None:
            raise MissingParameterError
        response = self._session.post(f'{self.url}/sn_cicd/plugin/{plugin_id}/rollback',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def apply_remote_source_control_changes(self, app_sys_id: str = None, scope: str = None, branch_name: str = None,
                                            auto_upgrade_base_app: bool = None):
        if app_sys_id is None and scope is None:
            raise MissingParameterError
        if app_sys_id:
            parameters = f'?app_sys_id={app_sys_id}'
        else:
            parameters = f'?scope={scope}'
        if auto_upgrade_base_app:
            if isinstance(auto_upgrade_base_app, bool):
                parameters = f'{parameters}&auto_upgrade_base_app={str(auto_upgrade_base_app).lower()}'
            else:
                raise ParameterError
        if branch_name:
            parameters = f'{parameters}&branch_name={branch_name}'
        response = self._session.post(f'{self.url}/sn_cicd/sc/apply_changes{parameters}', headers=self.headers,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def import_repository(self, credential_sys_id: str = None, mid_server_sys_id: str = None, repo_url: str = None,
                          branch_name: str = None, auto_upgrade_base_app: bool = None):
        if repo_url is None:
            raise MissingParameterError
        parameters = f'?repo_url={repo_url}'
        if auto_upgrade_base_app:
            if isinstance(auto_upgrade_base_app, bool):
                parameters = f'{parameters}&auto_upgrade_base_app={str(auto_upgrade_base_app).lower()}'
            else:
                raise ParameterError
        if branch_name:
            parameters = f'{parameters}&branch_name={branch_name}'
        if credential_sys_id:
            parameters = f'{parameters}&credential_sys_id={credential_sys_id}'
        if mid_server_sys_id:
            parameters = f'{parameters}&mid_server_sys_id={mid_server_sys_id}'
        response = self._session.post(f'{self.url}/sn_cicd/sc/import{parameters}', headers=self.headers,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def run_test_suite(self, test_suite_sys_id: str = None, test_suite_name: str = None, browser_name: str = None,
                       browser_version: str = None, os_name: str = None, os_version: str = None):
        if test_suite_sys_id is None and test_suite_name is None:
            raise MissingParameterError
        if test_suite_sys_id:
            parameters = f'?test_suite_sys_id={test_suite_sys_id}'
        else:
            parameters = f'?test_suite_name={test_suite_name}'
        if browser_name:
            if isinstance(browser_name, str) and browser_name in ['any', 'chrome', 'firefox', 'edge', 'ie', 'safari']:
                parameters = f'{parameters}&browser_name={browser_name}'
            else:
                raise ParameterError
        if browser_version:
            parameters = f'{parameters}&browser_version={browser_version}'
        if os_name:
            parameters = f'{parameters}&os_name={os_name}'
        if os_version:
            parameters = f'{parameters}&os_version={os_version}'
        response = self._session.post(f'{self.url}/sn_cicd/testsuite/run{parameters}', headers=self.headers,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    ####################################################################################################################
    #                                        Change Management API                                                     #
    ####################################################################################################################
    @require_auth
    def get_change_requests(self, order: str = None, name_value_pairs: dict = None, max_pages: int = 0,
                            per_page: int = 500, sysparm_query: str = None, text_search: str = None,
                            change_type: str = None):
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
                response = self._session.get(f'{self.url}/sn_chg_rest/change{change_type}{parameters}{offset}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
                try:
                    verified_response = response.json()
                    response_length = len(verified_response['result'])
                    if response_length > 1 and page < max_pages \
                            or response_length > 1 and max_pages == 0:
                        responses['result'] = responses['result'] + verified_response['result']
                except ValueError or AttributeError:
                    raise ParameterError
            else:
                responses = self._session.get(f'{self.url}/sn_chg_rest/change{change_type}{parameters}{offset}',
                                              headers=self.headers, verify=self.verify, proxies=self.proxies)
                try:
                    responses = responses.json()
                except ValueError or AttributeError:
                    raise ParameterError
            page = page + per_page
        return responses

    @require_auth
    def get_change_request_nextstate(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/nextstate',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_change_request_schedule(self, cmdb_ci_sys_id: str = None):
        if cmdb_ci_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/ci/{cmdb_ci_sys_id}/schedule',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_change_request_tasks(self, change_request_sys_id: str = None, order: str = None,
                                 name_value_pairs: dict = None, max_pages: int = 0, per_page: int = 500,
                                 sysparm_query: str = None, text_search: str = None):
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
                response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/'
                                             f'task{parameters}{offset}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
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
    def get_change_request(self, change_request_sys_id: str = None, change_type: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        if change_type and isinstance(change_type, str) and change_type.lower() == 'emergency':
            response = self._session.get(f'{self.url}/sn_chg_rest/change/emergency/{change_request_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        elif change_type and isinstance(change_type, str) and change_type.lower() == 'normal':
            response = self._session.get(f'{self.url}/sn_chg_rest/change/normal/{change_request_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        elif change_type and isinstance(change_type, str) and change_type.lower() == 'standard':
            response = self._session.get(f'{self.url}/sn_chg_rest/change/standard/{change_request_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        else:
            response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}',
                                         headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_change_request_ci(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/ci',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_change_request_ci(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/conflict',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_standard_change_request_templates(self, order: str = None, name_value_pairs: dict = None,
                                              max_pages: int = 0,
                                              per_page: int = 500, sysparm_query: str = None, text_search: str = None):
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
                response = self._session.get(f'{self.url}/sn_chg_rest/change/standard/template{parameters}{offset}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
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
    def get_change_request_models(self, order: str = None, name_value_pairs: dict = None, max_pages: int = 0,
                                  per_page: int = 500, sysparm_query: str = None, text_search: str = None):
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
                response = self._session.get(f'{self.url}/sn_chg_rest/change/model{parameters}{offset}',
                                             headers=self.headers, verify=self.verify, proxies=self.proxies)
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
    def get_standard_change_request_model(self, model_sys_id: str = None):
        if model_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/model/{model_sys_id}',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_standard_change_request_template(self, template_sys_id: str = None):
        if template_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/standard/template/{template_sys_id}',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_change_request_worker(self, worker_sys_id: str = None):
        if worker_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/sn_chg_rest/change/worker/{worker_sys_id}',
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def create_change_request(self, name_value_pairs: dict = None, change_type: str = None,
                              standard_change_template_id: str = None):
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
        response = self._session.post(f'{self.url}/sn_chg_rest/change{change_type}{standard_change_template_id}',
                                      headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def create_change_request_task(self, change_request_sys_id: str = None, name_value_pairs: dict = None):
        if change_request_sys_id is None or name_value_pairs is None:
            raise MissingParameterError
        try:
            data = json.dumps(name_value_pairs, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        response = self._session.post(f'{self.url}/sn_chg_rest/change/task', headers=self.headers, data=data,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def create_change_request_ci_association(self, change_request_sys_id: str = None, cmdb_ci_sys_ids: list = None,
                                             association_type: str = None, refresh_impacted_services: bool = None):
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
        response = self._session.post(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/ci',
                                      headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def calculate_standard_change_request_risk(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.patch(f'{self.url}/sn_chg_rest/change/standard/{change_request_sys_id}/risk',
                                       headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def check_change_request_conflict(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.post(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/conflict',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def refresh_change_request_impacted_services(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.post(f'{self.url}'
                                      f'/sn_chg_rest/change/{change_request_sys_id}/refresh_impacted_services',
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def approve_change_request(self, change_request_sys_id: str = None, state: str = None):
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
        response = self._session.patch(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/approvals',
                                       headers=self.headers, verify=self.verify, data=data, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def update_change_request(self, change_request_sys_id: str = None, name_value_pairs: dict = None,
                              change_type: str = None):
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
        response = self._session.patch(f'{self.url}/sn_chg_rest/change{change_type}/{change_request_sys_id}',
                                       headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def update_change_request_first_available(self, change_request_sys_id: str = None):
        if change_request_sys_id is None:
            raise MissingParameterError
        response = self._session.patch(f'{self.url}'
                                       f'/sn_chg_rest/change/{change_request_sys_id}/schedule/first_available',
                                       headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def update_change_request_task(self, change_request_sys_id: str = None, change_request_task_sys_id: str = None,
                                   name_value_pairs: dict = None):
        if change_request_sys_id is None or change_request_task_sys_id is None or name_value_pairs is None:
            raise MissingParameterError
        try:
            data = json.dumps(name_value_pairs, indent=4)
        except ValueError or AttributeError:
            raise ParameterError
        response = self._session.patch(f'{self.url}'
                                       f'/sn_chg_rest/change/{change_request_sys_id}/task/{change_request_task_sys_id}',
                                       headers=self.headers, data=data, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def delete_change_request(self, change_request_sys_id: str = None, change_type: str = None):
        if change_type and isinstance(change_type, str) and change_type.lower() == 'emergency':
            response = self._session.delete(f'{self.url}/sn_chg_rest/change/emergency/{change_request_sys_id}',
                                            headers=self.headers, verify=self.verify, proxies=self.proxies)
        elif change_type and isinstance(change_type, str) and change_type.lower() == 'normal':
            response = self._session.delete(f'{self.url}/sn_chg_rest/change/normal/{change_request_sys_id}',
                                            headers=self.headers, verify=self.verify, proxies=self.proxies)
        elif change_type and isinstance(change_type, str) and change_type.lower() == 'standard':
            response = self._session.delete(f'{self.url}/sn_chg_rest/change/standard/{change_request_sys_id}',
                                            headers=self.headers, verify=self.verify, proxies=self.proxies)
        else:
            response = self._session.delete(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}',
                                            headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def delete_change_request_task(self, change_request_sys_id: str = None, task_sys_id: str = None):
        if change_request_sys_id is None or task_sys_id is None:
            raise MissingParameterError
        response = self._session.delete(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/task/{task_sys_id}',
                                        headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def delete_change_request_conflict_scan(self, change_request_sys_id: str = None, task_sys_id: str = None):
        if change_request_sys_id is None or task_sys_id is None:
            raise MissingParameterError
        response = self._session.delete(f'{self.url}/sn_chg_rest/change/{change_request_sys_id}/conflict',
                                        headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    ####################################################################################################################
    #                                             Import Set API                                                       #
    ####################################################################################################################
    @require_auth
    def get_import_set(self, table: str = None, import_set_sys_id: str = None):
        if import_set_sys_id is None or table is None:
            raise ParameterError
        response = self._session.get(f'{self.url}/now/import/{table}/{import_set_sys_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def insert_import_set(self, table: str = None, data: dict = None):
        if data is None or table is None:
            raise ParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.post(f'{self.url}/now/import/{table}', headers=self.headers, data=data,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def insert_multiple_import_sets(self, table: str = None, data: dict = None):
        if data is None or table is None:
            raise ParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.post(f'{self.url}/now/import/{table}/insertMultiple', headers=self.headers, data=data,
                                      verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    ####################################################################################################################
    #                                                  Table API                                                       #
    ####################################################################################################################
    @require_auth
    def delete_table_record(self, table: str = None, table_record_sys_id: str = None):
        if table is None or table_record_sys_id is None:
            raise MissingParameterError
        response = self._session.delete(f'{self.url}/now/table/{table}/{table_record_sys_id}',
                                        headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_table(self, table: str = None, name_value_pairs: dict = None, sysparm_display_value: str = None,
                  sysparm_exclude_reference_link: bool = None, sysparm_fields: str = None, sysparm_limit: int = None,
                  sysparm_no_count: bool = None, sysparm_offset: int = None, sysparm_query: str = None,
                  sysparm_query_category: str = None, sysparm_query_no_domain: bool = None,
                  sysparm_suppress_pagination_header: bool = None, sysparm_view: str = None):
        if table is None:
            raise MissingParameterError
        parameters = None
        if name_value_pairs:
            if parameters:
                parameters = f'{parameters}&{name_value_pairs}'
            else:
                parameters = f'?{name_value_pairs}'
        if sysparm_display_value:
            if sysparm_display_value in [True, False, 'all']:
                if parameters:
                    parameters = f'{parameters}&sysparm_display_value={sysparm_display_value}'
                else:
                    parameters = f'?sysparm_display_value={sysparm_display_value}'
            else:
                raise ParameterError
        if sysparm_exclude_reference_link:
            if isinstance(sysparm_exclude_reference_link, bool):
                if parameters:
                    parameters = f'{parameters}&sysparm_exclude_reference_link={str(sysparm_display_value).lower()}'
                else:
                    parameters = f'?sysparm_exclude_reference_link={str(sysparm_display_value).lower()}'
            else:
                raise ParameterError
        if sysparm_fields:
            if isinstance(sysparm_fields, str):
                if parameters:
                    parameters = f'{parameters}&sysparm_fields={sysparm_fields}'
                else:
                    parameters = f'?sysparm_fields={sysparm_fields}'
            else:
                raise ParameterError
        if sysparm_limit:
            if isinstance(sysparm_limit, int):
                if parameters:
                    parameters = f'{parameters}&sysparm_limit={sysparm_limit}'
                else:
                    parameters = f'?sysparm_limit={sysparm_limit}'
            else:
                raise ParameterError
        if sysparm_no_count:
            if isinstance(sysparm_no_count, bool):
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
        response = self._session.get(f'{self.url}/now/table/{table}{parameters}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def get_table_record(self, table: str = None, table_record_sys_id: str = None):
        if table is None or table_record_sys_id is None:
            raise MissingParameterError
        response = self._session.get(f'{self.url}/now/table/{table}/{table_record_sys_id}', headers=self.headers,
                                     verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def patch_table_record(self, table: str = None, table_record_sys_id: str = None, data: dict = None):
        if table is None or table_record_sys_id is None or data is None:
            raise MissingParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.patch(f'{self.url}/now/table/{table}/{table_record_sys_id}', data=data,
                                       headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def update_table_record(self, table: str = None, table_record_sys_id: str = None, data: dict = None):
        if table is None or table_record_sys_id is None or data is None:
            raise MissingParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.put(f'{self.url}/now/table/{table}/{table_record_sys_id}', data=data,
                                     headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response

    @require_auth
    def add_table_record(self, table: str = None, data: dict = None):
        if table is None or data is None:
            raise MissingParameterError
        try:
            data = json.dumps(data, indent=4)
        except ValueError:
            raise ParameterError
        response = self._session.post(f'{self.url}/now/table/{table}', data=data,
                                      headers=self.headers, verify=self.verify, proxies=self.proxies)
        try:
            return response.json()
        except ValueError or AttributeError:
            return response
