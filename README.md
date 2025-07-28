# Curve DAO Voting Toolkit

A Python package for creating and simulating Curve DAO governance votes, including adding and killing gauges, with validation and simulation capabilities.

---

## Features

- **Vote Templates:** Easily create votes for adding or killing gauges.
- **Validation:** Checks input format and types before any onchain simulation.
- **Simulation:** Forks mainnet and simulates the vote, checking for onchain state and execution success.
- **Calldata Extraction:** Optionally outputs the EVM script (calldata) for use in other tools or manual submission.
- **Simple API:** Easy-to-use classes and methods for vote creation.
- **Tested:** Includes pytest-based tests for core logic.

---

## Installation

Clone the repo and install dependencies (ideally in a virtualenv):

```sh
git clone <your-repo-url>
cd curve-voting-lib
pip install -r requirements.txt
```

---

## Usage

### Add a Gauge

```sh
# Use default test gauge
python3 scripts/gauges/add_gauge.py

# Use custom gauge address
python3 scripts/gauges/add_gauge.py --gauge-address 0x123...

# Get calldata for manual submission
python3 scripts/gauges/add_gauge.py --calldata
```

### Kill a Gauge

```sh
# Kill a specific gauge
python3 scripts/gauges/kill_gauge.py --gauge-address 0x123...

# Get calldata for manual submission
python3 scripts/gauges/kill_gauge.py --gauge-address 0x123... --calldata
```

### Programmatic Usage

```python
from src.core.config import get_config
from src.templates.gauge import AddGauge, KillGauge

# Add a gauge
config = get_config()
vote = AddGauge(config, "0x123...", weight=0, type_id=0)

if vote.execute():
    print(f"Success! Vote ID: {vote.vote_id}")
else:
    print(f"Failed: {vote.error}")

# Kill a gauge
vote = KillGauge(config, "0x123...")
if vote.execute():
    print(f"Success! Vote ID: {vote.vote_id}")
else:
    print(f"Failed: {vote.error}")
```

---

## Adding New Vote Types

To add a new vote type, simply create a new class that inherits from `VoteTemplate`:

```python
# src/templates/ramp_a.py
from src.templates.base import VoteTemplate

class RampA(VoteTemplate):
    def __init__(self, config: dict, pool_address: str, future_a: int, future_time: int):
        super().__init__(config, "Ramp A parameter")
        self.pool_address = pool_address
        self.future_a = future_a
        self.future_time = future_time
    
    def _validate(self) -> bool:
        if not is_valid_address(self.pool_address):
            self.error = "Invalid pool address"
            return False
        return True
    
    def _simulate(self) -> bool:
        # Simulation logic here
        return True
    
    def _create_vote(self) -> bool:
        # Vote creation logic here
        return True
```

Then create a script to use it:

```python
# scripts/ramp_a.py
from src.core.config import get_config
from src.templates.ramp_a import RampA

def main():
    config = get_config()
    vote = RampA(config, "0x...", 1000, 1234567890)
    
    if vote.execute():
        print(f"Success! Vote ID: {vote.vote_id}")
    else:
        print(f"Failed: {vote.error}")

if __name__ == "__main__":
    main()
```

---

## Configuration

Set up your environment variables in a `.env` file:

```env
ALCHEMY_API_KEY=your_alchemy_key
ETHERSCAN_API_KEY=your_etherscan_key
PINATA_TOKEN=your_pinata_token
```

---

## Development & Testing

Run all tests with:

```sh
pytest
```

---

## How It Works

1. **Validation:** Checks the format of your input (address, weight, type).
2. **Simulation:** Forks mainnet, simulates the vote, and checks if it would succeed onchain.
3. **Execution:** Creates the actual vote if simulation passes.