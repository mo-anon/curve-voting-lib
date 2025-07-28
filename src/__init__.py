"""
Curve DAO Vote Package

A Python package to simplify the creation, validation and simulation of Curve DAO votes.
"""

# Core imports
from .core.config import get_config
from .core.create_vote import create_vote

# Template imports
from .templates.gauge import AddGauge, KillGauge

# Utility imports
from .utils.constants import DAO, get_dao_parameters

__version__ = "0.1.0"
__author__ = "mo"
__email__ = "moanonresearch@gmail.com"

__all__ = [
    "get_config",
    "create_vote", 
    "AddGauge",
    "KillGauge",
    "DAO",
    "get_dao_parameters",
] 