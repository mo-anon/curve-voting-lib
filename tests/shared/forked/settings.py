from enum import Enum
import os


# Using Chain ID for unique values
class Chain(Enum):
    ETH = 1
    FRAXTAL = 252
    SONIC = 146


CHAINS_DICT = {
    Chain.ETH: {
        "rpc": f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['WEB3_ETHEREUM_MAINNET_ALCHEMY_PROJECT_ID']}",
    },
    Chain.FRAXTAL: {"rpc": "https://rpc.frax.com"},
    Chain.SONIC: {"rpc": "https://rpc.soniclabs.com"},
}
