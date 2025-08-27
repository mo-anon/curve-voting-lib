import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

pool_address = '0xee351f12eae8c2b8b9d1b9bfd3c5dd565234578d'
pool = abi.twocrypto_ng_mainnet_pool.at(pool_address)


DAY = 86400
WEEK = 604800

future_A = 400000
future_gamma = 145000000000000
ramp_time = WEEK + DAY
ts = boa.env.evm.patch.timestamp

pool_name = pool.name()

with vote(
    OWNERSHIP,
    f"[twocrypto] Ramp A and gamma of {pool_address} ({pool_name}) to {future_A} and {future_gamma} over {ramp_time / DAY:.1f} days.",
    live=False
):

    pool.ramp_A_gamma(
        future_A:=future_A,
        future_gamma:=future_gamma,
        future_time:=ts + ramp_time,
    )

    future_A_gamma = pool.future_A_gamma()
    gamma = future_A_gamma & (2**128 - 1)
    A = future_A_gamma >> 128

    assert A == future_A
    assert gamma == future_gamma

    boa.env.time_travel(seconds=ramp_time)

    assert pool.A() == future_A
    assert pool.gamma() == future_gamma
