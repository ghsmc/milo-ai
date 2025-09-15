"""
Yale Alumni API Package

This package contains the API endpoints for querying Yale alumni data.
"""

from .simple_api import simple_api
from .api_endpoints import api_app

__all__ = ['simple_api', 'api_app']
