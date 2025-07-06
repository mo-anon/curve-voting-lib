from typing import Dict, Any
import re
import logging
import boa

from src.templates.base import VoteTemplate, ValidationResult, SimulationResult
from src.core.config import VoteConfig
from src.core.validation import VoteState
from src.utils.constants import GAUGE_CONTROLLER, get_dao_parameters, DAO, CONVEX_VOTERPROXY
from src.core.create_vote import create_vote

from rich.console import Console

logger = logging.getLogger(__name__)

console = Console()

class AddGauge(VoteTemplate):
    """Template for adding a gauge to the gauge controller"""
    
    def __init__(self, config: VoteConfig, gauge_address: str, weight: int, type_id: int, description: str = ""):
        """
        Initialize a gauge vote
        
        Args:
            config: Vote configuration including API keys and environment settings
            gauge_address: Address of the gauge to add
            weight: Weight to assign to the gauge
            type_id: Type ID for the gauge
            description: Description of the vote
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        self.weight = weight
        self.type_id = type_id
        
        # Create the vote payload - pass arguments directly
        self.vote_payload = [
            (
                GAUGE_CONTROLLER,
                "add_gauge",
                gauge_address,
                weight,
                type_id
            )
        ]
        
    def _validate(self, show_info=False) -> ValidationResult:
        """
        Perform static, local validation of input parameters.
        Only check input format, types, and ranges (e.g., address format, weight, type_id).
        Do NOT perform any onchain or stateful checks here—those belong in simulation.
        """
        errors = []
        if show_info:
            console.print(f"[bold cyan]Validating gauge address:[/] [white]{self.gauge_address}[/]")
        if not re.match(r"^0x[a-fA-F0-9]{40}$", self.gauge_address):
            errors.append("Invalid Ethereum address format.")
        if show_info:
            console.print(f"[bold cyan]Validating weight:[/] [white]{self.weight}[/]")
        if self.weight != 0:
            errors.append("Weight must be zero for new gauge.")
        if show_info:
            console.print(f"[bold cyan]Validating type_id:[/] [white]{self.type_id}[/]")
        if self.type_id != 0:
            errors.append("Type ID must be zero for new gauge.")
        
        # Do NOT check onchain state here!
        if errors:
            if show_info:
                for err in errors:
                    console.print(f"[bold red]Validation failed:[/] {err}")
            return ValidationResult(success=False, errors=errors)
        if show_info:
            console.print(f"[bold green]Validation passed![/]")
        return ValidationResult(success=True)

    def simulate(self, show_info=False, skip_validation=False, return_calldata=False):
        """
        Public method to simulate the vote
        Args:
            show_info: Show step-by-step info
            skip_validation: Skip validation step
            return_calldata: If True, include EVM script in SimulationResult.details
        Returns:
            SimulationResult
        """
        logger.info("Starting vote simulation")
        if not skip_validation:
            validation = self.validate(show_info=show_info)
            if not validation.success:
                return SimulationResult(success=False, message="Validation failed", error="; ".join(validation.errors))
        try:
            result = self._simulate(show_info=show_info, return_calldata=return_calldata)
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

    def _simulate(self, show_info=False, return_calldata=False) -> SimulationResult:
        """
        Perform simulation, including onchain state checks.
        Args:
            show_info: Show step-by-step info
            return_calldata: If True, include EVM script in SimulationResult.details
        Returns:
            SimulationResult
        """
        try:
            if show_info:
                console.print(f"[bold cyan]Starting gauge addition simulation[/]")
            boa.fork(self.config.get_rpc_url(), allow_dirty=True)

            voting = boa.load_abi("src/utils/abis/voting.json").at(get_dao_parameters(DAO.OWNERSHIP)["voting"])
            
            gauge_controller = boa.load_abi("src/utils/abis/gauge_controller.json").at(GAUGE_CONTROLLER)
            
            # we check if the gauge has already been added to the GaugeController
            # NOTE: need to fix the edgecase where a gauge has been killed
            gauge_exists = False
            try:
                gauge_type = gauge_controller.gauge_types(self.gauge_address)
                if isinstance(gauge_type, (int, float)) and gauge_type >= 0:
                    gauge_exists = True
            except Exception:
                # Exception means gauge does not exist, which is fine
                gauge_exists = False

            if gauge_exists:
                if show_info:
                    console.print(f"[bold red]Gauge has already been added to the GaugeController![/]")
                return SimulationResult(success=False, message="Gauge has already been added to the GaugeController.", error=None)
            else:
                if show_info:
                    console.print(f"[bold green]Gauge can be added to the GaugeController.[/]")

            # Only proceed to onchain execution if gauge has not been added yet (see above)
            try:
                if return_calldata:
                    temp_vote_id, evm_script = create_vote(
                        dao=DAO.OWNERSHIP,
                        actions=self.vote_payload,
                        description=self.description,
                        etherscan_api_key=self.config.etherscan_api_key,
                        pinata_token=self.config.pinata_token,
                        is_simulation=True,
                        return_calldata=True
                    )
                else:
                    temp_vote_id = create_vote(
                        dao=DAO.OWNERSHIP,
                        actions=self.vote_payload,
                        description=self.description,
                        etherscan_api_key=self.config.etherscan_api_key,
                        pinata_token=self.config.pinata_token,
                        is_simulation=True
                    )
                if show_info:
                    console.print(f"[bold magenta]Temporary vote created with ID:[/] [white]{temp_vote_id}[/]")
                with boa.env.prank(CONVEX_VOTERPROXY):
                    voting.vote(temp_vote_id, True, False)
                    num_seconds = voting.voteTime()
                    boa.env.time_travel(seconds=num_seconds)
                assert voting.canExecute(temp_vote_id), "Vote cannot be executed"
                with boa.env.prank(boa.env.generate_address()):
                    voting.executeVote(temp_vote_id)
                if show_info:
                    console.print(f"[bold green]Vote executed successfully[/]")
            except Exception as e:
                if show_info:
                    console.print(f"[bold red]Vote execution failed:[/] {str(e)}")
                return SimulationResult(success=False, message="Vote execution failed", error=str(e))

            details = {
                "gauge_address": self.gauge_address,
                "weight": self.weight,
                "type_id": self.type_id,
                "temp_vote_id": temp_vote_id
            }
            if return_calldata:
                details["evm_script"] = evm_script
            if show_info:
                console.print(f"[bold green]Simulation successful - gauge can be added[/]")
            return SimulationResult(
                success=True,
                message="Simulation successful - gauge can be added",
                details=details
            )
        except Exception as e:
            user_msg = str(e) or "Simulation failed."
            if "already been added" in user_msg:
                user_msg = "Simulation failed: Gauge has already been added to the GaugeController."
            else:
                user_msg = f"Simulation failed: {user_msg}"
            if show_info:
                console.print(f"[bold red]{user_msg}[/]")
            return SimulationResult(success=False, message=user_msg, error=None)


class KillGauge(VoteTemplate):
    """Template for killing a gauge"""

    def __init__(self, config: VoteConfig, gauge_address: str, description: str = ""):
        """
        Initialize a kill gauge vote

        Args:
            config: Vote configuration including API keys and environment settings
            gauge_address: Address of the gauge to kill
            description: Description of the vote
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address

        # Create the vote payload - pass arguments directly
        self.vote_payload = [
            (
                self.gauge_address,
                "set_killed",
                True  # Set is_killed to True
            )
        ]

    def _validate(self, show_info=False) -> ValidationResult:
        """
        Perform static, local validation of input parameters.
        Only check input format, types, and ranges (e.g., address format).
        Do NOT perform any onchain or stateful checks here—those belong in simulation.
        """
        errors = []
        if show_info:
            console.print(f"[bold cyan]Validating gauge address:[/] [white]{self.gauge_address}[/]")
        if not re.match(r"^0x[a-fA-F0-9]{40}$", self.gauge_address):
            errors.append("Invalid Ethereum address format.")
        if errors:
            if show_info:
                for err in errors:
                    console.print(f"[bold red]Validation failed:[/] {err}")
            return ValidationResult(success=False, errors=errors)
        if show_info:
            console.print(f"[bold green]Validation passed![/]")
        return ValidationResult(success=True)

    def simulate(self, show_info=False, skip_validation=False, return_calldata=False):
        """
        Public method to simulate the vote
        Args:
            show_info: Show step-by-step info
            skip_validation: Skip validation step
            return_calldata: If True, include EVM script in SimulationResult.details
        Returns:
            SimulationResult
        """

        # TODO: need to check if the gauge has even been added to the GaugeController

        logger.info("Starting vote simulation")
        if not skip_validation:
            validation = self.validate(show_info=show_info)
            if not validation.success:
                return SimulationResult(success=False, message="Validation failed", error="; ".join(validation.errors))
        try:
            result = self._simulate(show_info=show_info, return_calldata=return_calldata)
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

    def _simulate(self, show_info=False, return_calldata=False) -> SimulationResult:
        """
        Perform simulation, including onchain state checks.
        Args:
            show_info: Show step-by-step info
            return_calldata: If True, include EVM script in SimulationResult.details
        Returns:
            SimulationResult
        """
        try:
            if show_info:
                console.print(f"[bold cyan]Starting gauge killing simulation[/]")
            boa.fork(self.config.get_rpc_url(), allow_dirty=True)

            voting = boa.load_abi("src/utils/abis/voting.json").at(get_dao_parameters(DAO.OWNERSHIP)["voting"])

            # Only proceed to onchain execution
            try:
                if return_calldata:
                    temp_vote_id, evm_script = create_vote(
                        dao=DAO.OWNERSHIP,
                        actions=self.vote_payload,
                        description=self.description,
                        etherscan_api_key=self.config.etherscan_api_key,
                        pinata_token=self.config.pinata_token,
                        is_simulation=True,
                        return_calldata=True
                    )
                else:
                    temp_vote_id = create_vote(
                        dao=DAO.OWNERSHIP,
                        actions=self.vote_payload,
                        description=self.description,
                        etherscan_api_key=self.config.etherscan_api_key,
                        pinata_token=self.config.pinata_token,
                        is_simulation=True
                    )
                if show_info:
                    console.print(f"[bold magenta]Temporary vote created with ID:[/] [white]{temp_vote_id}[/]")
                with boa.env.prank(CONVEX_VOTERPROXY):
                    voting.vote(temp_vote_id, True, False)
                    num_seconds = voting.voteTime()
                    boa.env.time_travel(seconds=num_seconds)
                assert voting.canExecute(temp_vote_id), "Vote cannot be executed"
                with boa.env.prank(boa.env.generate_address()):
                    voting.executeVote(temp_vote_id)
                if show_info:
                    console.print(f"[bold green]Vote executed successfully[/]")
            except Exception as e:
                if show_info:
                    console.print(f"[bold red]Vote execution failed:[/] {str(e)}")
                return SimulationResult(success=False, message="Vote execution failed", error=str(e))

            # Check if the gauge is killed
            gauge = boa.load_abi("src/utils/abis/gauge_v6.json").at(self.gauge_address)
            try:
                is_killed = gauge.is_killed()
                if is_killed:
                    if show_info:
                        console.print(f"[bold green]Gauge has successfully been killed[/]")
                else:
                    raise Exception("Gauge was not killed successfully")
            except Exception as e:
                if show_info:
                    console.print(f"[bold red]Failed to verify gauge killed status:[/] {str(e)}")
                return SimulationResult(success=False, message="Gauge not killed", error=str(e))
            details = {
                "gauge_address": self.gauge_address,
                "temp_vote_id": temp_vote_id
            }
            if return_calldata:
                details["evm_script"] = evm_script
            if show_info:
                console.print(f"[bold green]Simulation successful - gauge can be killed[/]")
            return SimulationResult(
                success=True,
                message="Simulation successful - gauge can be killed",
                details=details
            )
        except Exception as e:
            if show_info:
                console.print(f"[bold red]Simulation failed:[/] {str(e)}")
            return SimulationResult(success=False, message="Simulation failed", error=str(e))
