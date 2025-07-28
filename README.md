# Curve DAO Voting Toolkit

A Python package for creating and simulating Curve DAO governance votes, including adding and killing gauges, with validation and simulation capabilities.

---

## Features

- **Vote Templates:** Easily create votes for adding or killing gauges.
- **Validation:** Checks input format and types before any onchain simulation.
- **Simulation:** Forks mainnet and simulates the vote, checking for onchain state and execution success.
- **Live Voting:** Connect to browser wallet for actual vote creation on mainnet.
- **Calldata Extraction:** Optionally outputs the EVM script (calldata) for use in other tools or manual submission.
- **Tested:** Includes pytest-based tests for core logic.

---

## Installation

### Local Development

```sh
git clone <your-repo-url>
cd curve-voting-lib
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Google Colab / Jupyter

```python
!pip install git+https://github.com/mo-anon/curve-voting-lib.git
```

---

## Configuration

Set up your environment variables in a `.env` file:

```env
ALCHEMY_API_KEY=your_alchemy_key
ETHERSCAN_API_KEY=your_etherscan_key
PINATA_TOKEN=your_pinata_token
```

For Google Colab, set them as environment variables:

```python
import os
os.environ['ALCHEMY_API_KEY'] = 'your_alchemy_key'
os.environ['ETHERSCAN_API_KEY'] = 'your_etherscan_key'
os.environ['PINATA_TOKEN'] = 'your_pinata_token'
```

---

## Usage

### CLI Scripts

#### Add a Gauge

```sh
# Use default test gauge
python3 scripts/gauges/add_gauge.py

# Use custom gauge address
python3 scripts/gauges/add_gauge.py --gauge-address 0x123...

# Get calldata for calldata
python3 scripts/gauges/add_gauge.py --calldata
```



### Programmatic Usage

#### Simulation Only

```python
from src.core.config import get_config
from src.templates.gauge import AddGauge

# Get configuration
config = get_config()

# Create vote template
vote = AddGauge(
    config=config,
    gauge_address="0x123...",
    weight=0,
    type_id=0,
    description="Add new gauge"
)

# Simulate the vote
if vote.simulate(verbose=True):
    print(f"Simulation successful! Vote ID: {vote.vote_id}")
else:
    print(f"Simulation failed: {vote.error}")
```

#### Live Voting with Browser Wallet (Google Colab)

```python
from src.core.config import get_config
from src.templates.gauge import AddGauge

# Get configuration
config = get_config()

# Create vote template for live voting
vote = AddGauge(
    config=config,
    gauge_address="0x123...",
    weight=0,
    type_id=0,
    description="Add new gauge",
    simulation=False  # This enables live voting
)

# Create live vote (will connect to browser wallet)
if vote.create_live_vote(verbose=True):
    print(f"Live vote successful! Vote ID: {vote.vote_id}")
else:
    print(f"Live vote failed: {vote.error}")
```

---

## Library Structure

```
curve-voting-lib/
├── src/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── create_vote.py     # Core vote creation logic
│   │   └── vote.py           # Base Vote class
│   ├── templates/
│   │   ├── base.py           # Base VoteTemplate class
│   │   └── gauge.py          # AddGauge template
│   └── utils/
│       ├── constants.py       # DAO addresses and constants
│       └── evm_script.py     # EVM script generation
├── scripts/
│   └── gauges/
│       └── add_gauge.py      # CLI for adding gauges
└── tests/
    └── test_add_gauge.py     # Pytest tests
```

---

## Adding New Vote Types

The library is designed to be easily extensible. To add a new vote type:

### 1. Create a Template Class

Create a new file in `src/templates/` (e.g., `src/templates/example_vote.py`):

```python
import re
import boa
from src.templates.base import VoteTemplate
from src.utils.constants import get_dao_parameters, DAO
from src.core.create_vote import create_vote

