#!/usr/bin/python
# coding: utf-8

import functools

try:
    from servicenow_api.exceptions import LoginRequiredError
except ModuleNotFoundError:
    from exceptions import LoginRequiredError


def require_auth(function):
    """
    Wraps API calls in function that ensures headers are passed
    with a token
    """

    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self.headers:
            raise LoginRequiredError
        return function(self, *args, **kwargs)

    return wrapper
