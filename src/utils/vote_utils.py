import logging
import warnings
import boa
import sys
import os
from dotenv import load_dotenv

from typing import Dict, List, Tuple
from datetime import datetime

from boa.contracts.abi.abi_contract import ABIContract
from boa.contracts.vyper.vyper_contract import VyperContract
from hexbytes import HexBytes
from rich.logging import RichHandler
from rich.console import Console

from src.utils.constants import DAO, get_dao_parameters

# Note: decoder module is not available - these imports are commented out
# from decoder.decoder import decode_input
# from decoder.ipfs import get_ipfs_hash_from_description

load_dotenv()

warnings.filterwarnings("ignore")

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("rich")
console = Console(file=sys.stdout)  # For rich console output


# Note: MissingVote exception and prepare_evm_script function are now imported from evm_script.py
from src.utils.evm_script import MissingVote, prepare_evm_script





#########################
### CODE FOR DECODING ###
#########################

# Note: MissingVote exception is now imported from evm_script.py


def get_evm_script(target, actions):
    """Prepares EVM script and creates an on-chain AragonDAO vote.

    Args:
        target (dict): ownership / parameter / emergency
        actions (list(tuple)): ("target addr", "fn_name", *args)
        vote_creator (str): msg.sender address
        description (str): Description of the on-chain governance proposal

    Returns:
        str: vote ID of the created vote.
    """

    aragon_voting = boa.from_etherscan(target["voting"], name="AragonVoting", api_key=os.getenv("ETHERSCAN_API_KEY"))

    #vote_creator = boa.env.eoa
    #assert aragon_voting.canCreateNewVote(vote_creator), "dev: user cannot create new vote"

    evm_script = prepare_evm_script(target, actions)
    return evm_script




def get_vote_script(vote_id: str, vote_type: str) -> str:
    
    try:
        # working until here
        boa.fork(os.getenv("ALCHEMY_API_KEY"), allow_dirty=True)
        voting_contract_address = get_dao_voting_contract(vote_type)
        voting_contract = boa.from_etherscan(voting_contract_address, name="test", api_key=os.getenv("ETHERSCAN_API_KEY"))
        vote = voting_contract.getVote(vote_id)
        script = vote[9]
        return script
    # to borad of an exception. what to do here?
    except Exception as e:
        raise MissingVote(f"Could not grab vote script: {e}")



# working
def get_vote_data(vote_id: str, vote_type: str) -> str:
    boa.fork(os.getenv("ALCHEMY_API_KEY"), allow_dirty=True)
    voting_contract_address = get_dao_voting_contract(vote_type)
    voting_contract = boa.from_etherscan(voting_contract_address, name="test", api_key=os.getenv("ETHERSCAN_API_KEY"))
    vote_data = voting_contract.getVote(vote_id)

    return {
        "yea": vote_data[6],
        "nay": vote_data[7],
        "votingPower": vote_data[8],
        "open": vote_data[0],
        "executed": vote_data[1],
        "startDate": vote_data[2],
    }


# working 
def decode_vote_script(script):
    idx = 4

    votes = []
    while idx < len(script):

        boa.fork(os.getenv("ALCHEMY_API_KEY"), allow_dirty=True)

        # can just replace ape.Contract(...) with boa.from_etherscan(script[idx : idx + 20], name="target")
        # works; get target contract address
        target = script[idx : idx + 20]
        target = target.hex()
        target = "0x" + target
        idx += 20

        voting_contract = boa.from_etherscan(target, name="test", api_key=os.getenv("ETHERSCAN_API_KEY"))
        length = int(script[idx : idx + 4].hex(), 16)
        idx += 4

        # get calldata to execute for the dao:
        calldata = script[idx : idx + length]
        idx += length

        # target and calldata matching
        # Note: decode_input function is not available due to missing decoder module
        # fn, inputs = decode_input(target, calldata)
        fn = {"name": "unknown_function"}  # Placeholder
        inputs = []  # Placeholder
        agent = None

        # print decoded vote:
        # target is either target_addr or target_contract. idk... yet...
        if "0x" + str(calldata[:4].hex()) == "0xb61d27f6":
            agent = target
            target = inputs[0]

            # Note: decode_input function is not available due to missing decoder module
            # fn, inputs = decode_input(target, inputs[2])
            fn = {"name": "unknown_function"}  # Placeholder
            inputs = inputs[2] if len(inputs) > 2 else []  # Placeholder
            inputs_with_names = get_inputs_with_names(fn, inputs)
            formatted_inputs = format_fn_inputs(inputs_with_names)
            formatted_output = (
                f"Call via agent: [yellow]{agent}[/]\n"
                f" ├─ [bold]To[/]: [green]{target}[/]\n"
                f" ├─ [bold]Function[/]: [yellow]{fn['name']}[/]\n"
                f" └─ [bold]Inputs[/]: \n{formatted_inputs}\n"
            )
        else:
            inputs_with_names = get_inputs_with_names(fn, inputs)
            formatted_inputs = format_fn_inputs(inputs_with_names)
            formatted_output = (
                f"Direct call\n "
                f" ├─ [bold]To[/]: [green]{target}[/]\n"
                f" ├─ [bold]Function[/]: [yellow]{fn['name']}[/]\n"
                f" └─ [bold]Inputs[/]: {formatted_inputs}\n"
            )

        vote = {
            "agent": agent if agent else None,
            "target": target,
            "function": fn['name'],
            "inputs": inputs_with_names,
            "formatted_output": formatted_output,
        }

        votes.append(vote)

    return votes


