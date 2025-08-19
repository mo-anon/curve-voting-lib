import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

pool_address = "0x4f493B7dE8aAC7d55F71853688b1F7C8F0243C85"
pool = abi.stableswap_ng_mainnet_pool.at(pool_address)

"""
Oracle EMA windows (denominated in seconds):
- Both inputs must be > 0 (no zeros).
- ma_exp_time: seconds / ln(2).
- D_ma_time: seconds / ln(2).
"""

ts = boa.env.evm.patch.timestamp
pool_name = pool.name()

ma_exp_time = 866
D_ma_time = 62324


with vote(
    OWNERSHIP,
    f"[stableswap] Set ma_exp_time of {pool_address} ({pool_name}) to {ma_exp_time} and D_ma_time to {D_ma_time}.",
    live=False
):

    pool.set_ma_exp_time(
        _ma_exp_time:=ma_exp_time,
        _D_ma_time:=D_ma_time,
    )

    assert pool.ma_exp_time() == ma_exp_time
    assert pool.D_ma_time() == D_ma_time
    