import sys
import argparse
from src.core.config import get_config
from src.templates.gauge import KillGauge

def main():
    parser = argparse.ArgumentParser(description="Kill a gauge from the Gauge Controller")
    parser.add_argument('--calldata', action='store_true', help='Return the EVM script (calldata) for the vote')
    parser.add_argument('--gauge-address', type=str, required=True, help='Gauge address to kill')
    args = parser.parse_args()

    config = get_config()
    
    vote = KillGauge(
        config=config,
        gauge_address=args.gauge_address,
        description="Kill gauge"
    )
    
    if vote.execute():
        print(f"✅ Success! Vote ID: {vote.vote_id}")
        if args.calldata and vote.calldata:
            print(f"📄 Calldata: {vote.calldata}")
    else:
        print(f"❌ Failed: {vote.error}")
        sys.exit(1)

if __name__ == "__main__":
    main() 