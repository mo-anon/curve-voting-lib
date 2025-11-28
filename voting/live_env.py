import boa
import logging

from eth_account import Account


logger = logging.getLogger(__name__)


class LiveEnv:
    ...

    def set(self) -> bool:
        pass


class BrowserEnv(LiveEnv):
    def set(self) -> bool:
        try:
            boa.set_browser_env()
        except Exception as e:
            logger.error(f"Failed to connect to browser wallet: {e}.")
            return False
        logger.info(f"Connected to browser wallet as {boa.env.eoa}")


class CustomEnv(LiveEnv):
    def __init__(self, url, account: Account, ask_to_proceed: bool = True):
        self.url = url  # This could be None and fetched from forked state
        self.account = account

        self.ask_to_proceed = ask_to_proceed

    def set(self) -> bool:
        if self.ask_to_proceed:
            print("Press ENTER to continue..")
            input()

        try:
            boa.set_network_env(self.url)
            boa.env.add_account(self.account)
        except Exception as e:
            logger.error(f"Failed to connect to network: {e}.")
            return False
        return True
