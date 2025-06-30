"""
LINE API Integration Library.

A comprehensive, type-safe Python library for integrating with LINE's APIs.
"""

from .core import LineAPIConfig
from .messaging import LineMessagingClient, TextMessage

__version__ = "0.1.0"

__all__ = [
    "LineAPIConfig",
    "LineMessagingClient",
    "TextMessage",
]
