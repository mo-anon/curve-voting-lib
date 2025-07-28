import re
import boa
from src.templates.base import VoteTemplate
from src.utils.constants import get_dao_parameters, DAO
from src.core.create_vote import create_vote

class RampA(VoteTemplate):
    """Template for ramping the A parameter of a Curve pool"""
    
    def __init__(self, config: dict, pool_address: str, future_a: int, future_time: int, description: str = ""):
        """
        Initialize a ramp A vote
        
        Args:
            config: Vote configuration dictionary
            pool_address: Address of the pool to ramp A for
            future_a: Future A value
            future_time: Future time for the ramp
            description: Description of the vote
        """
        super().__init__(config, description)
        self.pool_address = pool_address
        self.future_a = future_a
        self.future_time = future_time
        
        # Create the vote payload
        self.vote_payload = [
            (
                pool_address,
                "ramp_A",
                future_a,
                future_time
            )
        ]
        
    def _validate(self) -> bool:
        """
        Perform static validation of input parameters.
        """
        if not re.match(r"^0x[a-fA-F0-9]{40}$", self.pool_address):
            self.error = "Invalid pool address format"
            return False
        
        if self.future_a <= 0:
            self.error = "Future A must be positive"
            return False
        
        if self.future_time <= 0:
            self.error = "Future time must be positive"
            return False
        
        return True

    def _simulate(self) -> bool:
        """
        Simulate the vote on forked mainnet
        """
        try:
            # Fork mainnet
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get the pool contract
            pool = boa.from_etherscan(
                self.pool_address,
                name="CurvePool",
                api_key=self.config["etherscan_key"],
            )
            
            # Check if pool exists and has ramp_A function
            try:
                # This will fail if the pool doesn't exist or doesn't have ramp_A
                pool.ramp_A(self.future_a, self.future_time)
            except:
                self.error = "Pool does not exist or does not support ramp_A"
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
    
    def _create_vote(self) -> bool:
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
                is_simulation=True
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Vote creation failed: {str(e)}"
            return False 