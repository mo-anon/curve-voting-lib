import boa
import logging
from typing import Any, Tuple, List, Optional
from hexbytes import HexBytes

from src.utils.evm_script import prepare_evm_script
from src.utils.constants import get_dao_parameters, DAO

logger = logging.getLogger(__name__)


def create_vote(
        dao: str | DAO,
        actions: List[Tuple],
        description: str,
        etherscan_api_key: str,
        pinata_token: str,
        is_simulation: bool = True,
        vote_creator_address: Optional[str] = None,
        return_calldata: bool = False,
        simulation: bool = True,
) -> int | Tuple[int, HexBytes]:
    """
    Create a Curve DAO vote
    
    Args:
        dao: The DAO to create the vote in (ownership, parameter, emergency)
        actions: List of actions to execute (target_address, function_name, *args)
        description: Description of the vote
        etherscan_api_key: Etherscan API key for contract verification
        pinata_token: Pinata token for IPFS operations
        is_simulation: Whether to simulate the vote (True) or post it live (False) - DEPRECATED, use simulation
        vote_creator_address: Address of the vote creator (required for live posting)
        return_calldata: If True, return (vote_id, evm_script) where evm_script is the calldata/EVM script for the vote. Otherwise, return just vote_id.
        simulation: If True, simulate the vote. If False, connect to browser wallet for live voting
        
    Returns:
        int: Vote ID
        
    Raises:
        ValueError: If vote_creator_address is not provided for live posting
        Exception: If vote creation fails
    """
    
    # For browser wallet mode, we don't need vote_creator_address
    # The validation is handled by boa.set_browser_env() when simulation=False
    
    logger.info(f"Creating vote in {'simulation' if simulation else 'live'} mode")
    
    # Prepare the EVM script
    evm_script = prepare_evm_script(dao, actions, etherscan_api_key)
    logger.info(f"EVM script prepared: {evm_script.hex()}")

    # TODO: Implement IPFS pinning for vote description
    # For now, use empty string as placeholder
    vote_description_data = ""
    logger.info(f"Vote description data: {vote_description_data}")

    # Get the voting contract
    voting = boa.from_etherscan(
        get_dao_parameters(dao)["voting"],
        name="AragonVoting",
        api_key=etherscan_api_key,
    )
    logger.info(f"Voting contract loaded: {voting.address}")

    # Create the vote
    if simulation:
        # Use a test address for simulation
        with boa.env.prank('0xaE34c9738060137Ab0580587e813d1cfe637F506'):
            vote_id = voting.newVote(HexBytes(evm_script), vote_description_data, False, False)
            logger.info(f"Simulation vote created with ID: {vote_id}")
    else:
        # Live voting
        # Connect to browser wallet
        boa.set_browser_env()
        logger.info("Connected to browser wallet")
        
        vote_id = voting.newVote(HexBytes(evm_script), vote_description_data, False, False)
        logger.info(f"Live vote created with ID: {vote_id}")

    if return_calldata:
        return vote_id, evm_script
    else:
        return vote_id
