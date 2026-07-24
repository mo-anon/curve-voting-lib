from dataclasses import dataclass
from typing import Optional, Sequence, TYPE_CHECKING

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
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

CORN = Chain(
    id=1001,
    rpc="https://maizenet-rpc.usecorn.com",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

INK = Chain(
    id=57073,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

TAC = Chain(
    id=239,
    rpc="https://rpc.tac.build",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

FANTOM = Chain(
    id=250,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

POLYGON = Chain(
    id=137,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

SONIC = Chain(
    id=146,
    rpc="https://rpc.soniclabs.com",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0xE5De15A9C9bBedb4F5EC13B131E61245f2983A69",
)

XDC = Chain(
    id=50,
    rpc="https://rpc.xdc.org",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

BSC = Chain(
    id=56,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

MOONBEAM = Chain(
    id=1284,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

HYPERLIQUID = Chain(
    id=999,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

KAVA = Chain(
    id=2222,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

CELO = Chain(
    id=42220,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

ETHERLINK = Chain(
    id=42793,
    rpc="https://node.mainnet.etherlink.com",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

AVALANCHE = Chain(
    id=43114,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

AURORA = Chain(
    id=1313161554,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

PLUME = Chain(
    id=98866,
    rpc="https://rpc.plume.org",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

PLASMA = Chain(
    id=9745,
    rpc="https://rpc.plasma.to",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
)

MONAD = Chain(
    id=143,
    rpc="https://rpc.monad.xyz",
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x900e54EAfE5f05683907a22A0f532D5C25302E1E",
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
