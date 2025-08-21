import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

pool_address = '0xee351f12eae8c2b8b9d1b9bfd3c5dd565234578d'
pool = abi.twocrypto_ng_mainnet_pool.at(pool_address)
pool_name = pool.name()

with vote(
    OWNERSHIP,
    f"[twocrypto] Stop ramping A and gamma of {pool_address} ({pool_name})",
    live=False
):

    pool.stop_ramp_A_gamma()

    A_t1 = pool.A()
    gamma_t1 = pool.gamma()

    boa.env.time_travel(seconds=100)

    A_t2 = pool.A()
    gamma_t2 = pool.gamma()

    assert A_t1 == A_t2
    assert gamma_t1 == gamma_t2
