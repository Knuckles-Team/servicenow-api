#!/usr/bin/python
# coding: utf-8
from typing import Union

import requests

try:
    from servicenow_api.servicenow_models import (
        Response,
    )
except ModuleNotFoundError:
    from servicenow_models import (
        Response,
    )


def process_response(response: requests.Response) -> Union[Response, requests.Response]:
    try:
        response.raise_for_status()
    except Exception as response_error:
        print(f"Response Error: {response_error}")
    status_code = response.status_code
    raw_output = response.content
    try:
        response = response.json()
    except Exception as response_error:
        print(f"JSON Conversion Error: {response_error}")
    try:
        response = Response(
            **response,
            status_code=status_code,
            raw_output=raw_output,
            json_output=response,
        )
    except Exception as response_error:
        print(f"Response Model Application Error: {response_error}")

    return response
