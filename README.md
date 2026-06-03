# Prestige Mod

This mod allows players to gain 'prestige levels' after hitting the servers level cap, which they can then use to gain additional stats. This both gives your players another way to increase their power for harder custom content, and provides incentive for older players to group with newer players in content they outgear.

## How it works
Once players hit your servers level cap, they will continue to get exp from quests and kills. After they've earned enough exp (formula in config), they'll gain a prestige level. Players can access their prestige menu with the chat command ".prestige menu". From here, they can select which stat to increase. Prestige stats can also be set to disabled for pvp.

At the real level cap the stock UI often hides the XP bar even though the server tracks prestige XP.

**Option A — AIO + ALE (recommended if you use Rochet2 AIO)**  
Copy `lua/z_prestige_aio_xp.lua` into your ALE script directory next to `AIO_Server` (same layout as `env/dist/bin/lua_scripts/` on your host: `AIO_Server` plus this file). The `z_` prefix keeps load order **after** `AIO_Server/AIO.lua` so `AIO` is defined. Then set `Prestige.AddonXpIndicator = 0` in config so you do not get **two** updates (C++ whisper + AIO).

**Option B — C++ addon whisper**  
When `Prestige.AddonXpIndicator` is enabled, the module pushes addon whispers (prefix `PrestigeXP`, body `currentXP,nextXP,prestigeLevel`). Install the standalone client addon from `client/PrestigeXPIndicator` under `Interface\AddOns\` if you are not using AIO for this bar.

## Stats Available
**Core Stats:** Stamina, Strength, Agility, Intellect, Spirit

**Secondary Stats:** Attack Power, Spell Power, Crit Rating, Hit Rating, Expertise Rating, Haste Rating, Armor Pen, Spell Pen, Mp5

**Defensive Stats:** Defense Rating, Dodge Rating, Parry Rating, Block Rating, Block Value, Resilience Rating, Bonus Armor

**Resistance Stats:** Resist Fire, Resist Frost, Resist Nature, Resist Shadow, Resist Arcane, Resist All


The maximum points that can be spent in a stat, as well as how much each point is worth, can be set in the config. Stats can also be disabled by setting the max to 0.

## Chat Commands
**.prestige menu** --opens the main prestige menu for assigning and respeccing stats

**.prestige stats** --lists current prestige stats in the chatlog

**.prestige grantlevel** --GM only command to grant a prestige level from the target

**.prestige removelevel** --GM only command to remove a prestige level from the target


## Installation
Clone the repo to your modules folder and make sure the related SQL files run properly.

## Under The Hood
-This mod works by changing the max level on the server: if your server is set to max at level 80, this mod will change that to 81. Players will be bumped back to your intended max level and instead gain a prestige level when they do level up.

-Stats are awarded as new spell auras added to spell_dbc. Due to the limitations of stacks on spell auras, the maximum any stat bonus can grow with this mod is 65,536.

-This mod was inspired by https://github.com/AnchyDev/Attriboost, big thanks to his work on the Attriboost mod!
