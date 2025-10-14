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
    relayer="0xe0A1D8C3d243789EC6853b0d00903E70fded32d0",
)

CORN = Chain(
    id=1001,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x5bcA7dDF1bcccB2eE8e46c56bfc9d3CDC77262bC",
)

INK = Chain(
    id=200,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x13DFF1809D1E9ddf9Ac901F47817B7F45220A846",
)

TAC = Chain(
    id=2008,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x5bcA7dDF1bcccB2eE8e46c56bfc9d3CDC77262bC",
)

FANTOM = Chain(
    id=250,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0xc0b338DA0fDD43Dc48539837594cf6363795FEeA",
)

POLYGON = Chain(
    id=137,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x74d6aABD6197E83d963F0B48be9C034F93E8E66d",
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
    relayer="0x97aDC08FA1D849D2C48C5dcC1DaB568B169b0267",
)

BSC = Chain(
    id=56,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x3B519ae13D7CeB72CC922815f5dAaD741aD5087B",
)

MOONBEAM = Chain(
    id=1284,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x3c0a405E914337139992625D5100Ea141a9C4d11",
)

HYPERLIQUID = Chain(
    id=998,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x5bcA7dDF1bcccB2eE8e46c56bfc9d3CDC77262bC",
)

KAVA = Chain(
    id=2222,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x6a2691068C7CbdA03292Ba0f9c77A25F658bAeF5",
)

CELO = Chain(
    id=42220,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x3c0a405E914337139992625D5100Ea141a9C4d11",
)

ETHERLINK = Chain(
    id=42793,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0xC772063cE3e622B458B706Dd2e36309418A1aE42",
)

AVALANCHE = Chain(
    id=43114,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0xC6452F058fF4bb248D852C7b5f0E8753B8DbAbda",
)

AURORA = Chain(
    id=1313161554,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x3c0a405E914337139992625D5100Ea141a9C4d11",
)

PLUME = Chain(
    id=161221135,
    rpc=RPC_NOT_SET,
    broadcaster=bd.STORAGE_PROOFS,
    relayer="0x5bcA7dDF1bcccB2eE8e46c56bfc9d3CDC77262bC",
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
