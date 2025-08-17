import os
import boa
from voting import vote, abi, OWNERSHIP
from eth_utils import keccak

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)
factory = abi.twocrypto_ng_mainnet_factory.at("0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F")


with vote(
    OWNERSHIP,
    "[twocrypto] Add implementations for donations-enabled pools (yb, fx, etc)",
    live=True
):

    factory.set_pool_implementation(
        yb_pool:="0x986fAfB173801D9F82a01d9FfD71f1e1c080D2c2",
        yb_hash:=int.from_bytes(keccak(b'yb'), 'big')
    )

    factory.set_pool_implementation(
        donations_pool:="0xbab4CA419DF4e9ED96435823990C64deAD976a9F",
        donations_hash:=int.from_bytes(keccak(b'donations'), 'big')
    )

    assert factory.pool_implementations(yb_hash) == yb_pool
    assert factory.pool_implementations(donations_hash) == donations_pool
        
