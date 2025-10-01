import pytest

from tests.shared.forked.settings import Chain


pytest_plugins = [
    "shared.forked.fixtures",
]


@pytest.fixture(autouse=True)
def fork_chain(forked_rpc):
    """Fork the mainnet for testing and clean up after each test"""
    import boa
    boa.fork(forked_rpc(Chain.ETH), allow_dirty=True)  # TODO: should clean also work?
    with boa.env.anchor():
        yield
