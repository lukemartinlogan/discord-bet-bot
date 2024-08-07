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
        self.is_loaded_ = False
        self.users_ = {}
        self.winning_squad_ = 4
        self.winner_ = 2
        self.load_results()

    def make_id(self, id):
        id = str(id)
        return ''.join([c for c in id if c.isdigit()])

    def make_ref(self, id):
        return f'<@!{id}>'

    def load_results(self):
        if not os.path.exists('bets.json'):
            return
        with open('bets.json', 'r') as fp:
            info = json.load(fp)
        self.users_ = info['users']
        for user in self.users_:
            self.users_[user]['ref'] = self.make_ref(user)
        self.winning_squad_ = info['winning_squad']
        self.winner_ = info['winner']
        print(f"self.users_: {self.users_}")

    def store_results(self):
        info = {
            'users': self.users_,
            'winning_squad': self.winning_squad_,
            'winner': self.winner_
        }
        with open('bets.json', 'w') as fp:
            json.dump(info, fp, indent=4)

    def register(self, id):
        id = self.make_id(id)
        if self.user_is_registered(id):
            return "You're already registered."
        self.users_[id] = {
            'balance': 25,
            'bet-on': None,
            'bet-amt': 0,
            'borrow': 0,
            'ref': self.make_ref(id)
        }
        self.store_results()
        return f"{id} is registered"

    def bet(self, better, on, amt):
        better = self.make_id(better)
        on = self.make_id(on)
        if not self.user_is_registered(better):
            return f'{better} is not registered'
        amt = float(amt)
        if amt > self.users_[better]['balance']:
            return f"Cannot bet more than your balance: {self.users_[better]['balance']}"
        self.users_[better]['bet-on'] = on
        self.users_[better]['bet-amt'] = amt

        return f'{self.users_[better]["ref"]} bets on {self.users_[on]["ref"]} for {amt}'

    def withdraw(self, id):
        id = self.make_id(id)
        self.bet(id, None, 0)
        return f"{id} abstains from betting"

    def reset_bets(self):
        for user in self.users_.keys():
            self.withdraw(user)

    def crash_market(self):
        for profile in self.users_.values():
            profile['balance'] = 0

    def winner(self, winner, squad_win):
        winner = self.make_id(winner)
        squad_win = True if squad_win == 'yes' else False
        if not self.user_is_registered(winner):
            return f'{winner} ({self.make_ref(winner)}) is not in the user list'

        pot = sum([profile['bet-amt'] for profile in self.users_.values()])
        correct_betters = [profile['ref'] for user, profile in self.users_.items()
                           if profile['bet-on'] == winner]
        correct_bets = np.array([(profile['bet-on'] == winner)
                                 for profile in self.users_.values()])
        weights = np.array([profile['bet-amt'] for profile in self.users_.values()])
        weights = weights*correct_bets
        net_weight = np.sum(weights)
        if net_weight:
            weights /= net_weight
        print(weights)

        #Reward for guessing correctly
        for profile, weight in zip(self.users_.values(), weights):
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
            congrats = f'Congrats! The following sweaty people guessed correctly: {",".join(correct_betters)}\n'
        scores = ""
        for user, profile in self.users_.items():
            if profile['gain'] >= 0:
                scores += f'{profile["ref"]}: gain={profile["gain"]}, balance={profile["balance"]} shmeckles\n'
            else:
                scores += f'{profile["ref"]}: loss={-profile["gain"]}, balance={profile["balance"]} shmeckles\n'
        return congrats + scores

    def balance(self, id):
        id = self.make_id(id)
        if not self.user_is_registered(id):
            return f'{id} ({self.make_ref(id)}) is not in the user list'
        embed = self.balance_embed(id, self.users_[id])
        return embed

    def give(self, id, amt):
        id = self.make_id(id)
        if not self.user_is_registered(id):
            return f'{id} ({self.make_ref(id)}) is not a valid user'
        amt = float(amt)
        self.users_[id]['balance'] += amt
        return f"balance={self.users_[id]['balance']} shmeckles"

    def give_all(self, amt):
        for profile in self.users_.values():
            profile['balance'] += float(amt)
        return json.dumps(self.users_, indent=4)

    def user_is_registered(self, id):
        id = self.make_id(id)
        if id not in self.users_:
            return False
        else:
            return True

    def balance_embed(self, user, balance_dict):
        user = self.make_id(user)
        embed = Embed(title=f"{user}'s balance")
        embed.add_field(name='Balance', value=balance_dict['balance'], inline=True)
        embed.add_field(name='Bet on', value=balance_dict['bet-on'], inline=True)
        embed.add_field(name='Borrow', value=balance_dict['borrow'], inline=True)
        embed.add_field(name='Gain', value=balance_dict['borrow'], inline=True)
        return embed

    def leaderboard_embed(self, users):
        sorted_balances = sorted(users.items(), key=lambda user: user[1]['balance'], reverse=True)
        embed = Embed(title="Leaderboard")

        rank = 0
        user_rankings = []
        balances = []
        for tup in sorted_balances:
            rank += 1
            name_ref = self.make_ref(tup[0])
            balance = tup[1]['balance']
            user_rankings.append(f'`{rank}` {name_ref}')
            balances.append(str(balance))

        user_rankings = '\n'.join(user_rankings)
        balances = '\n'.join(balances)
        embed.add_field(name='Rank', value=user_rankings, inline=True)
        embed.add_field(name='Shmeckles', value=balances, inline=True)
        return embed

    def leaderboard(self):
        return self.leaderboard_embed(self.users_)
