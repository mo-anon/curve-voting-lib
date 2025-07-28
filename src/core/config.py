import os
from dotenv import load_dotenv

load_dotenv()

def get_config() -> dict:
    """Get configuration as a simple dictionary"""
    return {
        "rpc_url": f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}",
        "etherscan_key": os.getenv("ETHERSCAN_API_KEY"),
        "pinata_token": os.getenv("PINATA_TOKEN"),
        "simulate": True,
        "show_info": False,
        "is_forked": True,
    } 