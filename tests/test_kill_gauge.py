import os
import sys
import pytest

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.config import VoteConfig
from src.templates.gauge import KillGauge

@pytest.fixture
def config():
    """Create a VoteConfig for testing"""
    return VoteConfig(is_forked=True)

@pytest.fixture(autouse=True)
def fork_chain(config):
    """Fork the mainnet for testing and clean up after each test"""
    import boa
    boa.fork(config.get_rpc_url(), allow_dirty=True)
    with boa.env.anchor():
        yield

def test_kill_invalid_eth_address(config, fork_chain):
    """Test validation fails with invalid Ethereum address (KillGauge)"""
    kill_vote = KillGauge(
        config=config,
        gauge_address="0xinvalid",  # Invalid address
        description="Test invalid address"
    )
    is_valid = kill_vote.validate()
    assert not is_valid, "Validation should fail with invalid address"


def test_kill_nonexistent_gauge(config, fork_chain):
    """Test simulation fails for killing a non-existent gauge (should fail at execution)"""
    kill_vote = KillGauge(
        config=config,
        gauge_address="0x0000F90827F1C53a10cb7A02335B175320002935",  # Non-existent gauge
        description="Test kill non-existent gauge"
    )
    is_valid = kill_vote.validate()
    assert is_valid, "Validation should pass for valid gauge address"
    sim_result = kill_vote.simulate(skip_validation=True)
    assert not sim_result, "Simulation should fail for non-existent gauge"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])