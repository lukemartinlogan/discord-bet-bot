import os
import json
import numpy as np
from discord import Embed

class Gamble:
    bot = None

    @staticmethod
    def GetInstance():
        if Gamble.bot is None:
            Gamble.bot = Gamble()
        return Gamble.bot

    def __init__(self):
        self.users_ = {}
        self.winning_squad_ = 4
        self.winner_ = 2
        self.load_results()

    def load_results(self):
        if os.path.exists('bets.json'):
            with open('bets.json', 'r') as fp:
                info = json.load(fp)
            self.users_ = info['users']
            self.winning_squad_ = info['winning_squad']
            self.winner_ = info['winner']
            print(f"self.users_: {self.users_}")
        else:
            print('bets.json does not exist')
        

    def store_results(self):
        info = {
            'users': self.users_,
            'winning_squad': self.winning_squad_,
            'winner': self.winner_
        }
        print(f'writing data: {info}')
        with open('bets.json', 'w') as fp:
            json.dump(info, fp, indent=4)

    def register(self, name):
        if name in self.users_:
            print('already registered')
            return "You're already registered."
        self.users_[name] = {
            'balance': 25,
            'bet-on': None,
            'bet-amt': 0,
            'borrow': 0
        }
        gamble.store_results()
        return f"{name} is registered"

    def bet(self, better, on, amt):
        if better not in self.users_:
            return f'{better} is not registered'
        amt = float(amt)
        if amt > self.users_[better]['balance']:
            return f"Cannot bet more than your balance: {self.users_[better]['balance']}"
        self.users_[better]['bet-on'] = on
        self.users_[better]['bet-amt'] = amt

        return f'{better} bets on {on} for {amt}'

    def withdraw(self, id):
        self.bet(id, None, 0)
        return f"{id} abstains from betting"

    def reset_bets(self):
        for user in self.users_.keys():
            self.withdraw(user)

    def winner(self, winner, squad_win):
        if not self.user_is_registered(winner):
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
        self.users_[winner]['gain'] += self.winner_
        self.users_[winner]['balance'] += self.winner_

        #Withdraw all users at round end
        self.reset_bets()

        #Print winners and scores
        if net_weight == 0:
            congrats = 'None of you predicted correctly. Losers.\n'
        else:
            congrats = f"Congrats! The following sweaty people guessed correctly: {','.join(correct_betters)}\n"
        scores = ""
        for user,profile in self.users_.items():
            if profile['gain'] > 0:
                scores += f"{user}: gain={profile['gain']} 💰, balance={profile['balance']} shmeckles\n"
            elif profile['gain'] == 0: 
                scores += f"{user}: gain={profile['gain']} 0️⃣, balance={profile['balance']} shmeckles\n"
            else:
                scores += f"{user}: loss={-profile['gain']} 🔻, balance={profile['balance']} shmeckles\n"
        return congrats + scores

    def balance(self, id):
        if not self.user_is_registered(id):
            return f'{id} is not in the user list'
        embed = self.balance_embed(id, self.users_[id])
        return embed

    def give(self, user, amt):
        if not self.user_is_registered(user):
            return f'{user} is not a valid user'
        amt = float(amt)
        self.users_[user]['balance'] += amt
        return f"balance={self.users_[user]['balance']} shmeckles"

    def give_all(self, amt):
        for profile in self.users_.values():
            profile['balance'] += float(amt)
        return json.dumps(self.users_, indent=4)

    def leaderboard(self):
        return self.leaderboard_embed(self.users_)

    def user_is_registered(self, id):
        if id not in self.users_:
            return False
        else:
            return True

    # TODO: maybe it is better convention to move these embed builders to embeds.py ?
    def balance_embed(self, user, balance_dict):
        embed = Embed(title=user)
        embed.add_field(name='Balance', value=balance_dict['balance'], inline=True)
        embed.add_field(name='Bet on', value=balance_dict['bet-on'], inline=True)
        embed.add_field(name='Borrow', value=balance_dict['borrow'], inline=True)
        embed.add_field(name='Gain', value=balance_dict['borrow'], inline=True)
        return embed

    def leaderboard_embed(self, users):
        sorted_balances = sorted(users.items(), key=lambda user: user[1]['balance'], reverse=True)
        embed = Embed(title="Leaderboard")

        rank = 0
        user_rankings = ""
        balances = ""

        for tup in sorted_balances:
            rank += 1
            user_rankings += f'`{rank}` ' + tup[0] + '\n'
            balance = tup[1]['balance']
            balances += f'`{balance}`\n'

        embed.add_field(name='Rank', value=user_rankings, inline=True)
        embed.add_field(name='Shmeckles', value=balances, inline=True)
        return embed        
