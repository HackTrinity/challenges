from typing import Type, List, Any, Dict, Tuple, Awaitable

from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from maubot import Plugin, MessageEvent
from maubot.handlers import command

class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy('flag')

class PatrickPlugin(Plugin):
    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()
        self.allowed = set()

    async def _send_flag(self, evt):
        await evt.reply(f'Tá cead agat. Seo é an bratach: `{self.config["flag"]}`')

    @command.passive('an bhfuil cead agam dul go (dtí|dti) an leithreas', case_insensitive=True)
    async def handle_please(self, evt: MessageEvent, _: List[Tuple[str, str]]):
        self.allowed.add(evt.sender)
        await self._send_flag(evt)

    @command.passive('flag', case_insensitive=True)
    async def handle_flag(self, evt: MessageEvent, _: List[Tuple[str, str]]):
        if evt.sender in self.allowed:
            await self._send_flag(evt)
        else:
            await evt.reply(
                "I didn't banish the snakes from Ireland for nothing. " +
                "If you want the flag you need to ask for permission in the way every Irish student should know!")
