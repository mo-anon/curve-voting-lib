import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

gauge_controller = abi.gauge_controller.at("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB")

gauge_to_add = input("Enter the gauge you wish to add to the controller: ")
weight = 0
type_id = 0

# TODO: Consider refactoring the gauge existence check.
# Note: exit() doesn't work reliably in this context, so we use raise SystemExit(1) to ensure the script terminates when gauge already exists.
try:
    existing_type = gauge_controller.gauge_types(gauge_to_add)
    print(f"Gauge already exists with type {existing_type} - no vote needed")
    raise SystemExit(1)
except SystemExit:
    raise
except:
    pass


with vote(
    OWNERSHIP,
    f"Add gauge {gauge_to_add} to Gauge Controller with type {type_id}.",
    live=False
):
    gauge_controller.add_gauge(gauge_to_add, type_id, weight)

    assert gauge_controller.gauge_types(gauge_to_add) == type_id
