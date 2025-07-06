from typing import TypedDict
from enum import StrEnum


class DAO(StrEnum):
    OWNERSHIP = "ownership"
    PARAMETER = "parameter"
    EMERGENCY = "emergency"


class DAOParameters(TypedDict, total=False):
    """TypedDict for DAO parameters. total=False because EMERGENCY_DAO has fewer fields"""
    agent: str
    voting: str
    token: str
    quorum: int


# Core DAO configurations
CURVE_DAO_OWNERSHIP: DAOParameters = {
    "agent": "0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
    "voting": "0xE478de485ad2fe566d49342Cbd03E49ed7DB3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

CURVE_DAO_PARAMETER: DAOParameters = {
    "agent": "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    "voting": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 15,
}

EMERGENCY_DAO: DAOParameters = {
    "agent": "0x467947EE34aF926cF1DCac093870f613C96B1E0c"
}


GAUGE_CONTROLLER = "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"
VOTING_ESCROW = "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2"
veCRV = VOTING_ESCROW  # alias for clarity
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
ADDRESS_PROVIDER = "0x5ffe7FB82894076ECB99A30D6A32e969e6e35E98"


def get_address(vote_type: DAO | str) -> str:
    """
    Get agent address of DAO
    
    Args:
        - vote_type: Name, agent address or enum of the DAO
        
    Returns:
        - str: The agent address for the specified DAO
    """
    return get_dao_parameters(vote_type)["agent"]


def get_dao_parameters(vote_type: DAO | str) -> DAOParameters:
    """
    Get parameters for a specific DAO
    
    Args:
        vote_type: Name, agent address or enum of the DAO
        
    Returns:
        DAOParameters: Dictionary containing DAO configuration
        
    Raises:
        ValueError: If vote_type is not recognized
    """
    if isinstance(vote_type, str) and vote_type.startswith("0x"):
        # Create reverse lookup from agent address to DAO enum
        address_to_dao = {
            get_dao_parameters(dao)["agent"]: dao 
            for dao in DAO
        }
        if vote_type not in address_to_dao:
            raise ValueError(f"Unknown DAO address: {vote_type}")
        vote_type = address_to_dao[vote_type]
    
    match DAO(vote_type):
        case DAO.OWNERSHIP:
            return CURVE_DAO_OWNERSHIP
        case DAO.PARAMETER:
            return CURVE_DAO_PARAMETER
        case DAO.EMERGENCY:
            return EMERGENCY_DAO
        case _:
            raise ValueError(f"Unknown DAO type: {vote_type}")

def get_dao_voting_contract(vote_type: str):
    target = select_target(vote_type)
    return target["voting"]

def select_target(vote_type: str):
    match vote_type:
        case "ownership":
            return CURVE_DAO_OWNERSHIP
        case "parameter":
            return CURVE_DAO_PARAMETER
        case "emergency":
            return EMERGENCY_DAO