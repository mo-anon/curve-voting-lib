from dataclasses import dataclass
import boa


@dataclass(frozen=True)
class DAOParameters():
    agent: str
    voting: str
    token: str
    quorum: int


OWNERSHIP = DAOParameters(
    agent="0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
    voting="0xE478de485ad2fe566d49342Cbd03E49ed7DB3356",
    token="0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    quorum=30,
)

PARAMETER = DAOParameters(
    agent="0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    voting="0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    token="0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    quorum=15,
)


# Aliasing to improve vote debugging
for attribute in ['agent', 'voting', 'token']:
    for dao_name, dao_params in [('ownership', OWNERSHIP), ('parameter', PARAMETER)]:
        name = f"{attribute}_{dao_name}"
        address = getattr(dao_params, attribute)
        boa.env.alias(address, name)

            
CONVEX_VOTER_PROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
boa.env.alias(CONVEX_VOTER_PROXY, "convex")