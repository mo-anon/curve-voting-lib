import sys
import argparse
from src.core.config import get_config
from src.templates.ramp_a import RampA

def main():
    parser = argparse.ArgumentParser(description="Ramp A parameter for a Curve pool")
    parser.add_argument('--pool-address', type=str, required=True, help='Pool address to ramp A for')
    parser.add_argument('--future-a', type=int, required=True, help='Future A value')
    parser.add_argument('--future-time', type=int, required=True, help='Future time for the ramp')
    parser.add_argument('--calldata', action='store_true', help='Return the EVM script (calldata) for the vote')
    args = parser.parse_args()

    config = get_config()
    
    vote = RampA(
        config=config,
        pool_address=args.pool_address,
        future_a=args.future_a,
        future_time=args.future_time,
        description=f"Ramp A to {args.future_a} at time {args.future_time}"
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