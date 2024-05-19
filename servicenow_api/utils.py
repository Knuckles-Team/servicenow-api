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
    try:
        response = response.json()
    except Exception as response_error:
        print(f"JSON Conversion Error: {response_error}")
    try:
        response = Response(**response)
    except Exception as response_error:
        print(f"Response Model Application Error: {response_error}")

    return response
