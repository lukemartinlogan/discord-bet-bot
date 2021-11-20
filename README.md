# Discord Bet Bot

This is a simple bot to keep track of bets.  
Users bet on who will win at "the game".  
Users that bet correctly are awarded an equal fraction of the pot.  
The winner of the game will be awarded 2 points.

## Usage
```bash
!add_users [user1] ... [userN]
!bet [better] [on]
!most_dmg [user] [winning squad? (yes/no)]
!balance [user]
!borrow [user] [amt]
!pay_credit [user] [amt]
!give [user] [amt]
!give_all [amt]
```

## Note
Create a file named ".env" in the same folder as the bot with this content filled in.
```bash
# .env
DISCORD_TOKEN={bot-token}
```
