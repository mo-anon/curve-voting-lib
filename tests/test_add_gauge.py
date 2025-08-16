import pytest


from voting.core.config import get_config
from voting.templates.gauge import AddGauge

@pytest.fixture
def config():
    """Create a config for testing"""
    return get_config()

@pytest.fixture(autouse=True)
def fork_chain(config):
    """Fork the mainnet for testing and clean up after each test"""
    import boa
    boa.fork(config["rpc_url"], allow_dirty=True)
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
    assert "Invalid gauge address format" in gauge_vote.error

def test_gauge_status_check(config, fork_chain):
    """Test that gauge status checking works"""
    gauge_vote = AddGauge(
        config=config,
        gauge_address="0x1234567890123456789012345678901234567890",  # Non-existent gauge
        weight=0,
        type_id=0,
        description="Test gauge status"
    )
    # Validation should pass (format is fine)
    is_valid = gauge_vote.validate()
    assert is_valid, "Validation should pass for valid address format"
    # Check gauge status - should return a dict with expected keys
    gauge_status = gauge_vote.check_gauge_status()
    assert isinstance(gauge_status, dict), "Should return a dictionary"
    assert 'exists' in gauge_status, "Should have 'exists' key"
    assert 'can_add' in gauge_status, "Should have 'can_add' key"

def test_valid_type_id(config, fork_chain):
    """Test validation passes with valid type_id"""
    gauge_vote = AddGauge(
        config=config,
        gauge_address="0x7987b8cea5b61642f94259318fa59c5f0cafe221",  # Non-existent gauge
        weight=0,
        type_id=0,  # Valid type_id
        description="Test valid type_id"
    )
    is_valid = gauge_vote.validate()
    assert is_valid, "Validation should pass with valid type_id"

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

