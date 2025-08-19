import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

pool_address = "0x4f493B7dE8aAC7d55F71853688b1F7C8F0243C85"
pool = abi.stableswap_ng_mainnet_pool.at(pool_address)

"""
Fees (denominated in 1e10):
- new fee must be <= MAX_FEE (5 * 10**9)
- new offpeg_fee_multiplier must be <= 1e10
- new offpeg_fee_multiplier * new fee must be <= MAX_FEE * FEE_DENOMINATOR (5 * 10**9 * 1e10 = 5 * 10**19)

e.g. 0.04% fee = 4000000; offpeg_fee_multiplier of 5 = 50000000000
"""

ts = boa.env.evm.patch.timestamp
pool_name = pool.name()

new_fee = 4000000
new_offpeg_fee_multiplier = 20


with vote(
    OWNERSHIP,
    f"[stableswap] Set new fee of {pool_address} ({pool_name}) to {new_fee} and offpeg_fee_multiplier to {new_offpeg_fee_multiplier}.",
    live=False
):

    pool.set_new_fee(
        _new_fee:=new_fee,
        _new_offpeg_fee_multiplier:=new_offpeg_fee_multiplier,
    )

    assert pool.fee() == new_fee
    assert pool.offpeg_fee_multiplier() == new_offpeg_fee_multiplier
    