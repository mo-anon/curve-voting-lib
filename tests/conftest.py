import os
import pytest

from voting.xgov.chains import Chain


@pytest.fixture(autouse=True)
def fork_chain():
    """Fork the mainnet for testing and clean up after each test"""
    import boa

    boa.fork(
        f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['WEB3_ETHEREUM_MAINNET_ALCHEMY_PROJECT_ID']}",
        allow_dirty=True,
    )  # TODO: should clean also work?
    with boa.env.anchor():
        yield
