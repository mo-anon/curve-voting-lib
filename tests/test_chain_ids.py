"""Live cross-check: does each Chain() in voting.xgov.chains still match on-chain reality?

Catches drift like INK (declared id=200, live 57073) and HYPERLIQUID (declared id=998,
live 999) automatically instead of relying on someone noticing by hand.

Only checks chains with `rpc` set in chains.py; a hardcoded fallback endpoint would
go stale/rate-limit more often than the chain id actually drifts.
"""
import pytest
import requests

import voting.xgov.chains as chains_module
from voting.xgov.chains import Chain, RPC_NOT_SET

CHAINS_WITH_RPC = {
    name: obj
    for name, obj in vars(chains_module).items()
    if isinstance(obj, Chain) and obj.rpc != RPC_NOT_SET
}


@pytest.fixture(autouse=True)
def fork_chain():
    """Overrides conftest's autouse mainnet fork: these tests hit each chain's own RPC
    directly and have no use for (or dependency on) a forked mainnet."""
    yield


def _rpc_call(url, method, params):
    try:
        r = requests.post(
            url,
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            timeout=15,
        )
        r.raise_for_status()
        return r.json().get("result")
    except requests.RequestException as e:
        pytest.skip(f"RPC call to {url} failed: {e}")


@pytest.mark.parametrize("name,chain", sorted(CHAINS_WITH_RPC.items()))
def test_chain_matches_live_state(name, chain):
    live_id = int(_rpc_call(chain.rpc, "eth_chainId", []), 16)
    assert live_id == chain.id, (
        f"{name}: chains.py declares id={chain.id}, but live eth_chainId is {live_id}"
    )

    code = _rpc_call(chain.rpc, "eth_getCode", [chain.relayer, "latest"])
    assert code not in (None, "0x", "0x0"), (
        f"{name}: relayer {chain.relayer} has no bytecode on live chain (id {chain.id})"
    )
