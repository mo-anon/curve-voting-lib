import boa
import logging

from eth_account import Account


logger = logging.getLogger(__name__)


class LiveEnv:
    ...

    def set(self, chain_id: int = 1) -> bool:
        pass


class BrowserEnv(LiveEnv):
    @staticmethod
    def set(chain_id: int = 1) -> bool:
        try:
            boa.set_browser_env()

            if boa.env.get_chain_id() != chain_id:
                boa.env.set_chain_id(chain_id)

            actual_chain_id = boa.env.get_chain_id()
            if actual_chain_id != chain_id:
                raise RuntimeError(
                    f"Expected chain {chain_id}, connected to {actual_chain_id}"
                )
        except Exception as e:
            logger.error(f"Failed to configure browser wallet: {e}.")
            return False
        logger.info(
            f"Connected to browser wallet as {boa.env.eoa} on chain {actual_chain_id}"
        )
        return True


class CustomEnv(LiveEnv):
    def __init__(self, rpc, account: Account, ask_to_proceed: bool = True):
        self.rpc = rpc  # This could be None and fetched from forked state
        self.account = account

        self.ask_to_proceed = ask_to_proceed

    def set(self, chain_id: int = 1) -> bool:
        if self.ask_to_proceed:
            print("Press ENTER to continue..")
            input()
            print("Proceeding")

        try:
            boa.set_network_env(self.rpc)
            boa.env.add_account(self.account)
            actual_chain_id = boa.env.get_chain_id()
            if actual_chain_id != chain_id:
                raise RuntimeError(
                    f"Expected chain {chain_id}, connected to {actual_chain_id}"
                )
        except Exception as e:
            logger.error(f"Failed to connect to network: {e}.")
            return False
        return True
