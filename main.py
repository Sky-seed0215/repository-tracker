import os
import discord
from discord.ext import commands

from local.key import TOKEN

intents = discord.Intents.all()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!tc ', intents=intents)
    async def on_ready(self):
        await self.load_extension("jishaku")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        print('Logged on as')

    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        await self.process_commands(ctx)

if __name__ == "__main__":
    bot = MyBot()
    bot.run(str(TOKEN))
