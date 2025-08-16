import boa
from voting import vote, abi, OWNERSHIP

boa.fork("http://100.124.213.109:8545")
factory = abi.twocrypto_ng_mainnet_factory.at("0x98EE851a00abeE0d95D08cF4CA2BdCE32aeaAF7F")


with vote(
    OWNERSHIP,
    "Add a new implementation of twocrypto-ng pools adapted for yield basis.",
    live=True
):
    addy = boa.env.generate_address()
    id = 123 
    factory.set_pool_implementation(addy, id)
    factory.set_pool_implementation(addy, id)

    assert factory.pool_implementations(id) == addy
        




