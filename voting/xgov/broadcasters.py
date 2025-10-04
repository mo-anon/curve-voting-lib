from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Sequence, TYPE_CHECKING

import boa
from boa.contracts.abi.abi_contract import ABIContract

from voting.abi import (
    broadcasters as broadcaster_abis,
    agent as agent_abi,
    relayer as relayer_abi,
)
from voting.config import DAOParameters, OWNERSHIP, PARAMETER
from voting.constants import ZERO_ADDRESS
from voting.context import use_clean_prepare_calldata

if TYPE_CHECKING:
    from voting.xgov.chains import Chain


class BaseBroadcaster:
    def __init__(self, address: str, *, abi_key: Optional[str] = None):
        resolved_abi_key = (
            abi_key if abi_key is not None else getattr(type(self), "abi_key", None)
        )
        if resolved_abi_key is None:
            raise ValueError("abi_key must be provided by subclass or constructor")
        self.address = address
        self.abi_key = resolved_abi_key

    def build(self) -> ABIContract:
        return broadcaster_abis[self.abi_key].at(self.address)

    def relayer(self, chain: Chain):
        if not chain.relayer or chain.relayer == ZERO_ADDRESS:
            raise ValueError(f"Relayer not known for chain {chain.id}")
        return relayer_abi.at(chain.relayer)

    def agent_address(self, chain: Chain, dao_agent: DAOParameters) -> str:
        relayer_contract = self.relayer(chain)
        lookup = {
            OWNERSHIP: "OWNERSHIP_AGENT",
            PARAMETER: "PARAMETER_AGENT",
        }[dao_agent]
        return getattr(relayer_contract, lookup)()

    def agent(self, chain: Chain, dao_agent: DAOParameters):
        return agent_abi.at(self.agent_address(chain, dao_agent))

    def _chunk_messages(self, messages: Sequence[tuple], size: int = 8):
        for i in range(0, len(messages), size):
            yield messages[i : i + size]

    def _calculate_relay_gas(
        self,
        chain: Chain,
        dao_agent: DAOParameters,
        fork_params,
        messages: Sequence[tuple],
    ) -> List[int]:
        with use_clean_prepare_calldata():
            with boa.fork(**fork_params):
                agent_contract = self.agent(chain, dao_agent)
                relayer_contract = self.relayer(chain)
                costs = []
                for chunk in self._chunk_messages(messages):
                    costs.append(
                        self._relay_gas(agent_contract, relayer_contract, chunk)
                    )
                return costs

    def _relay_gas(
        self, agent_contract, relayer_contract, messages_chunk: Sequence[tuple]
    ) -> int:
        with boa.env.prank(relayer_contract.address):
            agent_contract.execute(messages_chunk)
            gas = agent_contract.call_trace().gas_used
            return self._relay_gas_extra() + gas

    def _relay_gas_extra(self) -> int:
        return 100_000

    def broadcast(
        self,
        chain: Chain,
        dao_agent: DAOParameters,
        fork_params,
        messages: Sequence[tuple],
        params: Optional["BroadcastParams"] = None,
    ) -> None:
        raise NotImplementedError


@dataclass
class BroadcastParams:
    """Optional parameters that can override broadcaster defaults."""

    gas_limit: Optional[int] = None
    max_fee_per_gas: Optional[int] = None  # Arbitrum
    destination_data: Optional[bytes] = None  # Generic solutions
    force_update: Optional[bool] = None  # PolygonZkEvm


class StorageProofsBroadcaster(BaseBroadcaster):
    abi_key = "storage_proofs"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        for chunk in self._chunk_messages(messages):
            broadcaster_contract.broadcast(chain.id, chunk)


class OptimismBroadcaster(BaseBroadcaster):
    abi_key = "optimism"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        gas_limits = (
            params.gas_limit
            if params and params.gas_limit
            else self._calculate_relay_gas(chain, dao_agent, fork_params, messages)
        )
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            args = [chunk]
            if gas_limit:
                args.append(gas_limit)
            broadcaster_contract.broadcast(*args)


class OptimismGenericBroadcaster(BaseBroadcaster):
    abi_key = "optimism_generic"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        destination_data = (
            params.destination_data if params and params.destination_data else None
        )
        if not destination_data:
            assert broadcaster_contract.destination_data(chain.id)[2] != ZERO_ADDRESS, (
                f"No destination_data set for {chain.id}"
            )

        gas_limits = (
            params.gas_limit
            if params and params.gas_limit
            else self._calculate_relay_gas(chain, dao_agent, fork_params, messages)
        )
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            args = [chain.id, chunk, gas_limit or 0]
            if destination_data:
                args.append(destination_data)
            broadcaster_contract.broadcast(*args)


