import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

factory = abi.stableswap_ng_mainnet_factory.at("0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf")

base_pool_address = "0xD001aE433f254283FeCE51d4ACcE8c53263aa186"
base_lp_token_address = "0xD001aE433f254283FeCE51d4ACcE8c53263aa186"
asset_types = [0, 0]
n_coins = 2

pool = abi.stableswap_ng_mainnet_pool.at(base_pool_address)
pool_name = pool.name()
base_pool_count = factory.base_pool_count()


with vote(
    OWNERSHIP,
    f"[stableswap-factory] Add pool {base_pool_address} ({pool_name}) as a base pool.",
    live=False
):

    factory.add_base_pool(
        _base_pool=base_pool_address,
        _base_lp_token=base_lp_token_address,
        _asset_types=asset_types,
        _n_coins=n_coins,
    )

    assert factory.base_pool_count() == base_pool_count + 1
    assert factory.base_pool_list(base_pool_count) == base_pool_address  # index starts at 0
    