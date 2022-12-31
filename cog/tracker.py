import requests
from discord import app_commands, Interaction, Embed, Object
from discord.ext import commands

import utils.sql_utils as sql
from utils.sql_utils import DuplicateKeyException

class Tracker(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="repo", description="Commands related to Github repositories.")

    @group.command(name="register", description="Register a github repository")
    async def register(self, interaction: Interaction, prefix: str, owner: str, repository: str):
        url = f'https://github.com/{owner}/{repository}'
        resp = requests.head(url=url)
        if resp.status_code == 200:
            try:
                sql.User.insert_repo(discord_id=interaction.user.id, prefix=prefix, owner=owner, repo=repository)
                await interaction.response.send_message(f"Repository {owner}/{repository} is registered.\nThe corresponding prefix is `{prefix}`\nURL: https://github.com/{owner}/{repository}")
            except DuplicateKeyException:
                result = sql.User.get_repo(discord_id=interaction.user.id, prefix=prefix)
                await interaction.response.send_message(f"This prefix is already attached to other repositories.\n\n```Registered Repository: {result.owner}/{result.repo}\nPrefix: {result.prefix}```")
        else:
            await interaction.response.send_message(f"Repository: {owner}/{repository} does not exist.")

    @group.command(name="remove", description="Removes the specified repository from the list.")
    async def remove(self, interaction: Interaction, prefix: str):
        try:
            result = sql.User.get_repo(discord_id=interaction.user.id, prefix=prefix)
            sql.User.remove_repo(discord_id=interaction.user.id, prefix=prefix)
            await interaction.response.send_message(f"Repository: `{result.owner}/{result.repo}` was deleted.")
        except IndexError:
            await interaction.response.send_message(f"Repository not found for the specified prefix `{prefix}`.")

    @group.command(name="get_all", description="Displays all registered repositories.")
    async def get_all(self, interaction: Interaction):
        embed = Embed(title="Repositories", color=0x1e90ff)
        result = sql.User.get_all_repos(discord_id=interaction.user.id)
        for i in result:
            embed.add_field(name=f"Prefix: {i.prefix}", value=f"[{i.owner}/{i.repo}](https://github.com/{i.owner}/{i.repo})", inline=False)
        await interaction.response.send_message(embed=embed)

    @group.command(name="remove_all", description="Removes all repositories.")
    async def remove_all_repo(self, interaction: Interaction):
        sql.User.remove_all(discord_id=interaction.user.id)
        await interaction.response.send_message("All registered repositories have been deleted.")

async def setup(bot):
    await bot.add_cog(Tracker(bot), guilds=[Object(id=840469180171550752)])
