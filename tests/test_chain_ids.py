"""Live cross-check: does each Chain() in voting.xgov.chains still match on-chain reality?

Catches drift like INK (declared id=200, live 57073) and HYPERLIQUID (declared id=998,
live 999) automatically instead of relying on someone noticing by hand.
"""
import pytest
import requests

import voting.xgov.chains as chains_module
from voting.xgov.chains import Chain, RPC_NOT_SET

# Only consulted when a Chain's own `rpc` field is RPC_NOT_SET.
FALLBACK_RPC = {
    "GNOSIS": "https://gnosis-rpc.publicnode.com",
    "INK": "https://rpc-gel.inkonchain.com",
    "FANTOM": "https://fantom-rpc.publicnode.com",
    "POLYGON": "https://polygon-bor-rpc.publicnode.com",
    "BSC": "https://bsc-rpc.publicnode.com",
    "MOONBEAM": "https://moonbeam-rpc.publicnode.com",
    "HYPERLIQUID": "https://rpc.hyperliquid.xyz/evm",
    "KAVA": "https://kava-evm-rpc.publicnode.com",
    "CELO": "https://celo-rpc.publicnode.com",
    "AVALANCHE": "https://avalanche-c-chain-rpc.publicnode.com",
    "AURORA": "https://mainnet.aurora.dev",
    "MANTLE": "https://mantle-rpc.publicnode.com",
    "BASE": "https://base-rpc.publicnode.com",
}

ALL_CHAINS = {
    name: obj for name, obj in vars(chains_module).items() if isinstance(obj, Chain)
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


def _resolve_rpc(name, chain):
    return chain.rpc if chain.rpc != RPC_NOT_SET else FALLBACK_RPC.get(name)


@pytest.mark.parametrize("name,chain", sorted(ALL_CHAINS.items()))
def test_chain_matches_live_state(name, chain):
    rpc = _resolve_rpc(name, chain)
    if rpc is None:
        pytest.skip(f"no RPC known for {name}; add one to FALLBACK_RPC or chains.py")

    live_id = int(_rpc_call(rpc, "eth_chainId", []), 16)
    assert live_id == chain.id, (
        f"{name}: chains.py declares id={chain.id}, but live eth_chainId is {live_id}"
    )

    code = _rpc_call(rpc, "eth_getCode", [chain.relayer, "latest"])
    assert code not in (None, "0x", "0x0"), (
        f"{name}: relayer {chain.relayer} has no bytecode on live chain (id {chain.id})"
    )
