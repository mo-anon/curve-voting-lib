# Curve DAO Voting Toolkit

A Python package for simulating and preparing Curve DAO governance votes, including adding and killing gauges, with robust validation, simulation, and calldata extraction.

---

## Features

- **Vote Templates:** Easily create and simulate votes for adding or killing gauges.
- **Validation:** Checks input format and types before any onchain simulation.
- **Simulation:** Forks mainnet and simulates the vote, checking for onchain state and execution success.
- **Calldata Extraction:** Optionally outputs the EVM script (calldata) for use in other tools or manual submission.
- **Rich Output:** Step-by-step, colorized terminal output for clarity.
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
PYTHONPATH=. python3 scripts/gauges/add_gauge.py --calldata
```

- By default, uses a test gauge address.  
- Use `--calldata` to print the EVM script for the vote.

### Kill a Gauge

```sh
PYTHONPATH=. python3 scripts/gauges/kill_gauge.py --calldata
```

---

## Customization

You can modify the scripts or extend the templates to:
- Use different gauge addresses, weights, or types.
- Add new vote types by subclassing `VoteTemplate`.

---

## How It Works

1. **Validation:** Checks the format of your input (address, weight, type).
2. **Simulation:** Forks mainnet, simulates the vote, and checks if it would succeed onchain.
3. **Calldata:** If requested, prints the EVM script for the vote.

---

## Development & Testing

Run all tests with:

```sh
pytest
```

---