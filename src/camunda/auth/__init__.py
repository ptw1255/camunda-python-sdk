"""Authentication strategies for Camunda SDK."""

from camunda.auth.base import AuthStrategy, NoAuth
from camunda.auth.basic import BasicAuth
from camunda.auth.bearer import BearerToken
from camunda.auth.cookie import CookieAuth
from camunda.auth.oauth import OAuthCredentials

__all__ = [
    "AuthStrategy",
    "BasicAuth",
    "BearerToken",
    "CookieAuth",
    "NoAuth",
    "OAuthCredentials",
]