class ExampleVote(VoteTemplate):
    """Template for an example vote type"""
    
    def __init__(self, config: dict, target_address: str, parameter: int, description: str = ""):
        super().__init__(config, description)
        self.target_address = target_address
        self.parameter = parameter
        
        # Define the vote payload (contract, function, parameters)
        self.vote_payload = [
            (
                target_address,
                "example_function",
                parameter
            )
        ]
        
    def _validate(self) -> bool:
        """Validate input parameters"""
        if not re.match(r"^0x[a-fA-F0-9]{40}$", self.target_address):
            self.error = "Invalid address format"
            return False
        
        if self.parameter <= 0:
            self.error = "Parameter must be positive"
            return False
        
        return True

    def _simulate(self) -> bool:
        """Simulate the vote on forked mainnet"""
        try:
            # Fork mainnet
            boa.fork(self.config["rpc_url"], allow_dirty=True)
            
            # Get the target contract
            contract = boa.from_etherscan(
                self.target_address,
                name="TargetContract",
                api_key=self.config["etherscan_key"],
            )
            
            # Check if contract exists and has the function
            try:
                contract.example_function(self.parameter)
            except:
                self.error = "Contract does not exist or does not support this function"
                return False
            
            # Simulate the vote
            vote_id = create_vote(
                dao=DAO.OWNERSHIP,
                actions=self.vote_payload,
                description=self.description,
                etherscan_api_key=self.config["etherscan_key"],
                pinata_token=self.config["pinata_token"],
                simulation=True
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Simulation failed: {str(e)}"
            return False
    
    def _create_vote(self, simulation: bool = True) -> bool:
        """Create the actual vote"""
        try:
            vote_id = create_vote(
                dao=DAO.OWNERSHIP,
                actions=self.vote_payload,
                description=self.description,
                etherscan_api_key=self.config["etherscan_key"],
                pinata_token=self.config["pinata_token"],
                simulation=simulation
            )
            
            self.vote_id = vote_id
            return True
            
        except Exception as e:
            self.error = f"Vote creation failed: {str(e)}"
            return False
```

### 2. Create a CLI Script

Create a script in `scripts/` (e.g., `scripts/example_vote.py`):

```python
import argparse
from src.core.config import get_config
from src.templates.example_vote import ExampleVote

def main():
    parser = argparse.ArgumentParser(description="Create an example vote")
    parser.add_argument("--target-address", required=True, help="Target contract address")
    parser.add_argument("--parameter", type=int, required=True, help="Parameter value")
    parser.add_argument("--calldata", action="store_true", help="Output calldata only")
    
    args = parser.parse_args()
    
    config = get_config()
    vote = ExampleVote(
        config=config,
        target_address=args.target_address,
        parameter=args.parameter,
        description="Example vote"
    )
    
    if vote.create_vote(simulation=True):
        print(f"Success! Vote ID: {vote.vote_id}")
        if args.calldata and vote.calldata:
            print(f"Calldata: {vote.calldata.hex()}")
    else:
        print(f"Failed: {vote.error}")

if __name__ == "__main__":
    main()
```

### 3. Add to Package Exports

Update `src/__init__.py` to export your new template:

```python
from .templates.example_vote import ExampleVote

__all__ = [
    # ... existing exports ...
    "ExampleVote",
]
```

### 4. Create Tests

Create tests in `tests/` (e.g., `tests/test_example_vote.py`):

```python
import pytest
from src.core.config import get_config
from src.templates.example_vote import ExampleVote

def test_example_vote_validation():
    config = get_config()
    vote = ExampleVote(config, "0x1234567890123456789012345678901234567890", 1000)
    assert vote.validate() == True

def test_example_vote_invalid_address():
    config = get_config()
    vote = ExampleVote(config, "invalid_address", 1000)
    assert vote.validate() == False
```

---

## Key Design Principles

### 1. Template Pattern
All vote types inherit from `VoteTemplate`, which provides:
- Common validation and simulation logic
- Standardized error handling
- Consistent API across all vote types

### 2. Separation of Concerns
- **Validation**: Input format and type checking
- **Simulation**: Onchain state verification
- **Execution**: Actual vote creation

### 3. Configuration Management
- Environment-based configuration
- Support for different environments (local, Colab)
- API key management

### 4. Error Handling
- Comprehensive error messages
- Graceful failure handling
- Debug information for troubleshooting

---

## Development & Testing

### Run Tests

```sh
pytest
```

---

## Troubleshooting

### Debug Mode

Enable verbose output to see detailed information:

```python
vote.simulate(verbose=True)
vote.create_live_vote(verbose=True)
```