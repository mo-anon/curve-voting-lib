#!/usr/bin/env python3
"""
Example usage of curve-voting-lib in an IPython notebook with browser wallet support
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voting.core.config import get_config
from voting.templates.gauge import AddGauge, KillGauge

def example_notebook_usage():
    """
    Example of how to use the package in an IPython notebook
    """
    
    # === Configuration ===
    config = get_config()
    
    # === Define vote parameters ===
    TARGET = "ownership"  # or "parameter", "emergency"
    GAUGE_ADDRESS = "0x1234567890123456789012345678901234567890"  # Replace with actual gauge
    WEIGHT = 0
    TYPE_ID = 0
    DESCRIPTION = "Add new gauge for testing"
    
    # === Create vote object ===
    vote = AddGauge(
        config=config,
        gauge_address=GAUGE_ADDRESS,
        weight=WEIGHT,
        type_id=TYPE_ID,
        description=DESCRIPTION
    )
    
    print("=== Vote Configuration ===")
    print(f"Target DAO: {TARGET}")
    print(f"Gauge Address: {GAUGE_ADDRESS}")
    print(f"Weight: {WEIGHT}")
    print(f"Type ID: {TYPE_ID}")
    print(f"Description: {DESCRIPTION}")
    
    # === Step 1: Validate ===
    print("\n=== Step 1: Validation ===")
    if vote.validate():
        print("✅ Validation passed")
    else:
        print(f"❌ Validation failed: {vote.error}")
        return
    
    # === Step 2: Simulate ===
    print("\n=== Step 2: Simulation ===")
    simulation = True  # Set to False to skip simulation
    
    if simulation:
        if vote.simulate():
            print(f"✅ Simulation successful! Vote ID: {vote.vote_id}")
        else:
            print(f"❌ Simulation failed: {vote.error}")
            return
    else:
        print("⏭️ Skipping simulation")
    
    # === Step 3: Live Vote ===
    print("\n=== Step 3: Live Vote ===")
    live_vote = False  # Set to True to create actual vote
    
    if live_vote:
        print("🔗 Connecting to browser wallet...")
        if vote.execute(simulation=False):
            print(f"✅ Live vote created! Vote ID: {vote.vote_id}")
        else:
            print(f"❌ Live vote failed: {vote.error}")
    else:
        print("⏭️ Skipping live vote (simulation only)")
    
    print("\n=== Summary ===")
    print(f"Vote ID: {vote.vote_id}")
    print(f"Success: {vote.success}")
    print(f"Error: {vote.error}")

def example_kill_gauge():
    """
    Example of killing a gauge
    """
    
    config = get_config()
    
    # === Define kill parameters ===
    GAUGE_ADDRESS = "0x1234567890123456789012345678901234567890"  # Replace with actual gauge
    DESCRIPTION = "Kill gauge"
    
    # === Create kill vote object ===
    vote = KillGauge(
        config=config,
        gauge_address=GAUGE_ADDRESS,
        description=DESCRIPTION
    )
    
    print("=== Kill Gauge Configuration ===")
    print(f"Gauge Address: {GAUGE_ADDRESS}")
    print(f"Description: {DESCRIPTION}")
    
    # === Validate ===
    if vote.validate():
        print("✅ Validation passed")
    else:
        print(f"❌ Validation failed: {vote.error}")
        return
    
    # === Simulate ===
    if vote.simulate():
        print(f"✅ Simulation successful! Vote ID: {vote.vote_id}")
    else:
        print(f"❌ Simulation failed: {vote.error}")
        return
    
    # === Live Vote (optional) ===
    live_vote = False
    if live_vote:
        if vote.execute(simulation=False):
            print(f"✅ Live vote created! Vote ID: {vote.vote_id}")
        else:
            print(f"❌ Live vote failed: {vote.error}")

if __name__ == "__main__":
    print("=== Add Gauge Example ===")
    example_notebook_usage()
    
    print("\n" + "="*50 + "\n")
    
    print("=== Kill Gauge Example ===")
    example_kill_gauge() 