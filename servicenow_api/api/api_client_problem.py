#!/usr/bin/python

import sys

from agent_utilities.core.exceptions import (
    MissingParameterError,
)
from pydantic import ValidationError

from servicenow_api.api.api_client_base import ServiceNowApiBase
from servicenow_api.servicenow_models import (
    Problem,
    ProblemModel,
    Response,
)


class ServiceNowApiProblem(ServiceNowApiBase):
    def get_problems(self, **kwargs) -> Response:
        """
        Retrieve details of problem records.

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

        :raises ParameterError: If input parameters are invalid.
        """
        try:
            problem = ProblemModel(**kwargs)
            response = self._session.get(
                url=f"{self.url}/now/table/problem",
                params=problem.api_parameters,
                headers=self.headers,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = [Problem.model_validate(item) for item in result_data]
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)
            raise

    def get_problem(self, **kwargs) -> Response:
        """
        Retrieve details of a specific problem record.

        :param problem_id: The sys_id of the problem record.
        :type problem_id: str

        :return: Response containing parsed Pydantic model with information about the retrieved record.
        :rtype: Response

        :raises MissingParameterError: If problem_id is not provided.
        :raises ParameterError: If input parameters are invalid.
        """
        try:
            problem = ProblemModel(**kwargs)
            if problem.problem_id is None:
                raise MissingParameterError
            response = self._session.get(
                url=f"{self.url}/now/table/problem/{problem.problem_id}",
                params=problem.api_parameters,
                headers=self.headers,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Problem.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)
            raise

    def create_problem(self, **kwargs) -> Response:
        """
        Create a new problem record.

        :param kwargs: Keyword arguments to initialize a ProblemModel instance.
        :type kwargs: dict

        :return: Response containing parsed Pydantic model with information about the created problem record.
        :rtype: Response

        :raises MissingParameterError: If data for the problem is not provided.
        :raises ParameterError: If validation of parameters fails.
        """
        try:
            problem = ProblemModel(**kwargs)
            if problem.data is None:
                raise MissingParameterError
            response = self._session.post(
                url=f"{self.url}/now/table/problem",
                headers=self.headers,
                json=problem.data,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Problem.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)
            raise

    def update_problem(self, **kwargs) -> Response:
        """
        Update an existing problem record.

        :param problem_id: The sys_id of the problem record to update.
        :type problem_id: str
        :param data: Dictionary of field values to update.
        :type data: dict

        :return: Response containing parsed Pydantic model with information about the updated problem record.
        :rtype: Response

        :raises MissingParameterError: If problem_id or data is not provided.
        :raises ParameterError: If validation of parameters fails.
        """
        try:
            problem = ProblemModel(**kwargs)
            if problem.problem_id is None or problem.data is None:
                raise MissingParameterError
            response = self._session.patch(
                url=f"{self.url}/now/table/problem/{problem.problem_id}",
                headers=self.headers,
                json=problem.data,
            )
            response.raise_for_status()
            json_response = response.json()
            result_data = json_response.get("result", json_response)
            parsed_data = Problem.model_validate(result_data)
            return Response(response=response, result=parsed_data)
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)
            raise

    def delete_problem(self, **kwargs) -> Response:
        """
        Delete a problem record.

        :param problem_id: The sys_id of the problem record to delete.
        :type problem_id: str

        :return: Response containing information about the deletion.
        :rtype: Response

        :raises MissingParameterError: If problem_id is not provided.
        """
        try:
            problem = ProblemModel(**kwargs)
            if problem.problem_id is None:
                raise MissingParameterError
            response = self._session.delete(
                url=f"{self.url}/now/table/problem/{problem.problem_id}",
                headers=self.headers,
            )
            response.raise_for_status()

            if response.content:
                json_response = response.json()
                result_data = json_response.get("result", json_response)
                return Response(response=response, result=result_data)
            return Response(response=response, result={"status": "deleted"})
        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)
            raise
