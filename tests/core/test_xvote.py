import os

import pytest
import boa

from tests.shared.forked.settings import Chain
from voting import vote, xvote, OWNERSHIP, PARAMETER


@pytest.mark.parametrize("chain", [
    Chain.SONIC,  # Storage proofs
    Chain.FRAXTAL,  # Optimism generic
    Chain.OPTIMISM,  # Optimism
    # Chain.ARBITRUM,  # Arbitrum
    # Arbitrum generic is not used
    Chain.TAIKO,  # Taiko generic
    Chain.X_LAYER,  # Polygon zkEVM
    # Polygon zkEVM generic is not used
])
@pytest.mark.parametrize("entity", [OWNERSHIP, PARAMETER])
def test_empty_vote(forked_rpc, chain, entity):
    with vote(entity, description="Empty test vote"):
        with xvote(chain.value, forked_rpc(chain)):
            pass


def test_vault_transfer(forked_rpc):
    future_owner = "0x71F718D3e4d1449D1502A6A7595eb84eBcCB1683"
    with vote(OWNERSHIP, description="Empty test vote"):
        with xvote(Chain.FRAXTAL.value, forked_rpc(Chain.FRAXTAL)):
            vault = boa.from_etherscan("0x50eD95CEb917443eE0790Eea97494121CA318a6C", uri="https://api.etherscan.io/v2/api?chainId=252", api_key=os.environ["ETHERSCAN_V2_TOKEN"])
            vault.commit_future_owner(future_owner)
            vault.apply_future_owner()
            assert vault.owner() == future_owner
