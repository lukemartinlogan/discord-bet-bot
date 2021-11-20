# bot.py
import os
import json
import threading
import numpy as np
import discord
from discord.ext import commands
#from dotenv import load_dotenv

#load_dotenv()

class DiscordBot:
    bot_ = None

    @staticmethod
    def GetInstance():
        if DiscordBot.bot_ is None:
            DiscordBot.bot_ = DiscordBot()
        return DiscordBot.bot_

    def __init__(self):
        self.token_ = os.getenv('DISCORD_TOKEN')
        self.lock_ = threading.Lock()
        self.is_loaded_ = False
        self.users_ = {}
        self.winning_squad_ = 4
        self.most_dmg_ = 2

    def store_results(self):
        info = {
            'users': self.users_,
            'winning_squad': self.winning_squad_,
            'most_dmg': self.most_dmg_
        }
        with open('bets.json', 'w') as fp:
            json.dump(info, fp)

    def load_results(self):
        if not os.path.exists('bets.json'):
            return
        with open('bets.json', 'r') as fp:
            info = json.load(fp)
        self.users_ = info['users']
        self.winning_squad_ = info['winning_squad']
        self.most_dmg_ = info['most_dmg']
        print(f"self.users_: {self.users_}")

    def add_users(self, user_list):
        for user in user_list:
            self.users_[user] = {
                'balance': 0,
                'bet-on': None,
                'bet-amt': 0
            }
        print(f"Added users {user_list}")

    def set_bet(self, better, on, amt = 1):
        self.users_[better]['bet-on'] = on
        self.users_[better]['bet-amt'] = float(amt)
        self.users_[better]['balance'] -= float(amt)
        if on == 'None':
            self.users_[better]['bet-on'] = None
            self.users_[better]['bet-amt'] = 0
        print(f"{better} bets on {on} for {amt}")

    def set_most_dmg(self, winner, squad_win):
        squad_win = True if squad_win == 'yes' else False
        if winner not in self.users_:
            return f'{winner} is not in the user list'

        pot = sum([profile['bet-amt'] for profile in self.users_.values()])
        correct_betters = [user for user,profile in self.users_.items() if profile['bet-on'] == winner]
        correct_bets = np.array([(profile['bet-on'] == winner) for profile in self.users_.values()])
        weights = np.array([profile['bet-amt'] for profile in self.users_.values()])
        weights = weights*correct_bets
        net_weight = np.sum(weights)
        if net_weight:
            weights /= net_weight
        print(weights)

        #Reward for guessing correctly
        for profile,weight in zip(self.users_.values(), weights):
            profile['gain'] = pot*weight - profile['bet-amt']
            profile['balance'] += pot*weight

        #Reward for winning the game
        if squad_win:
            for profile in self.users_.values():
                profile['gain'] += self.winning_squad_
                profile['balance'] += self.winning_squad_

        #Reward for doing most damage
        self.users_[winner]['gain'] += self.most_dmg_
        self.users_[winner]['balance'] += self.most_dmg_

        #Store the results
        self.store_results()

        #Print winners and scores
        if net_weight == 0:
            congrats = 'None of you predicted correctly. Losers.\n'
        else:
            congrats = f"Congrats! The following sweaty people guessed correctly: {','.join(correct_betters)}\n"
        scores = ""
        for user,profile in self.users_.items():
            scores += f"{user}: gain={profile['gain']}, balance={profile['balance']} shmeckles\n"
        return congrats + scores

    def process_message(self, message):
        cmds = message.content.split()
        output = None

        self.lock_.acquire()
        #!add_users [user1] ... [userN]
        if '!add_users' == cmds[0]:
            self.add_users(cmds[1:])
        #!bet [better] [betting-on]
        if '!bet' == cmds[0]:
            if len(cmds[1:]) == 3:
                self.set_bet(cmds[1], cmds[2], cmds[3])
            else:
                self.set_bet(cmds[1], cmds[2])
        #!winner [user]
        if '!most_dmg' == cmds[0]:
            output = self.set_most_dmg(cmds[1], cmds[2])
        self.lock_.release()

        return output


client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    bot = DiscordBot.GetInstance()
    bot.load_results()

@client.event
async def on_message(message):
    bot = DiscordBot.GetInstance()
    output = bot.process_message(message)
    if output:
        await  message.channel.send(output)

bot = DiscordBot()
client.run(bot.token_)

#!add_user luke wef
#!bet luke luke
#!bet wef wef
#!winner luke
