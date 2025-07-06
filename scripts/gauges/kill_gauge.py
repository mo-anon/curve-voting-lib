import sys
import argparse
from src.core.config import VoteConfig
from src.templates.gauge import KillGauge

def main():
    parser = argparse.ArgumentParser(description="Simulate and optionally return calldata for killing a gauge.")
    parser.add_argument('--calldata', action='store_true', help='Return the EVM script (calldata) for the vote')
    args = parser.parse_args()

    config = VoteConfig(is_forked=True)
    gauge = KillGauge(
        config=config,
        gauge_address="0xeB896fB7D1AaE921d586B0E5a037496aFd3E2412",
        description="Kill gauge for testing"
    )
    if not gauge.validate(show_info=True):
        print("Validation failed:", gauge.validate().errors)
        sys.exit(1)
    sim_result = gauge.simulate(show_info=True, skip_validation=True, return_calldata=args.calldata)
    if not sim_result:
        print("Simulation failed:", sim_result.message)
        sys.exit(1)
    print("Simulation successful!")
    if args.calldata and sim_result.details.get("evm_script"):
        print("EVM Script:", sim_result.details["evm_script"])

if __name__ == "__main__":
    main() 