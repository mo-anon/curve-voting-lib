import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

controller_address = "0x8035b16053560b3c351b665b10f6c7dbdb6a1e05"
controller = abi.lending_controller.at(controller_address)

new_monetary_policy = "0xB7c2d9088C5D327877782e383468eE16df2e2c3d"

with vote(
    OWNERSHIP,
    f"[lending] Set new monetary policy of fxSAVE lending market to {new_monetary_policy}.",
    live=False
):

    controller.set_monetary_policy(
        monetary_policy=new_monetary_policy,
    )

    assert controller.monetary_policy() == new_monetary_policy
    