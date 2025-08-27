import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

gauge_controller = abi.gauge_controller.at("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB")

gauge_to_add = input("Enter the gauge you wish to add to the controller: ")
WEIGHT = 0
TYPE_ID = 0


with vote(
    OWNERSHIP,
    f"Add gauge {gauge_to_add} to Gauge Controller with type {TYPE_ID}.",
    live=False  
):
    try:
        existing_type = gauge_controller.gauge_types(gauge_to_add)
        assert existing_type in range(0, 14), f"Gauge already exists with type {existing_type}"
    except:
        gauge_controller.add_gauge(gauge_to_add, TYPE_ID, WEIGHT)

        assert gauge_controller.gauge_types(gauge_to_add) == TYPE_ID
