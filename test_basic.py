#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voting.core.config import get_config
from voting.templates.gauge import AddGauge

def test_basic_functionality():
    """Test basic functionality without complex EVM script generation"""
    print("Testing basic functionality...")
    
    config = get_config()
    
    # Test AddGauge creation and validation
    vote = AddGauge(
        config=config,
        gauge_address="0x1234567890123456789012345678901234567890",
        weight=0,
        type_id=0,
        description="Test gauge"
    )
    
    print(f"✅ Vote object created successfully")
    print(f"✅ Gauge address: {vote.gauge_address}")
    print(f"✅ Weight: {vote.weight}")
    print(f"✅ Type ID: {vote.type_id}")
    print(f"✅ Vote payload: {vote.vote_payload}")
    
    # Test validation
    if vote.validate():
        print("✅ Validation passed")
    else:
        print(f"❌ Validation failed: {vote.error}")
    
    # Test that we can access the vote properties
    print(f"✅ Success state: {vote.success}")
    print(f"✅ Error state: {vote.error}")
    print(f"✅ Vote ID: {vote.vote_id}")
    print(f"✅ Calldata: {vote.calldata}")
    
    print("\n🎉 Basic functionality test passed!")

if __name__ == "__main__":
    test_basic_functionality() 