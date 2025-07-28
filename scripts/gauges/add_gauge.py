import sys
import argparse
from src.core.config import get_config
from src.templates.gauge import AddGauge

def main():
    parser = argparse.ArgumentParser(description="Add a gauge to Curve DAO")
    parser.add_argument('--calldata', action='store_true', help='Return the EVM script (calldata) for the vote')
    parser.add_argument('--gauge-address', type=str, default="0xeB896fB7D1AaE921d586B0E5a037496aFd3E2412", help='Gauge address to add')
    args = parser.parse_args()

    config = get_config()
    
    vote = AddGauge(
        config=config,
        gauge_address=args.gauge_address,
        weight=0,
        type_id=0,
        description="Add new gauge"
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

