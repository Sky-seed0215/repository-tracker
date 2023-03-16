import requests
import discord
from discord import app_commands, Interaction, Embed, Object, Member
from discord.ext import commands
from typing import Optional, Literal
import datetime
import pytz

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
    async def get_all(self, interaction: Interaction, user: Member):
        embed = Embed(title="Repositories", color=0x1e90ff)
        result = sql.User.get_all_repos(discord_id=user.id)
        if result == []:
            await interaction.response.send_message("No repositories registered.")
        else:
            for i in result:
                embed.add_field(name=f"Prefix: {i.prefix}", value=f"[{i.owner}/{i.repo}](https://github.com/{i.owner}/{i.repo})", inline=False)
            await interaction.response.send_message(embed=embed)

    @group.command(name="remove_all", description="Removes all repositories.")
    async def remove_all_repo(self, interaction: Interaction):
        sql.User.remove_all(discord_id=interaction.user.id)
        await interaction.response.send_message("All registered repositories have been deleted.")

    @group.command(name="issue", description="Displays the specified Issue.")
    async def get_issue(self, interaction: Interaction, prefix: str, number: int, multiple: Optional[Literal["and"]], to: Optional[int]):
        result = sql.User.get_repo(discord_id=interaction.user.id, prefix=prefix)
        url = f"https://api.github.com/repos/{result.owner}/{result.repo}/issues"
        if multiple == "and":
            r = requests.get(url=f"{url}/{str(number)}")
            r2 = requests.get(url=f"{url}/{str(to)}")
            res = r.json()
            res2 = r2.json()
            embed = Embed(color=0x1e90ff, timestamp=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
            embed.add_field(name=res["title"], value=f'{res["body"]}\n\n[open with github.com]({res["html_url"]})')
            embed.add_field(name=res2["title"], value=f'{res2["body"]}\n\n[open with github.com]({res2["html_url"]})')
            embed.set_footer(text=f'issue#{number}:{res["labels"][0]["name"]}, issue#{to}:{res2["labels"][0]["name"]}')
            await interaction.response.send_message(embed=embed)
        else:
            r = requests.get(url=f"{url}/{str(number)}")
            res = r.json()
            embed = Embed(color=discord.Colour.from_str(value=f'#{res["labels"][0]["color"]}'), timestamp=datetime.datetime.now(pytz.timezone('Asia/Tokyo')))
            embed.add_field(name=res["title"], value=f'{res["body"]}\n\n[open with github.com]({res["html_url"]})')
            embed.set_footer(text=f'issue#{number}:{res["labels"][0]["name"]}')
            await interaction.response.send_message(embed=embed)

    @group.command(name="info", description="Displays details of the selected repository.")
    async def info(self, interaction: Interaction, prefix: str):
        repo = sql.User.get_repo(discord_id=interaction.user.id, prefix=prefix)
        url = f"https://api.github.com/repos/{repo.owner}/{repo.repo}"
        r = requests.get(url=url)
        resp = r.json()

        embed = Embed(color=0x1e90ff, timestamp=datetime.datetime.now(pytz.timezone('Asia/Tokyo')), title=resp["full_name"], url=resp["html_url"])
        embed.add_field(name="owner", value=f'[{resp["owner"]["login"]}]({resp["owner"]["url"]})')
        embed.set_image(url=resp["owner"]["avatar_url"])
        embed.add_field(name="description", value=resp["description"])
        embed.add_field(name="archived?", value=resp["archived"])
        embed.add_field(name="license", value=resp["license"]["name"])
        embed.add_field(name="SSH URL", value=resp["ssh_url"], inline=False)
        embed.add_field(name="Clone URL", value=resp["clone_url"], inline=False)
        embed.add_field(name="forks", value=resp["forks"])
        embed.add_field(name="Watchers", value=resp["watchers"])
        embed.add_field(name="default branch", value=resp["default_branch"])
        embed.add_field(name="Open issues", value=resp["open_issues"])

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tracker(bot), guilds=[Object(id=840469180171550752)])
