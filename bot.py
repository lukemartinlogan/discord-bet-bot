import os
from gamble import Gamble
from discord import Intents, Embed
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv

load_dotenv()
bot = Bot(command_prefix="1")
slash = SlashCommand(bot, sync_commands=True)
token = os.getenv('DISCORD_TOKEN')
servers = [int(os.getenv("SERVER_1", None))]
print(f'using token: {token}')
print(f'servers: {servers}')

@slash.slash(name='register', description='Registers a user')
async def register(ctx: SlashContext):
    gamble = Gamble.GetInstance()
    await ctx.send(gamble.register(f"<@!{ctx.author.id}>"))

@slash.slash(
    name='bet',
    description='Bet credits on a user',
    options=[
        create_option(
            name="on",
            description="User to bet on",
            option_type=3,
            required=True
        ),
        create_option(
            name="amt",
            description="Number of credits to bet",
            option_type=4,
            required=True
        )
    ]
)
async def bet(ctx: SlashContext, on, amt):
    gamble = Gamble.GetInstance()
    better = f"<@!{ctx.author.id}>"
    await ctx.send(gamble.bet(better, on, amt))

@slash.slash(name='withdraw', description='Abstain from betting')
async def withdraw(ctx: SlashContext):
    gamble = Gamble.GetInstance()
    await ctx.send(gamble.withdraw(f"<@!{ctx.author.id}>"))

@slash.slash(
    name='winner',
    description='Input the winner of the round',
    options=[
        create_option(
            name="winner",
            description="The winner of the bet",
            option_type=3,
            required=True
        ),
        create_option(
            name="squad_win",
            description="Whether squad won or not",
            option_type=5,
            required=True
        )
    ]
)
async def winner(ctx: SlashContext, winner, squad_win):
    gamble = Gamble.GetInstance()
    await ctx.send(gamble.winner(winner, squad_win))

@slash.slash(name='balance', description='Check user balance')
async def balance(ctx: SlashContext):
    gamble = Gamble.GetInstance()
    embed = gamble.balance(f"<@!{ctx.author.id}>")
    await ctx.send(embed=embed)

@slash.slash(name='give', description='Give a user credits')
async def give(ctx: SlashContext, user, amt):
    gamble = Gamble.GetInstance()
    await ctx.send(gamble.give(f"{user}", amt))

@slash.slash(name='give_all', description='Give all users credits')
async def give_all(ctx: SlashContext, amt):
    gamble = Gamble.GetInstance()
    await ctx.send(gamble.give_all(amt))

