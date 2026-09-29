# ACB 2.0 Patch Notes

### 1.7.0
* Abilities now reach other players faster.
* All players' mutes are now visible no matter what, so you can see missed mutes and teammate mutes.
* Fixed a couple minor bugs in the patch.

### 1.6.3

* Made Enhanced Autobash a permanent thing instead of requiring the perk.
* Disabled numerous chasebreakers on Pienza due to a bug where they close on players before they can run through them.
* Fixed a bug that made it [possible to miss a gunshot even if fully aimed](https://www.youtube.com/watch?v=sSOUsRO8ysY).
* Fixed a bug where the host player's spawn used incorrect player positions. No more [host spawning directly on opponents](https://www.youtube.com/watch?v=XGoK3xnuHI8).

We've also done a little redesign of the AN website: https://assassins.network.

### 1.6.2

* Fixed a bug caused by the spawn change on Monteriggioni that caused players to fall through the map.
* On game end, the scoreboard is now logged under a `game_score_logs` folder.

### 1.6.1

* Fixed the Florence invisible chimney bug fix.

### 1.6.0

* Disabled score x2. (Host streak glitch triggers on it as well, plus it's horrible to balance around. Should be back once/if host streak glitch is fixed.)
* Added a `patch.ini` config file to toggle new settings.
* New setting to disable the FPS cap.
* New setting to force highest level of detail.
* New setting to raise civilian and player render distances.
* New setting to enable AC3/4 style controls when using an Xinput controller (Xbox 360 or any emulator, such as `claudia.asi`, `xinput.asi`, x360ce, PadForge, DS4Tool, etc.). RT now triggers RT+A and RT+A triggers RT. No more excuses about not being able to claw, Xanthex.
* Fixed an invisible chimney bug on Florence.
* Fixed the invisible smoke bomb glitch.
* Moved Monteriggioni's spawn trap to the center of the map.
* Fixed automatic camera dampening when using keyboard and mouse input. You can also adjust the dampening in the new settings file.
* Changed map order in private matches to better reflect play order.
* Disabled crowd-bandwidth management. This seems to have no effect on lag, but may later need to be reverted.
* Increased unlock distance. Locking distance is WIP, but at least you won't lose your locks as quickly.
* Wanted: set chases while in line of sight to expire after 15 s (up from 0 s).

### 1.5.1

* Reverted Firecrackers max intensity change.

### 1.5.0

* Diversion: score bonus raised from 75 to 175.
* Morph: rapid reload is now the only kind of morph. RIP super morph (I'm sure it'll be back).
* Firecrackers: lowered max intensity radius to 2.0 for normal and 2.5 for strong. This should make blinding white screens significantly rarer.
* Templar Vision: raised distance to 50 and duration to 3.5 s.

### 1.4.0

* Chest Capture: removed chases, made chests always visible on defense, changed spawn rule to remove spawn kills, and made compass inaccurate.
* Re-enabled Templar Vision with 2.5 s duration and a 50 s cooldown.
* Lowered poison delay from 6.5 s to 3.5 s.
* Raised intercepted bonus from +50 to +150.
* Wanted: contract system is now less leader-focused.
* Raised score x2 required losses from 5 to 6.

### 1.3.0

* Merged sprint boosts into one version with 4.5 s duration, 135% speed boost, 50 s cooldown.
* Raised cooldown on firecrackers by 5 s (now 40/50 s).
* Raised cooldown on rapid reload morph by 5 s (now 20 s).
* Lowered max civilian counts to 150 (San Donato to 100).
* Moved Siena teal spawn further into the corner to make rush killing VIPs more difficult.
* Disable Rome's pillars-spawn trap route.

### 1.2.0

* Moved Siena's green spawn into the corner to force defensible escort routes.
* Enabled target arrows on offense in escort.

### 1.1.4

* Added 10 more ability sets.
* Decreased max civilian count from 500 to 200. San Donato is still 150.
* Adjust camera acceleration depending on input method, with mouse using the original input method.
* Nerfed silent hunt outside of on the ground in manhunt.

### 1.1.3

With this patch, we're doing a small overhaul of available abilities to make ability set customization easier and make future balancing simpler.
Unused or hard to balance items are disabled, and ability variations are changed so that the standard ability is the most popular of the old variations.
In cases where nobody used alternative variations, there's only one version of an ability available.
If there's enough demand or it makes sense for balancing, these items can and will be brought back.

* Disabled templar vision.
* Disabled extra precision.
* Disabled fast getaway.
* Disguise: base is rapid reload, one alternative: long lasting
* Sprint boost: base is fast, two alternatives: long lasting, rapid
* Smoke: base is long lasting, one alternative: strong
* Gun: base is quick firing
* Fc: base is rapid, one alternative: strong
* Morph: base is strong, one alternative: rapid
* Knives: base is long lasting
* Charge: base is now low speed, low range, low range
* Decoy: base is rapid
* Mute: base is long lasting, two alternatives: strong, rapid
* Poison: base is slow acting

Other changes:

* Re-introduced wanted with random targeting, revenge targeting, and target inheritance.

### 1.1.2

No updating necessary for users, these changes are all serverside.

* Lowered power morph range from 20 m to 15 m and strong morph range from 35 m to 25 m.
* Raised firecracker range from 12 m to 15 m, with strong firecracker range being 17.5 m.
* Lowered firecracker duration from 6 s to 5 s, with long lasting being 6 s.
* Lowered chase depletion time from 1.5 s to 1 s when not hidden and 1 s to 0.75 s when hidden in assassinate.
* Immediately deplete detection meter at large distances in assassinate.

### 1.1.1

* Lowered escort's round length to 4:20.
* Removed camera deceleration.
* Lowered camera's deadzone, meaning it starts turning at lower joystick tilts and there are (somehow?) more speeds available.
* Lowered San Donato's maximum civilian count.
* Chases now last 1.5 s in assassinate regardless of line of sight. When hidden, this is lowered to 1.0 s.

### 1.1.0

* In-game camera sensitivity options raised from [0.5, 2.0] to [0.5, 3.5]. This means the old 5/10 is now 2/10 and old 10/10 is now 4/10.
* Removed the animus wall's camera collision on Florence.

### 1.0.0

* Moved all ability re-balancing serverside.
* Enabled hidden for all disguises.
* Removed disguise animation from strong disguise.
* Escort in public lobbies is now limited to 2 vs. 2.
* Assassinate in public lobbies now starts with 4 players.
* Assassinate in private lobbies now starts with 1 player.
* Disabled wanted, advanced wanted, alliance, and advanced alliance.
* Lowered minimum and maximum wait time for ability selection to [1, 12] seconds.
* Raised chest radius.
* Disabled intro session's first tip.
* Raise maximum ping to 1000 ms.
* Removed DLC/Uplay locks on characters.
* Lowered wait until compass shows in intro session.
* Changed escort compass to manhunt compass.
* Raised escort round lengths to 5 min.

### 0.4.1

* Re-enabled gun kill camera.
* Lowered sprint boost speeds: base 130% -> 125%, strong 169% -> 150%.
* Lowered strong sprint boost duration: 5 s -> 3.5 s.
* Lowered power morph cooldown: 60 s -> 50 s.
* Buffed strong morph: civilians 10 -> 100, range 30 m -> 35 m, cooldown 45 s -> 75 s.

### 0.4.0

* Removed zoom-in lock camera. A replacement zoom is being worked on.
* Raised maximum number of civilians and civilian despawn distance.
* Removed the gun sound delay.
* Raised sprint boost speed: base 120% -> 130%, strong 130% -> 169%. Strong and long lasting now theoretically cover the same distance.
* Redesigned morph:

Parameter | Power | Strong | Rapid Reload
--------- | ----- | ------ | ------------
Civilians |  50   |   10   |      2      
Range     |  20 m |   30 m |      2 m    
Cooldown  |  60 s |   45 s |     15 s    

### 0.3.3

* Fixed Siena checkpoint spawn for green start.

### 0.3.2

* Raised silent hunt's depletion factor from `0.30` to `0.44`.
* Removed more camera resets, mostly around climbing.
* Disabled drop kill camera. This is a bit of a WIP.
* Removed camera collision with the animus wall on relevant maps.

### 0.3.1

* Moved Venice haybales spawn further towards the docks and away from Tim spawn.
* Disabled a checkpoint spawn on Siena so green spawn is no longer problematic.
* Moved Rome spawn trap spawns under buildings.
* Applied compression.

### 0.3.0

* Moved Venice haybales spawn onto the other side of the building.
* Moved Venice haybale trap under the building.
* Moved Florence tree spawn under a roof.
* Moved Siena blue trap further towards the bar.

### 0.2.0

* Removed introductory session tips. (No more slowdowns! You can finally speedrun the intro session!)
* Removed some camera resets. (Ejects no longer move the camera.)

### 0.1.2

* Removed leap of faith camera animation.

### 0.1.1

* Removed chase breaker camera animations.

### 0.1.0

* Lowered camera mouse acceleration.
* Removed camera turn around corners.

### 0.0.0

* Re-added multiplayer files.
* Enabled all abilities without challenges.
* Raised silent hunt's depletion factor from `0.15` to `0.30`. (Depletion speed is `1.45 * (1 - factor)`.)
