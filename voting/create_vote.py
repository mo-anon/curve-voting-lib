from __future__ import annotations
from contextlib import contextmanager, ExitStack
import os
from typing import Optional, TYPE_CHECKING

import boa
import logging
from dotenv import load_dotenv
from hexbytes import HexBytes

from voting.config import CONVEX_VOTER_PROXY, DAOParameters
from requests import request
import hashlib
import json
from datetime import datetime
from voting import abi 
from boa.util.abi import abi_decode

from voting.context import use_dao, use_prepare_calldata, use_clean_prepare_calldata, get_dao

if TYPE_CHECKING:
    from voting.xgov.chains import Chain

logger = logging.getLogger(__name__)
load_dotenv()


def _pin_to_ipfs(description: str) -> str:
    # Create cache directory if it doesn't exist
    cache_dir = os.path.expanduser("~/.cache/curve-voting-lib")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "ipfs_cache.json")
    
    # Create a hash of the description for cache key
    description_hash = hashlib.sha256(description.encode()).hexdigest()
    
    # Load existing cache
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.warning("Could not load IPFS cache, starting fresh")
            cache = {}
    
    # Check if description is already cached
    if description_hash in cache:
        ipfs_hash = cache[description_hash]
        logger.info(f"Found cached IPFS hash for description.")
        return f"ipfs:{ipfs_hash}"

    pinata_token = os.getenv("PINATA_JWT")
    if not pinata_token:
        raise ValueError("PINATA_JWT environment variable is required")

    # TODO this is a legacy endpoint and should be updated before it breaks
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {pinata_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "pinataContent": {"text": description},
        "pinataMetadata": {"name": f"vote_description_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"},
        "pinataOptions": {"cidVersion": 1},
    }

    response = request("POST", url, json=payload, headers=headers)

    if not (200 <= response.status_code < 400):
        logger.error(f"IPFS pinning failed with status {response.status_code}: {response.text}")
        raise Exception(f"Failed to pin to IPFS: HTTP {response.status_code}")
    
    response_data = response.json()
    ipfs_hash = response_data["IpfsHash"]
    logger.info(f"Successfully pinned vote description to IPFS: {ipfs_hash}")
    
    # Cache the result
    cache[description_hash] = ipfs_hash
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        logger.info(f"Cached IPFS hash for future use")
    except IOError as e:
        logger.warning(f"Could not save IPFS cache: {e}")

    return f"ipfs:{ipfs_hash}"


