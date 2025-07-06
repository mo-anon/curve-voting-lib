import os
from typing import Optional
from dotenv import load_dotenv

class VoteConfig:
    """Configuration for vote operations"""
    
    def __init__(
        self,
        etherscan_api_key: Optional[str] = None,
        alchemy_api_key: Optional[str] = None,
        pinata_token: Optional[str] = None,
        is_forked: bool = False
    ):
        """
        Initialize vote configuration
        
        Args:
            etherscan_api_key: Etherscan API key for contract verification
            alchemy_api_key: Alchemy API key for RPC access
            pinata_token: Pinata token for IPFS operations
            is_forked: Whether to operate in forked mode
        """
        # Load environment variables if not provided
        load_dotenv()
        
        self.etherscan_api_key = etherscan_api_key or os.getenv("ETHERSCAN_API_KEY")
        self.alchemy_api_key = alchemy_api_key or os.getenv("ALCHEMY_API_KEY")
        self.pinata_token = pinata_token or os.getenv("PINATA_TOKEN")
        self.is_forked = is_forked
        
        if not self.etherscan_api_key:
            raise ValueError("Etherscan API key is required")
        if not self.alchemy_api_key:
            raise ValueError("Alchemy API key is required")
        if not self.pinata_token:
            raise ValueError("Pinata token is required")
            
    def get_rpc_url(self) -> str:
        """Get the RPC URL based on configuration"""
        return f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}" 