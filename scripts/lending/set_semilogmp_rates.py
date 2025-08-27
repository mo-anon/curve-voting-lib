import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

semilog_mp = "0xd1671194FC23d1da8e9C2ec4a57c7F5e0957f55b"
contract = abi.semilog_mp.at(semilog_mp)

new_min_rate = 4631085          # 0.015%
new_max_rate = 21153444781      # 66.7%

with vote(
    OWNERSHIP,
    f"[lending] Set new semilogmp rates of {semilog_mp} to {new_min_rate} and {new_max_rate}.",
    live=False
):

    contract.set_rates(
        min_rate=new_min_rate,
        max_rate=new_max_rate,
    )

    assert contract.min_rate() == new_min_rate
    assert contract.max_rate() == new_max_rate
    