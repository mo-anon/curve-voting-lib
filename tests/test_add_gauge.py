import os
import sys
import pytest

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.config import VoteConfig
from src.templates.gauge import AddGauge

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

def test_invalid_eth_address(config, fork_chain):
    """Test validation fails with invalid Ethereum address"""
    gauge_vote = AddGauge(
        config=config,
        gauge_address="0xinvalid",  # Invalid address
        weight=0,
        type_id=0,
        description="Test invalid address"
    )
    is_valid = gauge_vote.validate()
    assert not is_valid, "Validation should fail with invalid address"

def test_existing_gauge(config, fork_chain):
    """Test simulation fails when trying to add an existing gauge"""
    gauge_vote = AddGauge(
        config=config,
        gauge_address="0xbFcF63294aD7105dEa65aA58F8AE5BE2D9d0952A",  # Known existing gauge
        weight=0,
        type_id=0,
        description="Test existing gauge"
    )
    # Validation should pass (format is fine)
    is_valid = gauge_vote.validate()
    assert is_valid, "Validation should pass for existing gauge (format only)"
    # Simulation should fail (gauge already exists)
    sim_result = gauge_vote.simulate(skip_validation=True)
    assert not sim_result, "Simulation should fail for existing gauge"

def test_invalid_type_id(config, fork_chain):
    """Test validation fails with non-zero type_id"""
    gauge_vote = AddGauge(
        config=config,
        gauge_address="0x798_7b8cea5b61642f94259318fa59c5f0cafe221",  # Non-existent gauge
        weight=0,
        type_id=1,  # Invalid type_id
        description="Test invalid type_id"
    )
    is_valid = gauge_vote.validate()
    assert not is_valid, "Validation should fail with non-zero type_id"

def test_valid_new_gauge(config, fork_chain):
    """Test validation passes for a valid new gauge"""
    gauge_vote = AddGauge(
        config=config,
        gauge_address="0x7987b8cea5b61642f94259318fa59c5f0cafe221",  # Non-existent gauge
        weight=0,
        type_id=0,
        description="Test valid new gauge"
    )
    is_valid = gauge_vote.validate()
    assert is_valid, "Validation should pass for valid new gauge"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])

