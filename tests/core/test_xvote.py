import os

import pytest
import boa

from tests.shared.forked.settings import Chain
from voting import vote, xvote, OWNERSHIP, PARAMETER


@pytest.fixture(scope="module")
def rpc(forked_rpc):
    return forked_rpc(Chain.FRAXTAL)


@pytest.mark.parametrize("entity", [OWNERSHIP, PARAMETER])
def test_empty_vote(rpc, entity):
    with vote(entity, description="Empty test vote"):
        with xvote(Chain.FRAXTAL.value, rpc):
            pass


def test_vault_transfer(rpc):
    future_owner = "0x71F718D3e4d1449D1502A6A7595eb84eBcCB1683"
    with vote(OWNERSHIP, description="Empty test vote"):
        with xvote(Chain.FRAXTAL.value, rpc):
            vault = boa.from_etherscan("0x50eD95CEb917443eE0790Eea97494121CA318a6C", uri="https://api.etherscan.io/v2/api?chainId=252", api_key=os.environ["ETHERSCAN_V2_TOKEN"])
            vault.commit_future_owner(future_owner)
            vault.apply_future_owner()
            assert vault.owner() == future_owner
