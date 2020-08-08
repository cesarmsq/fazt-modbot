from discord.ext import commands

from .database import session


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = None

    async def start(self, *args, **kwargs):
        self.db_session = session()
        await super().start(*args, **kwargs)

    async def close(self, *args, **kwargs):
        await super().close()
        self.db_session.remove()
