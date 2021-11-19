# bot.py
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix='!')

users = {}

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.command()
async def ping():
    await client.say('Pong')

@client.event
async def on_message(message):
    cmds = message.content.split()
    #!add_users [user1] ... [userN]
    if '!add_users' == cmds[0]:
        for user in cmds[1:]:
            users[user] = {
                'earnings': 0,
                'cur-bet': None
            }

    #!bet [better] [betting-on]
    if '!bet' == cmds[0]:
        better = cmds[1]
        on = cmds[2]
        users[better]['cur-bet'] = on
        if on == 'None':
            users[better]['cur-bet'] = None

    #!winner [user]
    if '!winner' == cmds[0]:
        winner = cmds[1]
        if winner not in users:
            await message.channel.send(f'{winner} is not in the user list')
            return

        pot = len(users.keys())
        correct_bets = [user for user,profile in users.items() if profile['cur-bet'] == winner]
        score = pot / len(correct_bets) if len(correct_bets) > 0 else 0

        #Update rewards
        for user in correct_bets:
            users[user]['earnings'] += score
        users[winner]['earnings'] += 2

        #Print winners and scores
        if len(correct_bets) == 0:
            congrats = 'None of you predicted correctly. Losers.\n'
        else:
            congrats = f"Congrats! The following sweaty people guessed correctly: {','.join(correct_bets)}\n"
        scores = ""
        for user,profile in users.items():
            scores += f"{user}: {profile['earnings']} shmeckles\n"
        await  message.channel.send(congrats + scores)

client.run(TOKEN)

#!add_user luke wef
#!bet luke luke
#!bet wef wef
#!winner luke
