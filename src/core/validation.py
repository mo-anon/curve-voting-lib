from typing import Protocol, Any
from enum import Enum

class VoteState(Enum):
    INITIALIZED = "initialized"
    SIMULATED = "simulated"
    VALIDATED = "validated"
    POSTED = "posted"

class Validator(Protocol):
    """Protocol for vote validators"""
    def validate(self, context: Any) -> bool:
        """Validate the vote conditions"""
        ...

class ValidationError(Exception):
    """Base exception for validation errors"""
    pass

def validate_vote_state(current_state: VoteState, required_state: VoteState):
    """Utility to check if vote is in correct state"""
    if current_state != required_state:
        raise ValidationError(f"Vote must be in {required_state} state, current: {current_state}")