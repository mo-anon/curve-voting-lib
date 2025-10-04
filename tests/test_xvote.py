import os

import pytest
import boa

from voting import vote, xvote, OWNERSHIP, PARAMETER
from voting.xgov.chains import SONIC, FRAXTAL, OPTIMISM, TAIKO, X_LAYER


@pytest.mark.parametrize(
    "chain",
    [
        SONIC,  # Storage proofs
        FRAXTAL,  # Optimism generic
        OPTIMISM,  # Optimism
        TAIKO,  # Taiko generic
        X_LAYER,  # Polygon zkEVM
    ],
)
@pytest.mark.parametrize("entity", [OWNERSHIP, PARAMETER])
def test_empty_vote(chain, entity):
    with vote(entity, description="Empty test vote"):
        with xvote(chain, chain.rpc):
            pass


def test_vault_transfer():
    future_owner = "0x71F718D3e4d1449D1502A6A7595eb84eBcCB1683"
    with vote(OWNERSHIP, description="Empty test vote"):
        with xvote(FRAXTAL, FRAXTAL.rpc):
            vault = boa.from_etherscan(
                "0x50eD95CEb917443eE0790Eea97494121CA318a6C",
                uri="https://api.etherscan.io/v2/api?chainId=252",
                api_key=os.environ["ETHERSCAN_V2_TOKEN"],
            )
            vault.commit_future_owner(future_owner)
            vault.apply_future_owner()
            assert vault.owner() == future_owner
