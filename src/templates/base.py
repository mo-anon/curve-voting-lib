from typing import Dict, Any, List, Tuple, Optional
from src.core.vote import Vote
from src.core.validation import VoteState, ValidationError
from src.core.config import VoteConfig
from src.core.simulation import simulation_context
from src.core.create_vote import create_vote
import contextlib
import logging
from src.core.results import ValidationResult, SimulationResult

logger = logging.getLogger(__name__)


class VoteTemplate(Vote):
    """Base class for all vote templates"""
    
    def __init__(self, config: VoteConfig, description: str = ""):
        """
        Initialize a vote template
        
        Args:
            config: Vote configuration including API keys and environment settings
            description: Description of the vote
        """
        super().__init__()
        self.config = config
        self.description = description
        self.vote_payload: List[Tuple] = []
        
    def validate(self, show_info=False) -> ValidationResult:
        """
        Validate the vote conditions by calling the subclass's _validate method
        Returns:
            ValidationResult: Result object with success and errors
        """
        try:
            result = self._validate(show_info=show_info)
            if isinstance(result, ValidationResult):
                return result
            elif isinstance(result, bool):
                return ValidationResult(success=result)
            else:
                return ValidationResult(success=False, errors=["Unknown validation result type"])
        except Exception as e:
            return ValidationResult(success=False, errors=[str(e)])
        
    def _validate(self, show_info=False) -> bool:
        """
        Validate the vote conditions - to be implemented by subclasses
        
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError("This should be implemented by subclasses")
        
    def _simulate(self, show_info=False) -> Dict[str, Any]:
        """
        Simulate the vote
        
        Returns:
            Dict[str, Any]: Simulation results including success status and any errors
        """
        raise NotImplementedError("This should be implemented by subclasses")
        
    def __simulate(self, show_info=False) -> Dict[str, Any]:
        """
        Private method to run simulation in the correct context
        """
        # Only use simulation context if in forked mode
        context = simulation_context() if self.config.is_forked else contextlib.nullcontext()
        
        with context:
            return self._simulate(show_info=show_info)
    
    def simulate(self, show_info=False, skip_validation=False) -> SimulationResult:
        """
        Public method to simulate the vote
        Returns:
            SimulationResult: Result object with success, message, details, error
        """
        logger.info("Starting vote simulation")
        if not skip_validation:
            validation = self.validate(show_info=show_info)
            if not validation.success:
                return SimulationResult(success=False, message="Validation failed", error="; ".join(validation.errors))
        try:
            result = self.__simulate(show_info=show_info)
            if isinstance(result, SimulationResult):
                if result.success:
                    self.state = VoteState.SIMULATED
                    logger.info("Vote simulation completed successfully")
                else:
                    logger.error(f"Vote simulation failed: {result.error}")
                return result
            elif isinstance(result, dict):
                if result.get("success"):
                    self.state = VoteState.SIMULATED
                    logger.info("Vote simulation completed successfully")
                else:
                    logger.error(f"Vote simulation failed: {result.get('error', 'Unknown error')}")
                return SimulationResult(**result)
            else:
                return SimulationResult(success=False, message="Unknown simulation result type")
        except Exception as e:
            logger.error(f"Simulation exception: {str(e)}")
            return SimulationResult(success=False, message="Simulation exception", error=str(e))
            
    def post(self, vote_creator_address: Optional[str] = None) -> dict:
        """
        Create and post the vote to the chain
        Args:
            vote_creator_address: Address of the vote creator (required for live posting)
        Returns:
            dict: Vote creation results including vote ID and status
        """
        logger.info("Starting vote posting process")
        try:
            validation = self.validate()
            if not validation.success:
                return {
                    "success": False,
                    "stage": "validation",
                    "errors": validation.errors,
                    "message": validation.message
                }
            simulation = self.simulate()
            if not simulation.success:
                return {
                    "success": False,
                    "stage": "simulation",
                    "error": simulation.error,
                    "message": simulation.message
                }
            is_simulation = self.config.is_forked or vote_creator_address is None
            if is_simulation:
                vote_id = create_vote(
                    dao=DAO.OWNERSHIP,
                    actions=self.vote_payload,
                    description=self.description,
                    etherscan_api_key=self.config.etherscan_api_key,
                    pinata_token=self.config.pinata_token,
                    is_simulation=True
                )
                mode = "simulation"
            else:
                raise NotImplementedError("Live vote posting is not implemented yet. 'post_vote' function is missing.")
            self.state = VoteState.POSTED
            logger.info(f"Vote created successfully in {mode} mode with ID: {vote_id}")
            return {
                "success": True,
                "message": f"Vote created successfully in {mode} mode",
                "vote_id": vote_id,
                "mode": mode,
                "payload": {
                    "vote_id": vote_id,
                    "description": self.description,
                    "actions": self.vote_payload
                }
            }
        except Exception as e:
            logger.error(f"Failed to create vote: {str(e)}")
            return {
                "success": False,
                "stage": "exception",
                "message": f"Failed to create vote: {str(e)}",
                "error": str(e)
            }
