import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

pool_address = "0x4f493B7dE8aAC7d55F71853688b1F7C8F0243C85"
pool = abi.stableswap_ng_mainnet_pool.at(pool_address)

"""
Ramping (A):
- Wait >= 1 day since last ramp/stop.
- future_time must be >= now + 1 day (needs to ramp for at least 1 day).
- future_A must hold 0 < A < 1,000,000.
- Change limited to <= 10x up or down vs current A (cannot ramp 10x).
"""

DAY = 86400
WEEK = 604800

new_A = 5000
ramp_time = WEEK + DAY
ts = boa.env.evm.patch.timestamp

pool_name = pool.name()

with vote(
    OWNERSHIP,
    f"[stableswap] Ramp A of {pool_address} ({pool_name}) to {new_A} over {ramp_time / DAY:.1f} days.",
    live=False
):

    pool.ramp_A(
        _future_A:=new_A,
        _future_time:=ts + ramp_time,
    )

    assert pool.future_A() == new_A * 100      # need to multiply by 100 because of the precision
    assert pool.future_A_time() == ts + ramp_time

    boa.env.time_travel(seconds=ramp_time)

    assert pool.A() == new_A
    