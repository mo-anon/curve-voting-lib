# Curve DAO Voting Toolkit

A Python package for creating and simulating Curve DAO governance votes.

---

## Features

- **Context Manager Voting:** Use `vote()` context manager to automatically capture contract interactions
- **Simulation & Live Voting:** Fork mainnet for testing or create actual governance proposals
- **IPFS Integration:** Automatic vote description pinning via Pinata

---

## Installation

```sh
git clone <your-repo-url>
cd curve-voting-lib
uv sync
uv run python -m pip install -e .
```

---

## Configuration

Set environment variables:

```env
RPC_URL=your_rpc_url
PINATA_JWT=your_pinata_jwt_token
```

---

## Usage

Scripts can be run using `uv run`:

```sh
uv run scripts/gauges/add_gauge.py
```

### Basic Example

```python
import os
import boa
from voting import vote, abi, OWNERSHIP
from eth_utils import keccak

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)
factory = abi.twocrypto_ng_mainnet_factory.at("0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F")


with vote(
    OWNERSHIP,
    "[twocrypto] Add implementations for donations-enabled pools (yb, fx, etc)",
    live=True
):

    factory.set_pool_implementation(
        donations_pool:="0xbab4CA419DF4e9ED96435823990C64deAD976a9F",
        donations_hash:=int.from_bytes(keccak(b'donations'), 'big')
    )

    assert factory.pool_implementations(donations_hash) == donations_pool
```

### Available Scripts

```sh
# Add gauge
uv run scripts/gauges/add_gauge.py
# or
python scripts/gauges/add_gauge.py

# Set pool implementation
uv run scripts/twocrypto-ng/set_implementation.py
# or
python scripts/twocrypto-ng/set_implementation.py
```
