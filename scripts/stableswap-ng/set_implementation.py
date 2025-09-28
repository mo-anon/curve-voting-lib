import os
import boa
from voting import vote, abi, OWNERSHIP
from eth_utils import keccak

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

factory = abi.stableswap_ng_mainnet_factory.at("0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf")

hash = int.from_bytes(keccak(b'testtest'), 'big')  # create unique hash for the implementation
new_impl = "0xDCc91f930b42619377C200BA05b7513f2958b202"


with vote(
    OWNERSHIP,
    "[stableswap-factory] Add implementations for ...",
    live=False
):

    factory.set_pool_implementations(
        hash,
        new_impl,
    )

    assert factory.pool_implementations(hash) == new_impl
    