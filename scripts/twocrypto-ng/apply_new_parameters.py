import os
import boa
from voting import vote, abi, OWNERSHIP

RPC_URL = os.getenv("RPC_URL")
boa.fork(RPC_URL)

pool_address = '0xee351f12eae8c2b8b9d1b9bfd3c5dd565234578d'
pool = abi.twocrypto_ng_mainnet_pool.at(pool_address)
pool_name = pool.name()


new_mid_fee = 26000000
new_out_fee = 45000000
new_fee_gamma = 230000000000000
new_allowed_extra_profit = 2000000000000
new_adjustment_step = 146000000000000
new_ma_time = 880           # new_ma_time = ma_time / ln(2); setting new_ma_time to 880 means new_ma_time = 880 * ln(2) = 610

with vote(
    OWNERSHIP,
    f"[twocrypto] Apply the following parameters to {pool_address} ({pool_name}): mid_fee={new_mid_fee}, out_fee={new_out_fee}, fee_gamma={new_fee_gamma}, allowed_extra_profit={new_allowed_extra_profit}, adjustment_step={new_adjustment_step}, ma_time={new_ma_time}",
    live=False
):

    pool.apply_new_parameters(
        new_mid_fee:=new_mid_fee,
        new_out_fee:=new_out_fee,
        new_fee_gamma:=new_fee_gamma,
        new_allowed_extra_profit:=new_allowed_extra_profit,
        new_adjustment_step:=new_adjustment_step,
        new_ma_time:=new_ma_time,
    )

    assert pool.mid_fee() == new_mid_fee
    assert pool.out_fee() == new_out_fee
    assert pool.fee_gamma() == new_fee_gamma
    assert pool.allowed_extra_profit() == new_allowed_extra_profit
    assert pool.adjustment_step() == new_adjustment_step
    expected_ma_time = new_ma_time * 694 // 1000
    assert pool.ma_time() == expected_ma_time
    