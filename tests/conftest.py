import json
from pathlib import Path
from typing import TYPE_CHECKING

import nonebot
import pytest
from nonebug import NONEBOT_INIT_KWARGS
from nonebug.app import App
from pytest_mock import MockerFixture

if TYPE_CHECKING:
    from nonebot.plugin import Plugin


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "driver": "~none",
        "input_config": {
            "base": "master",
            "adapter_path": "adapter_path",
            "bot_path": "bot_path",
            "plugin_path": "plugin_path",
        },
        "github_repository": "owner/repo",
        "github_run_id": "123456",
        "github_event_path": "event_path",
    }


@pytest.fixture(scope="session", autouse=True)
def load_plugin(nonebug_init: None) -> set["Plugin"]:
    return nonebot.load_plugins(str(Path(__file__).parent.parent / "src" / "plugins"))


@pytest.fixture()
async def app(app: App, tmp_path: Path, mocker: MockerFixture):
    from src.plugins.publish.config import plugin_config

    adapter_path = tmp_path / "adapters.json"
    with adapter_path.open("w") as f:
        json.dump(
            [
                {
                    "module_name": "module_name1",
                    "project_link": "project_link1",
                    "name": "name",
                    "desc": "desc",
                    "author": "author",
                    "homepage": "https://v2.nonebot.dev",
                    "tags": [],
                    "is_official": False,
                },
            ],
            f,
        )
    bot_path = tmp_path / "bots.json"
    with bot_path.open("w") as f:
        json.dump(
            [
                {
                    "name": "name",
                    "desc": "desc",
                    "author": "author",
                    "homepage": "https://v2.nonebot.dev",
                    "tags": [],
                    "is_official": False,
                },
            ],
            f,
        )
    plugin_path = tmp_path / "plugins.json"
    with plugin_path.open("w") as f:
        json.dump(
            [
                {
                    "module_name": "module_name1",
                    "project_link": "project_link1",
                    "name": "name",
                    "desc": "desc",
                    "author": "author",
                    "homepage": "https://v2.nonebot.dev",
                    "tags": [],
                    "is_official": False,
                },
            ],
            f,
        )

    mocker.patch.object(plugin_config.input_config, "adapter_path", adapter_path)
    mocker.patch.object(plugin_config.input_config, "bot_path", bot_path)
    mocker.patch.object(plugin_config.input_config, "plugin_path", plugin_path)
    mocker.patch.object(plugin_config, "skip_plugin_test", False)

    return app


@pytest.fixture(autouse=True, scope="function")
def clear_cache(app: App):
    """每次运行前都清除 cache"""
    from src.plugins.publish.validation import check_url

    check_url.cache_clear()
