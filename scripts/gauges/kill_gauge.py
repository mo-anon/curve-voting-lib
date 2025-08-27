import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

gauge_to_kill = '0x479dfb03cddea20dc4e8788b81fd7c7a08fd3555'
gauge = abi.liquidity_gauge_v6.at(gauge_to_kill)

gauge_name = gauge.name()

with vote(
    OWNERSHIP,
    f"Kill gauge {gauge_to_kill} ({gauge_name}).",
    live=False  
):

    assert gauge.is_killed() == False

    gauge.set_killed(True)

    assert gauge.is_killed() == True
