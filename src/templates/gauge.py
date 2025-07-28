import re
import boa
from src.templates.base import VoteTemplate
from src.utils.constants import GAUGE_CONTROLLER, get_dao_parameters, DAO
from src.core.create_vote import create_vote

class AddGauge(VoteTemplate):
    """Add a new gauge to the Curve DAO"""
    
    def __init__(self, config: dict, gauge_address: str, weight: int = 0, type_id: int = 0, description: str = ""):
        """
        Initialize an AddGauge vote
        
        Args:
            config: Vote configuration dictionary
            gauge_address: Address of the gauge to add
            weight: Weight for the gauge (default: 0)
            type_id: Type ID for the gauge (default: 0)
            description: Description of the vote
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        self.weight = weight
        self.type_id = type_id
        
        # Prepare the vote payload
        self.vote_payload = [
            (GAUGE_CONTROLLER, "add_gauge", gauge_address, weight, type_id)
        ]
        
    def _validate(self) -> bool:
        """
        Validate the gauge addition
        """
        try:
            # Check if gauge address is valid
            if not self.gauge_address.startswith("0x") or len(self.gauge_address) != 42:
                self.error = "Invalid gauge address format"
                return False
                
            # Check if gauge already exists (basic check)
            # TODO: Add more sophisticated validation
            
            return True
            
        except Exception as e:
            self.error = f"Validation failed: {str(e)}"
            return False
    
    def _simulate(self) -> bool:
        """
        Simulate the gauge addition
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
                simulation=True
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
            
            # If not simulation, connect to browser wallet
            if not simulation:
                boa.set_browser_env()
                print("🔗 Connected to browser wallet")
            
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
    
    def simulate(self) -> bool:
        """
        Simulate the vote creation
        """
        return self._create_vote(simulation=True)
    
    def create_live_vote(self) -> bool:
        """
        Create a live vote with browser wallet
        """
        # First simulate to make sure everything is valid
        if not self.simulate():
            return False
        
        print("✅ Simulation passed, creating live vote...")
        return self._create_vote(simulation=False)

class KillGauge(VoteTemplate):
    """Kill an existing gauge in the Curve DAO"""
    
    def __init__(self, config: dict, gauge_address: str, description: str = ""):
        """
        Initialize a KillGauge vote
        
        Args:
            config: Vote configuration dictionary
            gauge_address: Address of the gauge to kill
            description: Description of the vote
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        
        # Prepare the vote payload
        self.vote_payload = [
            (GAUGE_CONTROLLER, "kill_gauge", gauge_address)
        ]
        
    def _validate(self) -> bool:
        """
        Validate the gauge killing
        """
        try:
            # Check if gauge address is valid
            if not self.gauge_address.startswith("0x") or len(self.gauge_address) != 42:
                self.error = "Invalid gauge address format"
                return False
                
            return True
            
        except Exception as e:
            self.error = f"Validation failed: {str(e)}"
            return False
    
    def _simulate(self) -> bool:
        """
        Simulate the gauge killing
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
                simulation=True
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
            
            # If not simulation, connect to browser wallet
            if not simulation:
                boa.set_browser_env()
                print("🔗 Connected to browser wallet")
            
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
    
    def simulate(self) -> bool:
        """
        Simulate the vote creation
        """
        return self._create_vote(simulation=True)
    
    def create_live_vote(self) -> bool:
        """
        Create a live vote with browser wallet
        """
        # First simulate to make sure everything is valid
        if not self.simulate():
            return False
        
        print("✅ Simulation passed, creating live vote...")
        return self._create_vote(simulation=False)
