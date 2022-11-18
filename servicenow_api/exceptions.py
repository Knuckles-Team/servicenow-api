#!/usr/bin/python
# coding: utf-8

class AuthError(Exception):
    """
    Authentication error
    """
    pass


class UnauthorizedError(AuthError):
    """
    Unauthorized error
    """
    pass


class MissingParameterError(Exception):
    """
    Missing Parameter error
    """
    pass


class ParameterError(Exception):
    """
    Parameter error
    """
    pass


class LoginRequiredError(Exception):
    """
    Authentication error
    """
    pass
