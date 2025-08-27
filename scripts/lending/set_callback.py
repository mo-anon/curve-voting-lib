import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

controller_address = "0x5756a035f276a8095a922931f224f4ed06149608"
controller = abi.lending_controller.at(controller_address)
amm = abi.lending_amm.at(controller.amm())

new_cb = '0x0000000000000000000000000000000000000000'

with vote(
    OWNERSHIP,
    f"[lending] Set callback of fxSAVE lending market to {new_cb}.",
    live=False
):

    controller.set_callback(
        cb=new_cb,
    )

    assert amm.liquidity_mining_callback() == new_cb
