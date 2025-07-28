import re
import boa
from src.templates.base import VoteTemplate
from src.utils.constants import GAUGE_CONTROLLER, get_dao_parameters, DAO
from src.core.create_vote import create_vote

class AddGauge(VoteTemplate):
    """Template for adding a gauge to the gauge controller"""
    
    def __init__(self, config: dict, gauge_address: str, weight: int, type_id: int, description: str = ""):
        """
        Initialize a gauge vote
        
        Args:
            config: Vote configuration dictionary
            gauge_address: Address of the gauge to add
            weight: Weight to assign to the gauge
            type_id: Type ID for the gauge
            description: Description of the vote
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        self.weight = weight
        self.type_id = type_id
        
        # Create the vote payload
        self.vote_payload = [
            (
                GAUGE_CONTROLLER,
                "add_gauge",
                gauge_address,
                weight,
                type_id
            )
        ]
        
    def _validate(self) -> bool:
        """
        Perform static validation of input parameters.
        Only check input format, types, and ranges.
        """
        if not re.match(r"^0x[a-fA-F0-9]{40}$", self.gauge_address):
            self.error = "Invalid Ethereum address format"
            return False
        
        if self.weight != 0:
            self.error = "Weight must be zero for new gauge"
            return False
        
        if self.type_id != 0:
            self.error = "Type ID must be zero for new gauge"
            return False
        
        return True

    def _simulate(self) -> bool:
        """
        Simulate the vote on forked mainnet
        """
        try:
            # Fork mainnet
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get the gauge controller
            gauge_controller = boa.from_etherscan(
                GAUGE_CONTROLLER,
                name="GaugeController",
                api_key=self.config["etherscan_key"],
            )
            
            # Check if gauge already exists
            try:
                gauge_controller.gauge_types(self.gauge_address)
                self.error = "Gauge already exists"
                return False
            except:
                # Gauge doesn't exist, which is what we want
                pass
            
            # Simulate the vote
            vote_id = create_vote(
                dao=DAO.OWNERSHIP,
                actions=self.vote_payload,
                description=self.description,
                etherscan_api_key=self.config["etherscan_key"],
                pinata_token=self.config["pinata_token"],
                is_simulation=True
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Simulation failed: {str(e)}"
            return False
    
    def _create_vote(self, simulation: bool = True) -> bool:
        """
        Create the actual vote
        """
        try:
            # Fork mainnet first
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            vote_id = create_vote(
                dao=DAO.OWNERSHIP,
                actions=self.vote_payload,
                description=self.description,
                etherscan_api_key=self.config["etherscan_key"],
                pinata_token=self.config["pinata_token"],
                simulation=simulation
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Vote creation failed: {str(e)}"
            return False

class KillGauge(VoteTemplate):
    """Template for killing a gauge in the gauge controller"""
    
    def __init__(self, config: dict, gauge_address: str, description: str = ""):
        """
        Initialize a kill gauge vote
        
        Args:
            config: Vote configuration dictionary
            gauge_address: Address of the gauge to kill
            description: Description of the vote
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        
        # Create the vote payload
        self.vote_payload = [
            (
                GAUGE_CONTROLLER,
                "kill_gauge",
                gauge_address
            )
        ]
        
    def _validate(self) -> bool:
        """
        Perform static validation of input parameters.
        """
        if not re.match(r"^0x[a-fA-F0-9]{40}$", self.gauge_address):
            self.error = "Invalid Ethereum address format"
            return False
        
        return True

    def _simulate(self) -> bool:
        """
        Simulate the vote on forked mainnet
        """
        try:
            # Fork mainnet
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get the gauge controller
            gauge_controller = boa.from_etherscan(
                GAUGE_CONTROLLER,
                name="GaugeController",
                api_key=self.config["etherscan_key"],
            )
            
            # Check if gauge exists
            try:
                gauge_type = gauge_controller.gauge_types(self.gauge_address)
                if gauge_type == 0:
                    self.error = "Gauge does not exist"
                    return False
            except:
                self.error = "Gauge does not exist"
                return False
            
            # Simulate the vote
            vote_id = create_vote(
                dao=DAO.OWNERSHIP,
                actions=self.vote_payload,
                description=self.description,
                etherscan_api_key=self.config["etherscan_key"],
                pinata_token=self.config["pinata_token"],
                is_simulation=True
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Simulation failed: {str(e)}"
            return False
    
    def _create_vote(self, simulation: bool = True) -> bool:
        """
        Create the actual vote
        """
        try:
            vote_id = create_vote(
                dao=DAO.OWNERSHIP,
                actions=self.vote_payload,
                description=self.description,
                etherscan_api_key=self.config["etherscan_key"],
                pinata_token=self.config["pinata_token"],
                simulation=simulation
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Vote creation failed: {str(e)}"
            return False
