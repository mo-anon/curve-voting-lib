from abc import abstractmethod, ABC
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from voting.abi import agent, broadcasters, relayer
from voting.config import DAOParameters, OWNERSHIP, PARAMETER

import boa

# Constants
EMPTY_ADDRESS = "0x0000000000000000000000000000000000000000"


class BroadcastType(Enum):
    STORAGE_PROOFS = "storage_proofs"

    OPTIMISM = "optimism"
    OPTIMISM_GENERIC = "optimism_generic"

    ARBITRUM = "arbitrum"
    ARBITRUM_GENERIC = "arbitrum_generic"

    POLYGON_ZKEVM = "polygon_zkevm"
    POLYGON_ZKEVM_GENERIC = "polygon_zkevm_generic"

    TAIKO_GENERIC = "taiko_generic"


@dataclass
class BroadcastParams:
    """Optional parameters that can override broadcaster defaults"""
    gas_limit: Optional[int] = None
    max_fee_per_gas: Optional[int] = None  # Arbitrum
    destination_data: Optional[bytes] = None  # Generic solutions
    force_update: Optional[bool] = None  # PolygonZkEvm


# Broadcaster addresses by type and chain
BROADCASTERS = {
    # Base broadcasters
    BroadcastType.STORAGE_PROOFS: "0x7BA33456EC00812C6B6BB6C1C3dfF579c34CC2cc",
    
    # Optimism chain broadcasters
    BroadcastType.OPTIMISM: {
        10: "0x8e1e5001c7b8920196c7e3edf2bcf47b2b6153ff",  # mainnet
        8453: "0xcb843280c5037acfa67b8d4adc71484ced7c48c9",  # Base
        5000: "0xB50B9a0D8A4ED8115Fe174F300465Ea4686d86Df",  # Mantle
    },
    BroadcastType.OPTIMISM_GENERIC: "0xE0fE4416214e95F0C67Dc044AAf1E63d6972e0b9",
    
    # Arbitrum chain broadcasters
    BroadcastType.ARBITRUM: {
        42161: "0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830",  # Arbitrum
    },
    BroadcastType.ARBITRUM_GENERIC: "0x94630a56519c00Be339BBd8BD26f342Bf4bd7eE0",
    
    # Polygon zkEVM chain broadcasters
    BroadcastType.POLYGON_ZKEVM: {
        196: "0x9D9e70CA10fE911Dee9869F21e5ebB24A9519Ade",  # X-layer
    },
    BroadcastType.POLYGON_ZKEVM_GENERIC: "0xB5e7fE8eA8ECbd33504485756fCabB5f5D29C051",
    
    # Taiko chain broadcasters
    BroadcastType.TAIKO_GENERIC: "0x05a3a7b57cb60419ff0b087e9eae8469c28ac8cd",
}

# Chain configuration: broadcaster type and relayer address
CHAIN_CONFIG: Dict[int, Dict[str, Union[BroadcastType, str]]] = {
    # Storage proofs
    100: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},   # Gnosis
    1001: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Corn
    200: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Ink
    2008: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # TAC
    250: {"type": BroadcastType.STORAGE_PROOFS, "relayer": "0x002599c7D4299A268b332B3240d60308f93C99eC"},   # Fantom
    137: {"type": BroadcastType.STORAGE_PROOFS, "relayer": "0x91e95f16f7F1b988391A869771Ffb50Df4ceBDF7"},   # Polygon
    146: {"type": BroadcastType.STORAGE_PROOFS, "relayer": "0xE5De15A9C9bBedb4F5EC13B131E61245f2983A69"},  # Sonic
    50: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # XDC
    56: {"type": BroadcastType.STORAGE_PROOFS, "relayer": "0x37b6d6d425438a9f8e40C8B4c06c10560967b678"},   # BSC
    1284: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Moonbeam
    998: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Hyperliquid
    2222: {"type": BroadcastType.STORAGE_PROOFS, "relayer": "0xA5961898870943c68037F6848d2D866Ed2016bcB"},   # Kava
    42220: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Celo
    42793: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Etherlink
    43114: {"type": BroadcastType.STORAGE_PROOFS, "relayer": "0x3895064FD74a86542206C4c39eb1bf14BB9aF9a6"},  # Avalanche
    1313161554: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Aurora
    161221135: {"type": BroadcastType.STORAGE_PROOFS, "relayer": ""},  # Plume
    
    # OP stack
    10: {"type": BroadcastType.OPTIMISM, "relayer": "0x8e1e5001C7B8920196c7E3EdF2BCf47B2B6153ff"},   # Optimism
    252: {"type": BroadcastType.OPTIMISM_GENERIC, "relayer": "0x7BE6BD57A319A7180f71552E58c9d32Da32b6f96"},   # Fraxtal
    5000: {"type": BroadcastType.OPTIMISM, "relayer": "0xB50B9a0D8A4ED8115Fe174F300465Ea4686d86Df"},   # Mantle
    8453: {"type": BroadcastType.OPTIMISM, "relayer": "0xCb843280C5037ACfA67b8D4aDC71484ceD7C48C9"},  # Base

    # Arbitrum
    42161: {"type": BroadcastType.ARBITRUM, "relayer": "0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830"},  # Arbitrum

    # Polygon zkEVM
    196: {"type": BroadcastType.POLYGON_ZKEVM, "relayer": "0x9D9e70CA10fE911Dee9869F21e5ebB24A9519Ade"},   # X-layer

    # Taiko
    167000: {"type": BroadcastType.TAIKO_GENERIC, "relayer": "0xE5De15A9C9bBedb4F5EC13B131E61245f2983A69"},  # Taiko
}


