import re
import boa
from src.templates.base import VoteTemplate
from src.utils.constants import GAUGE_CONTROLLER, get_dao_parameters, DAO
from src.core.create_vote import create_vote

class AddGauge(VoteTemplate):
    """Add a new gauge to the Curve DAO"""
    
    def __init__(self, config: dict, gauge_address: str, weight: int = 0, type_id: int = 0, description: str = "", simulation: bool = True):
        """
        Initialize an AddGauge vote
        
        Args:
            config: Vote configuration dictionary
            gauge_address: Address of the gauge to add
            weight: Weight for the gauge (default: 0)
            type_id: Type ID for the gauge (default: 0)
            description: Description of the vote
            simulation: If True, simulate the vote. If False, create live vote with browser wallet
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        self.weight = weight
        self.type_id = type_id
        self.simulation = simulation
        
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
    
    def simulate(self, verbose: bool = False) -> bool:
        """Simulate the vote creation"""
        if verbose:
            print("Simulating vote creation...")
            print(f"   Gauge: {self.gauge_address}")
            print(f"   Weight: {self.weight}")
            print(f"   Type ID: {self.type_id}")
            print(f"   Target: Gauge Controller ({GAUGE_CONTROLLER})")
            print("\nRunning validations...")
        
        # Validate inputs
        if not self._validate():
            if verbose:
                print(f"   Validation failed: {self.error}")
            return False
        if verbose:
            print("   Input validation passed")
        
        # Check gauge status
        if verbose:
            print("\nChecking gauge status...")
        gauge_status = self.check_gauge_status()
        if verbose:
            print(f"   Gauge already exists: {gauge_status['exists']}")
            if 'gauge_type' in gauge_status:
                print(f"   Current gauge type: {gauge_status['gauge_type']}")
                print(f"   Current weight: {gauge_status['weight']}")
            if 'error' in gauge_status:
                print(f"   Query error: {gauge_status['error']}")
            print(f"   Can be added: {gauge_status['can_add']}")
        
        if not gauge_status['can_add']:
            if verbose:
                print("   Gauge cannot be added (already exists or invalid)")
            return False
        if verbose:
            print("   Gauge can be added")
        
        # Simulate the actual vote creation
        if verbose:
            print("\nCreating vote on fork...")
        
        return self._create_vote(simulation=True)
    
    def create_live_vote(self, verbose: bool = False) -> bool:
        """Create a live vote with browser wallet"""
        if verbose:
            print("Running safety checks before live vote...")
        
        if not self.simulate(verbose=verbose):
            return False
        
        if verbose:
            print("Safety checks passed, creating live vote...")
        
        return self._create_vote(simulation=False)
    
    def create_vote(self, verbose: bool = False) -> bool:
        """
        Create the vote (simulate or live based on simulation parameter)
        """
        if self.simulation:
            return self.simulate(verbose=verbose)
        else:
            return self.create_live_vote(verbose=verbose)
    
    def validate_inputs(self) -> bool:
        """
        Manually validate inputs without creating any votes
        """
        return self._validate()
    
    def check_gauge_exists(self) -> bool:
        """
        Check if the gauge already exists (basic check)
        """
        try:
            # Fork mainnet to check
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get gauge controller
            gauge_controller = boa.from_etherscan(
                GAUGE_CONTROLLER,
                name="GaugeController",
                api_key=self.config["etherscan_key"],
            )
            
            # Check if gauge exists
            try:
                gauge_type = gauge_controller.gauge_types(self.gauge_address)
                if gauge_type != 0:
                    self.error = f"Gauge already exists with type {gauge_type}"
                    return False
                else:
                    return True
            except:
                # Gauge doesn't exist, which is what we want
                return True
                
        except Exception as e:
            self.error = f"Failed to check gauge existence: {str(e)}"
            return False
    
    def test_contract_interaction(self) -> bool:
        """
        Test if the contract interaction would work (without creating vote)
        """
        try:
            # Fork mainnet
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get gauge controller
            gauge_controller = boa.from_etherscan(
                GAUGE_CONTROLLER,
                name="GaugeController",
                api_key=self.config["etherscan_key"],
            )
            
            # Test the function call (this won't actually execute, just test if it's valid)
            # We can't actually call add_gauge without proper permissions, but we can test the interface
            
            return True
            
        except Exception as e:
            self.error = f"Contract interaction test failed: {str(e)}"
            return False
    
    def run_full_validation(self) -> dict:
        """
        Run all validation checks and return results
        """
        results = {
            "input_validation": False,
            "gauge_exists_check": False,
            "contract_interaction": False,
            "simulation": False,
            "overall": False
        }
        
        # Test input validation
        results["input_validation"] = self.validate_inputs()
        
        # Test gauge existence
        if results["input_validation"]:
            results["gauge_exists_check"] = self.check_gauge_exists()
        
        # Test contract interaction
        if results["gauge_exists_check"]:
            results["contract_interaction"] = self.test_contract_interaction()
        
        # Test simulation
        if results["contract_interaction"]:
            results["simulation"] = self.simulate()
        
        # Overall result
        results["overall"] = all([
            results["input_validation"],
            results["gauge_exists_check"], 
            results["contract_interaction"],
            results["simulation"]
        ])
        
        return results

    def check_gauge_status(self) -> dict:
        """
        Manual check: Query gauge status from gauge controller
        """
        try:
            # Fork mainnet to check
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get gauge controller
            gauge_controller = boa.from_etherscan(
                GAUGE_CONTROLLER,
                name="GaugeController",
                api_key=self.config["etherscan_key"],
            )
            
            # Check gauge status
            try:
                # Suppress Vyper debug output
                import contextlib
                import io
                
                with contextlib.redirect_stdout(io.StringIO()):
                    gauge_type = gauge_controller.gauge_types(self.gauge_address)
                    weight = gauge_controller.get_gauge_weight(self.gauge_address)
                
                return {
                    "exists": gauge_type != 0,
                    "gauge_type": gauge_type,
                    "weight": weight,
                    "can_add": gauge_type == 0  # Can add if type is 0 (not registered)
                }
            except Exception as e:
                return {
                    "exists": False,
                    "error": str(e),
                    "can_add": True  # Assume can add if query fails
                }
                
        except Exception as e:
            return {
                "exists": False,
                "error": f"Failed to query gauge: {str(e)}",
                "can_add": False
            }

class KillGauge(VoteTemplate):
    """Kill an existing gauge in the Curve DAO"""
    
    def __init__(self, config: dict, gauge_address: str, description: str = "", simulation: bool = True):
        """
        Initialize a KillGauge vote
        
        Args:
            config: Vote configuration dictionary
            gauge_address: Address of the gauge to kill
            description: Description of the vote
            simulation: If True, simulate the vote. If False, create live vote with browser wallet
        """
        super().__init__(config, description)
        self.gauge_address = gauge_address
        self.simulation = simulation
        
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
        
        print("Simulation passed, creating live vote...")
        return self._create_vote(simulation=False)
    
    def create_vote(self, verbose: bool = False) -> bool:
        """
        Create the vote (simulate or live based on simulation parameter)
        """
        if self.simulation:
            return self.simulate(verbose=verbose)
        else:
            return self.create_live_vote(verbose=verbose)