def _prepare_evm_script(dao: DAOParameters, actions):
    aragon_agent = abi.aragon_agent.at(dao.agent)

    evm_script = bytes.fromhex("00000001")

    for address, calldata in actions:
        agent_calldata = aragon_agent.execute.prepare_calldata(address, 0, calldata)

        length = bytes.fromhex(hex(len(agent_calldata.hex()) // 2)[2:].zfill(8))
        evm_script = (
            evm_script
            + bytes.fromhex(aragon_agent.address[2:])
            + length
            + agent_calldata
        )

    evm_script = HexBytes(evm_script)

    return evm_script


def _generate_preview(dao: DAOParameters, actions):
    """
    Generates a human-readable preview of the transaction payload.
    This version assumes all actions are valid and decodable.
    """
    preview_blocks = []
    for address, calldata in actions:
        
        block = f"Call via agent ({dao.agent}):\n"

        # Directly get the contract and function, assuming they exist
        contract = boa.env.lookup_contract(address)
        method_id = calldata[:4]
        func = contract.method_id_map[method_id]

        # Directly decode arguments, assuming it will succeed
        arg_data = calldata[4:]
        decoded_inputs = abi_decode(func.signature, arg_data)

        # Format the decoded inputs into a readable string
        inputs_list = [
            f"('{abi_input['type']}', '{abi_input['name']}', '{value}')"
            for abi_input, value in zip(func._abi['inputs'], decoded_inputs)
        ]
        inputs_str = f"[{', '.join(inputs_list)}]"
        
        # Build the preview block for this action
        block += f" ├─ To: {address}\n"
        block += f" ├─ Function: {func.name}\n"
        block += f" └─ Inputs: {inputs_str}\n"
        preview_blocks.append(block)

    # Join each action's preview block with a newline for clear separation
    print("Calldata")
    print("\n\n".join(block.strip() for block in preview_blocks))


def _create_vote(
        dao: DAOParameters, 
        actions,
        description: str,
        live: bool = False,
) -> int:
    logger.info(f"Creating vote in {'live' if live else 'simulation'} mode")
    
    # Prepare the EVM script
    evm_script = _prepare_evm_script(dao, actions)
    logger.info(f"EVM script prepared.")

    # For now, use empty string as placeholder

    # Get the voting contract
    voting = abi.voting.at(dao.voting)
    logger.info(f"Voting contract loaded: {voting.address}")

    # Always sim regardless of whether the vote is going live or not
    vote_id = voting.newVote(evm_script, "", False, False, sender=CONVEX_VOTER_PROXY)

    logger.info("Simulating vote creation")
    assert voting.canVote(vote_id, CONVEX_VOTER_PROXY)
    with boa.env.prank(CONVEX_VOTER_PROXY):
        voting.vote(vote_id, True, False)

    boa.env.time_travel(seconds=voting.voteTime())

    logger.info("Simulating vote execution")
    assert voting.canExecute(vote_id)
    voting.executeVote(vote_id)


    # Live voting
    if live:
        vote_description_hash = _pin_to_ipfs(description)
        try:
            boa.set_browser_env()
        except Exception as e:
            logger.error(f"Failed to connect to browser wallet: {e}.\nIf you're running this script in a non-browser environment, please use google colab or jupyter notebook.")
            return None
        logger.info("Connected to browser wallet")

        # Refresh contract binding so calls use the browser environment signer
        voting = abi.voting.at(dao.voting)

        assert voting.canCreateNewVote(boa.env.eoa), "EOA cannot create new vote. Either there isn't enough veCRV balance or EOA created a vote less than 12 hours ago."

        vote_id = voting.newVote(evm_script, vote_description_hash, False, False)
        logger.info(f"Live vote created with ID: {vote_id}")

    return vote_id


@contextmanager
def vote(
    dao: DAOParameters,
    description: str,
    live: bool = False
):
    """
    A context manager to patch boa's ABIFunction.prepare_calldata that
    generates a transaction payload.

    This context manager also behaves like a prank (where the pranked
    user is the dao agent) and like an anchor (changes are reverted
    after the `with` block).

    Inside the `with` block, any call to a mutable function on an
    ABIContract will have its calldata captured. The payload is
    stored as a list of [target_address, calldata] pairs.
    """
    # TODO forbid ops like deploying contracts inside to keep the vote clean

    captured_actions = []

    def _patched_prepare_calldata(self, *args, **kwargs):
        with use_clean_prepare_calldata():
            calldata = self.prepare_calldata(*args, **kwargs)
        if self.is_mutable:
            contract_address = str(self.contract.address)
            captured_actions.append([contract_address, calldata])
        return calldata

    with ExitStack() as stack:
        def _cleanup():
            print(f"Metadata\n{description}\n")
            _generate_preview(dao, captured_actions)
            _create_vote(dao, captured_actions, description, live)

        stack.callback(_cleanup)

        stack.enter_context(boa.env.prank(dao.agent)) 
        stack.enter_context(boa.env.anchor())
        stack.enter_context(use_dao(dao))
        stack.enter_context(use_prepare_calldata(_patched_prepare_calldata))

        yield


@contextmanager
def xvote(
    chain: Chain,
    rpc: str,
    broadcaster_parameters: Optional[dict]=None,
):
    """
    Works similarly to `vote` and is intended to be used inside a vote context:

    ```py
    from voting.xgov.chains import FRAXTAL

    with vote(OWNERSHIP, description="[Frax] Set things."):
        with xvote(FRAXTAL, "https://rpc.frax.com"):
            things.set()
    ```
    """

    messages = []

    def _patched_prepare_calldata(self, *args, **kwargs):
        with use_clean_prepare_calldata():
            calldata = self.prepare_calldata(*args, **kwargs)
        if self.is_mutable:
            contract_address = str(self.contract.address)
            messages.append((contract_address, calldata))
        return calldata  # calldata is prepared, but I need gas_used available after execution

    fork_params = {"url": rpc, "allow_dirty": True}

    dao_params = get_dao()

    with ExitStack() as stack:
        stack.enter_context(boa.env.anchor())
        stack.enter_context(boa.fork(**fork_params))

        stack.enter_context(boa.env.prank(chain.agent_address(dao_params)))
        stack.enter_context(use_prepare_calldata(_patched_prepare_calldata))

        yield
    # TODO: how to represent xgov votes?
    chain.broadcast(dao_params, fork_params, messages, broadcaster_parameters)


@contextmanager
def vote_test():
    """
    Context manager to do tests inside a vote context, so they aren't taken into actions.

    ```py
    with vote(OWNERSHIP, description="Set things."):
        things.set()
        with vote_test():
            things.do_something()
            assert things.went_as_set()
    """
    with use_clean_prepare_calldata():
        yield
