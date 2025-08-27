import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

controller_address = "0x5756a035f276a8095a922931f224f4ed06149608"
controller = abi.lending_controller.at(controller_address)

"""
some rules:
- loan_discount > liquidation_discount
- liquidation_discount >= MIN_LIQUIDATION_DISCOUNT (10**16)
- loan_discount <= MAX_LOAN_DISCOUNT (5 * 10**17)
"""

new_loan_discount = 19000000000000000
new_liquidation_discount = 14000000000000000

with vote(
    OWNERSHIP,
    f"[lending] Set new borrowing discounts of fxSAVE lending market: loan_discount={new_loan_discount}, liquidation_discount={new_liquidation_discount}.",
    live=False
):

    controller.set_borrowing_discounts(
        loan_discount=new_loan_discount,
        liquidation_discount=new_liquidation_discount,
    )

    assert controller.loan_discount() == new_loan_discount
    assert controller.liquidation_discount() == new_liquidation_discount
    