# works
def decode_vote_data(data: dict, vote_type: str):
    yes = round(data["yea"] / 1e18, 2)
    no = round(data["nay"] / 1e18, 2)
    total_votes = data["yea"] + data["nay"]
    total_voting_power = data["votingPower"]

    VOTE_TIME = 604800

    # Handle edge case where there are no votes at all
    if total_votes == 0 or total_voting_power == 0:
        quorum = 0
        support = 0
    else:
        quorum = total_votes / total_voting_power
        support = data["yea"] / total_votes

    required_support = 0.51 if vote_type == "ownership" else 0.30
    required_quorum = 0.30 if vote_type == "ownership" else 0.15

    if data["open"]:  # Voting is ongoing
        pass_status = "[yellow]Voting Ongoing[/]"
    else:  # Voting is closed
        if total_votes == 0 or total_voting_power == 0:
            pass_status = "[red]Vote Invalid: No Votes[/]"
        elif support >= required_support and quorum >= required_quorum:
            # Check if the vote has been executed
            execution_status = (
                "[green]Executed[/]" if data["executed"] else "[red]Not Executed[/]"
            )
            pass_status = (
                f"[green]Vote Passed[/] ([grey]Execution Status[/]: {execution_status})"
            )
        else:
            if support < required_support and quorum < required_quorum:
                failure_reason = "Both Support and Quorum Not Met"
            elif support < required_support:
                failure_reason = "Support Not Met"
            else:
                failure_reason = "Quorum Not Met"
            pass_status = f"[red]Vote Failed: {failure_reason}[/]"

    start = datetime.utcfromtimestamp(data["startDate"]).strftime("%Y-%m-%d %H:%M:%S")
    end = datetime.utcfromtimestamp(data["startDate"] + VOTE_TIME).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    formatted_output = (
        f"[bold]Results[/]: {pass_status}\n"
        f" ├─ [grey]Voting Start Time[/]: {start}\n"
        f" ├─ [grey]Voting End Time[/]: {end}\n"
        f" ├─ [green]Votes For[/]: {yes}\n"
        f" ├─ [red]Votes Against[/]: {no}\n"
        f" ├─ [blue]Support[/]: {round(support * 100, 2)}% (Required: {int(required_support * 100)}%)\n"
        f" └─ [purple]Quorum[/]: {round(quorum * 100, 2)}% (Minimum: {int(required_quorum * 100)}%)\n"
    )

    results = {
        "start": data["startDate"],
        "end": data["startDate"] + VOTE_TIME,
        "votingPower": data["votingPower"],
        "open": data["open"],
        "executed": data["executed"],
        "yes": data["yea"],
        "no": data["nay"],
        "support": support,
        "quorum": quorum,
        "formatted_output": formatted_output,
    }

    return results


def get_inputs_with_names(abi, inputs):
    arg_names = []
    for i in range(len(inputs)):
        argname = abi["inputs"][i]["name"]
        arg_names.append(argname)

    inputs_with_names = list(zip(arg_names, inputs))
    return inputs_with_names


def format_fn_inputs(inputs_with_names):
    if len(inputs_with_names) == 0:
        return ""

    if len(inputs_with_names) == 1:
        name, arg = inputs_with_names[0]
        return f"    └─ [bold]{name}[/]: [yellow]{arg}[/]"

    formatted_args = ""
    for name, arg in inputs_with_names[:-1]:
        formatted_args += f"    ├─ [bold]{name}[/]: [yellow]{arg}[/]\n"
    name, arg = inputs_with_names[-1]
    formatted_args += f"    └─ [bold]{name}[/]: [yellow]{arg}[/]"
    return formatted_args


