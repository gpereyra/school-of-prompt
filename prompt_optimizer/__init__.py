"""Prompt Optimization Framework

A simple, powerful framework for optimizing prompts with minimal boilerplate.
"""

__version__ = "0.2.0"
__author__ = "Prompt Optimization Team"

# Simple API - the main entry point
from .optimize import optimize

# Extension points for advanced users
from .core.simple_interfaces import (
    CustomMetric,
    CustomDataSource,
    CustomModel,
    CustomTask
)

__all__ = [
    # Main API
    "optimize",
    
    # Extension interfaces
    "CustomMetric",
    "CustomDataSource", 
    "CustomModel",
    "CustomTask",
]