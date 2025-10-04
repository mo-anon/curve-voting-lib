from dataclasses import dataclass
from typing import Optional, Sequence, TYPE_CHECKING

from voting.constants import ZERO_ADDRESS
from voting.config import DAOParameters
import voting.xgov.broadcasters as bd

if TYPE_CHECKING:
    from voting.xgov import BroadcastParams


RPC_NOT_SET = "RPC_NOT_SET"


@dataclass(frozen=True)
class Chain:
    id: int
    rpc: str
    broadcaster: bd.BaseBroadcaster
    relayer: str

    def agent_address(self, dao_agent: DAOParameters) -> str:
        return self.broadcaster.agent_address(self, dao_agent)

    def broadcast(
        self,
        dao_agent: DAOParameters,
        fork_params,
        messages: Sequence[tuple],
        params: Optional["BroadcastParams"] = None,
    ) -> None:
        self.broadcaster.broadcast(self, dao_agent, fork_params, messages, params)


GNOSIS = Chain(
    id=100,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

CORN = Chain(
    id=1001,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

INK = Chain(
    id=200,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

TAC = Chain(
    id=2008,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

FANTOM = Chain(
    id=250,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x002599c7D4299A268b332B3240d60308f93C99eC",
)

POLYGON = Chain(
    id=137,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x91e95f16f7F1b988391A869771Ffb50Df4ceBDF7",
)

SONIC = Chain(
    id=146,
    rpc="https://rpc.soniclabs.com",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0xE5De15A9C9bBedb4F5EC13B131E61245f2983A69",
)

XDC = Chain(
    id=50,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

BSC = Chain(
    id=56,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x37b6d6d425438a9f8e40C8B4c06c10560967b678",
)

MOONBEAM = Chain(
    id=1284,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

HYPERLIQUID = Chain(
    id=998,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

KAVA = Chain(
    id=2222,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0xA5961898870943c68037F6848d2D866Ed2016bcB",
)

CELO = Chain(
    id=42220,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

ETHERLINK = Chain(
    id=42793,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

AVALANCHE = Chain(
    id=43114,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x3895064FD74a86542206C4c39eb1bf14BB9aF9a6",
)

AURORA = Chain(
    id=1313161554,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)

PLUME = Chain(
    id=161221135,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer=ZERO_ADDRESS,
)


OPTIMISM = Chain(
    id=10,
    rpc="https://mainnet.optimism.io",
    broadcaster=bd.OPTIMISM_MAINNET,
    relayer="0x8e1e5001C7B8920196c7E3EdF2BCf47B2B6153ff",
)

FRAXTAL = Chain(
    id=252,
    rpc="https://rpc.frax.com",
    broadcaster=bd.OPTIMISM_GENERIC,
    relayer="0x7BE6BD57A319A7180f71552E58c9d32Da32b6f96",
)

MANTLE = Chain(
    id=5000,
    rpc=RPC_NOT_SET,
    broadcaster=bd.MANTLE,
    relayer="0xB50B9a0D8A4ED8115Fe174F300465Ea4686d86Df",
)

BASE = Chain(
    id=8453,
    rpc=RPC_NOT_SET,
    broadcaster=bd.BASE,
    relayer="0xCb843280C5037ACfA67b8D4aDC71484ceD7C48C9",
)


ARBITRUM = Chain(
    id=42161,
    rpc="https://arb1.arbitrum.io/rpc",
    broadcaster=bd.ARBITRUM,
    relayer="0xb7b0FF38E0A01D798B5cd395BbA6Ddb56A323830",
)


X_LAYER = Chain(
    id=196,
    rpc="https://rpc.xlayer.tech",
    broadcaster=bd.POLYGON_ZKEVM_X_LAYER,
    relayer="0x9D9e70CA10fE911Dee9869F21e5ebB24A9519Ade",
)


TAIKO = Chain(
    id=167000,
    rpc="https://rpc.taiko.xyz",
    broadcaster=bd.TAIKO_GENERIC,
    relayer="0xE5De15A9C9bBedb4F5EC13B131E61245f2983A69",
)
