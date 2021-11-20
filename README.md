# Discord Bet Bot

This is a simple bot to keep track of bets.  
Users bet on who will win at "the game".  
Users that bet correctly are awarded an equal fraction of the pot.  
The winner of the game will be awarded 2 points.

## Usage
```bash
#USER COMMANDS
$register
$bet [on] [amt]
$withdraw
$balance
$most_dmg [user] [winning squad? (yes/no)]

#ADMIN COMMANDS
$register [user1] ... [userN]
$give [user] [amt]
$give_all [amt]
$withdraw [usr]
$reset_bets
```

## Note
Create a file named ".env" in the same folder as the bot with this content filled in.
```bash
# .env
DISCORD_TOKEN={bot-token}
```