class Broadcaster(ABC):
    """Abstract base class for all broadcaster implementations"""
    
    def __init__(self, chain_id: int, dao_agent: DAOParameters, fork_params, broadcaster):
        self.chain_id = chain_id
        self.dao_agent = dao_agent
        self.fork_params = fork_params  # save Env in case of re-execution
        self.broadcaster = broadcaster
        self.relayer = relayer.at(CHAIN_CONFIG.get(chain_id, {}).get("relayer", ""))
    
    @abstractmethod
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        """Broadcast messages with chain-specific logic"""
        pass

    def calculate_relay_gas(self, messages: List[tuple]) -> List[int]:
        with boa.env.fork(**self.fork_params):
            agent_ = self.get_agent()
            return [self._relay_gas(agent_, chunk) for chunk in self._chunk_messages(messages)]

    def _chunk_messages(self, messages: List[tuple], chunk_size: int = 8) -> List[List[tuple]]:
        """Split messages into max possible chunks"""
        return [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]

    def _relay_gas(self, agent, messages: List[tuple]) -> int:
        """
        Considered to be called before Broadcasting to calculate gas usage.
        Better to be done separately to reduce impact from other functionality.
        """
        with boa.env.prank(self.relayer):
            boa.env.evm.reset_gas_used()
            agent.execute(messages)
            gas = agent.call_trace().gas_used
            return self._relay_gas_extra() + gas

    def _relay_gas_extra(self):
        """Gas for messaging infra before relayer hits agent.relay()"""
        return 100_000

    def get_agent(self):
        agent_address = getattr(self.relayer, {
            OWNERSHIP: "OWNERSHIP_AGENT",
            PARAMETER: "PARAMETER_AGENT",
            # EMERGENCY: "EMERGENCY_AGENT",
        }[self.dao_agent])()
        return agent.at(agent_address)


class StorageProofsBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        for chunk in self._chunk_messages(messages):
            self.broadcaster.broadcast(self.chain_id, chunk)


class OptimismBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        gas_limits = params.gas_limit if params.gas_limit else self.calculate_relay_gas(messages)
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            args = [chunk]
            if gas_limit:
                args.append(gas_limit)

            self.broadcaster.broadcast(*args)

    # def _relay_gas_extra(self):  TODO
    #     return ovm_chain.enqueueL2GasPrepaid()


class OptimismGenericBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        destination_data = params.destination_data if params and params.destination_data else None
        if not destination_data:
            assert self.broadcaster.destination_data(self.chain_id)[2] != EMPTY_ADDRESS, f"No destination_data set for {self.chain_id}"

        gas_limits = params.gas_limit if params.gas_limit else self.calculate_relay_gas(messages)
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            args = [self.chain_id, chunk, gas_limit or 0]  # always include some gas_limit, so destination_data doesn't occur earlier
            
            if destination_data:
                args.append(destination_data)

            self.broadcaster.broadcast(*args)


class ArbitrumBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        gas_limits = params.gas_limit if params.gas_limit else self.calculate_relay_gas(messages)
        max_fee_per_gas = params.max_fee_per_gas if params and params.max_fee_per_gas else self._max_fee_per_gas()
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            self.broadcaster.broadcast(chunk, gas_limit, max_fee_per_gas)

    def _max_fee_per_gas(self):
        return 10 ** 9


class ArbitrumGenericBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        destination_data = params.destination_data if params and params.destination_data else None
        if not destination_data:
            assert self.broadcaster.destination_data(self.chain_id)[2] != EMPTY_ADDRESS, f"No destination_data set for {self.chain_id}"

        gas_limits = params.gas_limit if params.gas_limit else self.calculate_relay_gas(messages)
        max_fee_per_gas = params.max_fee_per_gas if params and params.max_fee_per_gas else self._max_fee_per_gas()
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            args = [self.chain_id, chunk, gas_limit, max_fee_per_gas]

            if destination_data:
                args.append(destination_data)

            self.broadcaster.broadcast(*args)

    def _max_fee_per_gas(self):
        return 10 ** 9


class PolygonZkevmBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        """Broadcast using Polygon zkEVM format"""
        for chunk in self._chunk_messages(messages):
            args = [chunk]
            if params and params.force_update:
                args.append(params.force_update)

            self.broadcaster.broadcast(*args)


class PolygonZkevmGenericBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        """Broadcast using Polygon zkEVM generic format"""
        destination_data = params.destination_data if params and params.destination_data else None
        if not destination_data:
            assert self.broadcaster.destination_data(self.chain_id)[1] != EMPTY_ADDRESS, f"No destination_data set for {self.chain_id}"

        for chunk in self._chunk_messages(messages):
            args = [self.chain_id, chunk, params.force_update if params and params.force_update else True]
            
            if destination_data:
                args.append(destination_data)

            self.broadcaster.broadcast(*args)


class TaikoGenericBroadcaster(Broadcaster):
    def broadcast(self, messages: List[tuple], params: Optional[BroadcastParams] = None):
        """Broadcast using Taiko generic format"""
        for chunk in self._chunk_messages(messages):
            args = [self.chain_id, chunk]
            if params and params.destination_data:
                args.append(params.destination_data)

            self.broadcaster.broadcast(*args)


class BroadcasterFactory:
    """Factory for creating broadcaster instances"""
    
    @staticmethod
    def create_broadcaster(dao_agent: DAOParameters, fork_params) -> Broadcaster:
        """Create a broadcaster instance based on chain ID and DAO agent"""
        chain_id = boa.env.get_chain_id()
        
        # Get chain configuration
        chain_config = CHAIN_CONFIG.get(chain_id)
        if not chain_config:
            raise ValueError(f"Unsupported chain ID: {chain_id}")
        
        broadcaster_type = chain_config["type"]
        
        # Get broadcaster address
        broadcaster_address = BROADCASTERS.get(broadcaster_type)
        if isinstance(broadcaster_address, dict):
            # Handle chain-specific addresses (like Optimism)
            broadcaster_address = broadcaster_address.get(chain_id)
            if not broadcaster_address:
                raise ValueError(f"No broadcaster address for chain {chain_id}")
        
        if not broadcaster_address:
            raise ValueError(f"No broadcaster address for type {broadcaster_type}")
        
        # Get broadcaster ABI and create contract instance
        broadcaster_abi = broadcasters.get(broadcaster_type.value)
        if not broadcaster_abi:
            raise ValueError(f"No ABI for broadcaster type {broadcaster_type}")
        
        broadcaster_contract = broadcaster_abi.at(broadcaster_address)
        
        # Map broadcaster type to class
        broadcaster_map = {
            # Storage proofs broadcasters
            BroadcastType.STORAGE_PROOFS: StorageProofsBroadcaster,
            
            # Optimism chain broadcasters
            BroadcastType.OPTIMISM: OptimismBroadcaster,
            BroadcastType.OPTIMISM_GENERIC: OptimismGenericBroadcaster,
            
            # Arbitrum chain broadcasters
            BroadcastType.ARBITRUM: ArbitrumBroadcaster,
            BroadcastType.ARBITRUM_GENERIC: ArbitrumGenericBroadcaster,
            
            # Polygon zkEVM chain broadcasters
            BroadcastType.POLYGON_ZKEVM: PolygonZkevmBroadcaster,
            BroadcastType.POLYGON_ZKEVM_GENERIC: PolygonZkevmGenericBroadcaster,
            
            # Taiko chain broadcasters
            BroadcastType.TAIKO_GENERIC: TaikoGenericBroadcaster,
        }
        
        broadcaster_class = broadcaster_map.get(broadcaster_type)
        if not broadcaster_class:
            raise ValueError(f"Unsupported broadcaster type: {broadcaster_type}")
        
        return broadcaster_class(chain_id, dao_agent, fork_params, broadcaster_contract)
