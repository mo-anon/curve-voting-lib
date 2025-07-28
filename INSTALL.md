# Installation Guide

## Google Colab Installation

```python
# Install from GitHub
!pip install git+https://github.com/yourusername/curvefi.git#subdirectory=curve-voting-lib

# Or if you have the repo locally and want to install from local path
!pip install -e /path/to/curve-voting-lib
```

## Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/curvefi.git
cd curvefi/curve-voting-lib

# Install in development mode
pip install -e .

# Or install from GitHub directly
pip install git+https://github.com/yourusername/curvefi.git#subdirectory=curve-voting-lib
```

## Environment Setup

Create a `.env` file in the project root with your API keys:

```env
ALCHEMY_API_KEY=your_alchemy_api_key_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here
PINATA_TOKEN=your_pinata_token_here
```

## Usage in Google Colab

```python
# Import the package
from src.core.config import get_config
from src.templates.gauge import AddGauge

# Get configuration
config = get_config()

# Create a vote
vote = AddGauge(
    config=config,
    gauge_address="0x1234567890123456789012345678901234567890",
    weight=0,
    type_id=0,
    description="Add new gauge for testing"
)

# Validate
if vote.validate():
    print("✅ Validation passed")
    
    # Simulate
    if vote.execute(simulation=True):
        print(f"✅ Simulation successful! Vote ID: {vote.vote_id}")
        
        # Live vote (optional)
        if vote.execute(simulation=False):
            print(f"✅ Live vote created! Vote ID: {vote.vote_id}")
```

## Dependencies

The package requires:
- `titanoboa==0.2.6` - For Ethereum contract interaction
- `vyper==0.4.0` - For Vyper contract compilation
- `python-dotenv>=1.0.0` - For environment variable management
- `hexbytes>=0.3.0` - For hex data handling

## Troubleshooting

If you encounter dependency conflicts, try:

```bash
pip install "titanoboa==0.2.3" "vyper==0.4.0"
``` 