# bot.py
import os
import json
import threading
import numpy as np
import discord
from discord.ext import commands
#from dotenv import load_dotenv

#load_dotenv()
client = commands.Bot(command_prefix='!')

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, self_bot):
        super().__init__(command_prefix=command_prefix, self_bot=self_bot)
        self.token_ = os.getenv('DISCORD_TOKEN')
        self.message_lock_ = threading.Lock()
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
        if self.is_loaded_:
            return
        if not os.path.exists('bets.json'):
            return
        with open('bets.json', 'r') as fp:
            info = json.load(fp)
        self.users_ = info['users']
        self.winning_squad_ = info['winning_squad']
        self.most_dmg_ = info['most_dmg']
        self.is_loaded_ = True
        print(f"self.users_: {self.users_}")

    def add_users(self, user_list):
        for user in user_list:
            self.users_[user] = {
                'earnings': 0,
                'cur-bet': None,
                'bet-amt': 0
            }

    def set_bet(self, better, on, amt = 1):
        self.users_[better]['cur-bet'] = on
        self.users_[better]['bet-amt'] = float(amt)
        if on == 'None':
            self.users_[better]['cur-bet'] = None
            self.users_[better]['bet-amt'] = 0

    def set_most_dmg(self, winner, squad_win):
        squad_win = bool(squad_win)
        if winner not in self.users_:
            return f'{winner} is not in the user list'

        pot = sum([profile['bet-amt'] for profile in self.users_.values()])
        correct_bets = [user for user,profile in self.users_.items() if profile['cur-bet'] == winner]
        weights = np.array([self.users_[user]['bet-amt'] for user in correct_bets])
        weights = weights / np.sum(weights)

        #Reward for guessing correctly
        print(weights)
        for user,weight in zip(correct_bets, weights):
            self.users_[user]['earnings'] += pot * weight

        #Reward for winning the game
        print(squad_win)
        if squad_win:
            for profile in self.users_.values():
                profile['earnings'] += self.winning_squad_

        #Reward for doing most damage
        self.users_[winner]['earnings'] += self.most_dmg_

        #Store the results
        store_results()

        #Print winners and scores
        if len(correct_bets) == 0:
            congrats = 'None of you predicted correctly. Losers.\n'
        else:
            congrats = f"Congrats! The following sweaty people guessed correctly: {','.join(correct_bets)}\n"
        scores = ""
        for user,profile in self.users_.items():
            scores += f"{user}: {profile['earnings']} shmeckles\n"
        return congrats + scores

    async def on_ready(self):
        print(f'{client.user} has connected to Discord!')
        self.load_results()

    @commands.command(name="on_message", pass_context=True)
    def add_users(self):
        return

    async def on_message(self, message):
        print("ctx")
        msg = None
        cmds = message.content.split()
        self.message_lock_.acquire()
        #!add_users [user1] ... [userN]
        if '!add_users' == cmds[0]:
            self.add_users(cmds[1:])
        #!bet [better] [betting-on] [amount]
        if '!bet' == cmds[0]:
            if len(cmds) < 4:
                self.set_bet(cmds[1], cmds[2], cmds[3])
            else:
                self.set_bet(cmds[1], cmds[2])
        #!self.most_dmg_ [user] [squad_win? (True/False)]
        if '!self.most_dmg_' == cmds[0]:
            msg = self.set_most_dmg(cmds[1], cmds[2])
        self.message_lock_.release()
        #Send message to user
        if msg:
            await message.channel.send(msg)



bot = DiscordBot(command_prefix="!", self_bot=False)
bot.run(bot.token_)

#!add_user luke wef
#!bet luke luke
#!bet wef wef
#!winner luke
