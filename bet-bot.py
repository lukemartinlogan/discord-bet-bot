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

    def __init__(self, prefix='$'):
        self.token_ = os.getenv('DISCORD_TOKEN')
        self.lock_ = threading.Lock()
        self.is_loaded_ = False
        self.users_ = {}
        self.winning_squad_ = 4
        self.most_dmg_ = 2
        self.prefix_ = prefix

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

    def register(self, user_list):
        for user in user_list:
            if user in self.users_:
                return f"You're already registered.\n"
            self.users_[user] = {
                'balance': 25,
                'bet-on': None,
                'bet-amt': 0,
                'borrow': 0
            }
        if len(user_list) > 1:
            return f"{user_list} are registered"
        else:
            return f"{user_list} is registered"

    def withdraw(self, user):
        self.set_bet(user, None, 0)
        return f"{user} abstains from betting"

    def set_bet(self, better, on, amt = 1):
        if better not in self.users_:
            return
        amt = float(amt)
        if amt > self.users_[better]['balance']:
            return f"Cannot bet more than your balance: {self.users_[better]['balance']}"
        self.users_[better]['bet-on'] = on
        self.users_[better]['bet-amt'] = amt
        if on == 'None':
            self.users_[better]['bet-on'] = None
            self.users_[better]['bet-amt'] = 0
        return f"{better} bets on {on} for {amt}."

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
            profile['balance'] += profile['gain']

        #Reward for winning the game
        if squad_win:
            for profile in self.users_.values():
                profile['gain'] += self.winning_squad_
                profile['balance'] += self.winning_squad_

        #Reward for doing most damage
        self.users_[winner]['gain'] += self.most_dmg_
        self.users_[winner]['balance'] += self.most_dmg_

        # Withdraw all users at round end
        for user in self.users_.keys():
            self.withdraw(user)

        #Print winners and scores
        if net_weight == 0:
            congrats = 'None of you predicted correctly. Losers.\n'
        else:
            congrats = f"Congrats! The following sweaty people guessed correctly: {','.join(correct_betters)}\n"
        scores = ""
        for user,profile in self.users_.items():
            if profile['gain'] >= 0:
                scores += f"{user}: gain={profile['gain']}, balance={profile['balance']} shmeckles\n"
            else:
                scores += f"{user}: loss={-profile['gain']}, balance={profile['balance']} shmeckles\n"
        return congrats + scores

    def get_balance(self, user):
        if user not in self.users_:
            return
        return json.dumps(self.users_[user], indent=4)

    def give(self, user, amt):
        if user not in self.users_:
            return
        amt = float(amt)
        self.users_[user]['balance'] += amt
        return f"balance={self.users_[user]['balance']}, debt={self.users_[user]['borrow']} shmeckles\n"

    def give_all(self, amt):
        for profile in self.users_.values():
            profile['balance'] += float(amt)
        return json.dumps(self.users_, indent=4)

    def process_message(self, message):
        cmds = message.content.split()
        author = f"<@!{message.author.id}>"
        output = None

        self.lock_.acquire()
        #!register
        if f'{self.prefix_}register' == cmds[0]:
            if len(cmds) == 1:
                output = self.register([author])
            else:
                output = self.register(cmds[1:])
            self.store_results()
        #!withdraw
        if f'{self.prefix_}withdraw' == cmds[0]:
            output = self.withdraw(author)
        #!bet [bet-on] [bet-amt]
        if f'{self.prefix_}bet' == cmds[0]:
            if len(cmds[1:]) == 2:
                output = self.set_bet(author, cmds[1], cmds[2])
            elif len(cmds[1:]) == 3:
                output = self.set_bet(cmds[1], cmds[2], cmds[3])
            else:
                output = self.set_bet(author, cmds[1])
            self.store_results()
        #!balance
        if f'{self.prefix_}balance' == cmds[0]:
            if len(cmds) == 1:
                output = self.get_balance(author)
            elif len(cmds) == 2:
                output = self.get_balance(cmds[1])
        #!give_all [amt]
        if f'{self.prefix_}give_all' == cmds[0]:
            output = self.give_all(cmds[1])
            self.store_results()
        #!most_dmg [user] [winning squad? (yes/no)]
        if f'{self.prefix_}most_dmg' == cmds[0]:
            output = self.set_most_dmg(cmds[1], cmds[2])
            self.store_results()
        #!give [user] [amt]
        if f'{self.prefix_}give' == cmds[0]:
            output = self.give(cmds[1], cmds[2])
            self.store_results()
        self.lock_.release()

        return output

client = commands.Bot(command_prefix='$')

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

if (bot.token_):
    client.run(bot.token_)
else:
    print('DISCORD_TOKEN environment variable not found')
