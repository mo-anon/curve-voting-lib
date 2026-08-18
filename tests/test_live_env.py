from types import SimpleNamespace

import pytest

import voting.live_env as live_env_module
from voting.live_env import BrowserEnv, CustomEnv


@pytest.fixture
def fork_chain():
    """These unit tests mock Boa environments and do not need a mainnet fork."""
    yield


class FakeBrowserBoaEnv:
    def __init__(self, chain_id):
        self.chain_id = chain_id
        self.eoa = "0x0000000000000000000000000000000000000001"
        self.requested_chain_ids = []

    def get_chain_id(self):
        return self.chain_id

    def set_chain_id(self, chain_id):
        self.requested_chain_ids.append(chain_id)
        self.chain_id = chain_id


def test_browser_env_switches_to_requested_chain(monkeypatch):
    browser_env = FakeBrowserBoaEnv(chain_id=146)
    monkeypatch.setattr(live_env_module.boa, "env", browser_env)
    monkeypatch.setattr(live_env_module.boa, "set_browser_env", lambda: None)

    assert BrowserEnv().set(chain_id=1)
    assert browser_env.requested_chain_ids == [1]
    assert browser_env.get_chain_id() == 1


def test_browser_env_does_not_switch_when_chain_is_already_correct(monkeypatch):
    browser_env = FakeBrowserBoaEnv(chain_id=1)
    monkeypatch.setattr(live_env_module.boa, "env", browser_env)
    monkeypatch.setattr(live_env_module.boa, "set_browser_env", lambda: None)

    assert BrowserEnv().set(chain_id=1)
    assert browser_env.requested_chain_ids == []


def test_browser_env_fails_when_switch_does_not_take_effect(monkeypatch):
    browser_env = FakeBrowserBoaEnv(chain_id=146)
    browser_env.set_chain_id = lambda chain_id: None
    monkeypatch.setattr(live_env_module.boa, "env", browser_env)
    monkeypatch.setattr(live_env_module.boa, "set_browser_env", lambda: None)

    assert not BrowserEnv().set(chain_id=1)


def test_custom_env_rejects_rpc_for_wrong_chain(monkeypatch):
    network_env = FakeBrowserBoaEnv(chain_id=146)
    network_env.add_account = lambda account: None
    monkeypatch.setattr(live_env_module.boa, "env", network_env)
    monkeypatch.setattr(live_env_module.boa, "set_network_env", lambda rpc: None)

    account = SimpleNamespace(address=network_env.eoa)
    live_env = CustomEnv("https://example.invalid", account, ask_to_proceed=False)

    assert not live_env.set(chain_id=1)