class ArbitrumBroadcaster(BaseBroadcaster):
    abi_key = "arbitrum"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        gas_limits = (
            params.gas_limit
            if params and params.gas_limit
            else self._calculate_relay_gas(chain, dao_agent, fork_params, messages)
        )
        max_fee_per_gas = (
            params.max_fee_per_gas
            if params and params.max_fee_per_gas
            else self._max_fee_per_gas()
        )
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            broadcaster_contract.broadcast(chunk, gas_limit, max_fee_per_gas)

    def _max_fee_per_gas(self):
        return 10**9


class ArbitrumGenericBroadcaster(BaseBroadcaster):
    abi_key = "arbitrum_generic"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        destination_data = (
            params.destination_data if params and params.destination_data else None
        )
        if not destination_data:
            assert broadcaster_contract.destination_data(chain.id)[2] != ZERO_ADDRESS, (
                f"No destination_data set for {chain.id}"
            )

        gas_limits = (
            params.gas_limit
            if params and params.gas_limit
            else self._calculate_relay_gas(chain, dao_agent, fork_params, messages)
        )
        max_fee_per_gas = (
            params.max_fee_per_gas
            if params and params.max_fee_per_gas
            else self._max_fee_per_gas()
        )
        for chunk, gas_limit in zip(self._chunk_messages(messages), gas_limits):
            args = [chain.id, chunk, gas_limit, max_fee_per_gas]
            if destination_data:
                args.append(destination_data)
            broadcaster_contract.broadcast(*args)

    def _max_fee_per_gas(self):
        return 10**9


class PolygonZkevmBroadcaster(BaseBroadcaster):
    abi_key = "polygon_zkevm"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        for chunk in self._chunk_messages(messages):
            args = [chunk]
            if params and params.force_update is not None:
                args.append(params.force_update)
            broadcaster_contract.broadcast(*args)


class PolygonZkevmGenericBroadcaster(BaseBroadcaster):
    abi_key = "polygon_zkevm_generic"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        destination_data = (
            params.destination_data if params and params.destination_data else None
        )
        if not destination_data:
            assert broadcaster_contract.destination_data(chain.id)[1] != ZERO_ADDRESS, (
                f"No destination_data set for {chain.id}"
            )

        for chunk in self._chunk_messages(messages):
            args = [
                chain.id,
                chunk,
                params.force_update
                if params and params.force_update is not None
                else True,
            ]
            if destination_data:
                args.append(destination_data)
            broadcaster_contract.broadcast(*args)


class TaikoGenericBroadcaster(BaseBroadcaster):
    abi_key = "taiko_generic"

    def broadcast(self, chain, dao_agent, fork_params, messages, params=None):
        broadcaster_contract = self.build()
        destination_data = (
            params.destination_data if params and params.destination_data else None
        )
        if not destination_data:
            assert broadcaster_contract.destination_data(chain.id)[1] != ZERO_ADDRESS, (
                f"No destination_data set for {chain.id}"
            )

        for chunk in self._chunk_messages(messages):
            args = [chain.id, chunk]
            if destination_data:
                args.append(destination_data)
            broadcaster_contract.broadcast(*args)


# Instances used by chains
STORAGE_PROOFS = StorageProofsBroadcaster("0x7BA33456EC00812C6B6BB6C1C3dfF579c34CC2cc")
OPTIMISM_MAINNET = OptimismBroadcaster("0x8e1e5001c7b8920196c7e3edf2bcf47b2b6153ff")
BASE = OptimismBroadcaster("0xcb843280c5037acfa67b8d4adc71484ced7c48c9")
MANTLE = OptimismBroadcaster("0xB50B9a0D8A4ED8115Fe174F300465Ea4686d86Df")
OPTIMISM_GENERIC = OptimismGenericBroadcaster(
    "0xE0fE4416214e95F0C67Dc044AAf1E63d6972e0b9"
)
ARBITRUM = ArbitrumBroadcaster("0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830")
ARBITRUM_GENERIC = ArbitrumGenericBroadcaster(
    "0x94630a56519c00Be339BBd8BD26f342Bf4bd7eE0"
)
POLYGON_ZKEVM_X_LAYER = PolygonZkevmBroadcaster(
    "0x9D9e70CA10fE911Dee9869F21e5ebB24A9519Ade"
)
POLYGON_ZKEVM_GENERIC = PolygonZkevmGenericBroadcaster(
    "0xB5e7fE8eA8ECbd33504485756fCabB5f5D29C051"
)
TAIKO_GENERIC = TaikoGenericBroadcaster("0x05a3a7b57cb60419ff0b087e9eae8469c28ac8cd")
