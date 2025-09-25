import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

controller_address = "0x5756a035f276a8095a922931f224f4ed06149608"
controller = abi.lending_controller.at(controller_address)
amm = abi.lending_amm.at(controller.amm())

"""
some rules:
- fee >= MIN_FEE (10**6)
- fee <= MAX_FEE ((10**18 * MIN_TICK)/A) / 10**17
"""

new_amm_fee = 2000000000000000


with vote(
    OWNERSHIP,
    f"[lending] Set new fee of {amm.address} to {new_amm_fee}.",
    live=False
):

    controller.set_amm_fee(
        fee=new_amm_fee,
    )

    assert amm.fee() == new_amm_fee
    