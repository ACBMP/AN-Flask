# ACB 2.0 Patch Summary

The ACB 2.0 patch aims to bring long awaited quality of life improvements to the game, optimize it for competitive play, and fix bugs along the way.
While constant improvements are made, the patch also routinely re-balances the game via ability balancing and map changes.
Although escort is the main mode of focus, the patch also tries to optimize competitive manhunt and assassinate.
Finally, while lower priority, efforts are made to modernize the visuals of the game.

## Camera

* Removed (almost) all cases where the camera moves itself or becomes unmoveable.
* Removed all kill cameras aside from the gun kill camera.
* Raised camera sensitivities. Old 5/10 is now 2/10 and old 10/10 is now 4/10.
* Removed lock camera zoom. A replace that doesn't move the camera is being worked on.
* Removed camera collision with animus wall where possible.
* Lowered camera acceleration.
* Removed camera deceleration on controller.

## Spawns

* Moved the following spawns so players can't be shot on spawn: Siena blue trap, Venice haybale trap, Rome trap, Florence tree.
* Moved the Venice haybale initial spawn further towards the docks.

## Abilities

* Replaced base abilities with their most popular variant and disabled unpopular variants.
* Removed templar vision.
* Removed gun sound delay.
* Morph:

Parameter | Base | Rapid Reload
--------- | ------ | ------------
Civilians |   100   |      2      
Range     |   25 m |      2 m    
Cooldown  |   75 s |     15 s    

* Sprint boost: 

Parameter | Long Lasting | Base (Strong) | Rapid Reload
--------- | ----- | ------ | ------------
Speed boost |  125%   |   150%   |      125%      
Duration     |  7.5 s |   3.5 s |      5 s    
Cooldown  |  60 s |   60 s |     50 s    

* Raised firecracker range from 12 m to 15 m, with strong firecracker range being 17.5 m.
* Lowered firecracker duration from 6 s to 5 s.
* Charge is now short and controllable.

## Perks

* Fixed silent hunt.
* Removed fast getaway.

## Streaks

* Removed extra precision.

## Modes

* Chest radius increased and capture time increased.
* Changed escort compass to manhunt.
* Escort in public lobbies is now limited to 2 vs. 2.
* Escort rounds are now 4:20 long.
* Assassinate in public lobbies now starts with 4 players, private lobbies 1.
* Escapes take 1 s (not hidden) or 0.75 s (hidden) in assassinate.
* Escapes trigger regardless of vision status in assassinate.
* Immediately deplete detection meter at large distances in assassinate.
* Wanted now assigns random targets instead of rank-based targets.

## Misc.

* Raised maximum number of civilians and civilian despawn distance.
* Removed introductory session tips. (No more slowdowns! You can finally speedrun the intro session!)
* Enabled all abilities without challenges.
* Ability set selection time changed to [1, 12] s. 
* Increased number of ability sets to 15.
* Maximum ping is now 1000 ms.
