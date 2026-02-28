# ACB Spawn Logic

### Scoring

The game first grants every spawn point a score using the following method:

1. If the spawn is closer than the minimum radius, grant a score of 0.
2. If the spawn is between the minimum radius and the minimum ideal radius, grant a score between 0 and 1, with 0 being at the minimum radius and 1 being at the minimum ideal radius.
3. If the spawn is between the minimum and maximum ideal radii, grant a score of 1.
4. If the spawn is between the maximum ideal radius and the maximum radius, grant a score between 1 and `w`, with 1 being at the maximum ideal radius and `w` being at the maximum radius.
5. If the spawn is further away than the maximum radius, grant a score of `w`.

The game then selects the spawn with the highest score. If multiple spawns have the same score, it grabs the first one with this score.
This leads to certain spawns (e.g. Florence tree or Siena red) being favored heavily.

### Parameters

The scoring method is calculated using the following parameters.

#### Teammate

* Minimum radius: 4
* Minimum ideal radius: 5
* Maximum ideal radius: 15
* Maximum radius: 100
* `w`: 0.2

#### Opponent

* Minimum radius: 30
* Minimum ideal radius: 40
* Maximum ideal radius: 60
* Maximum radius: 90
* `w`: 0.2

#### Objective (e.g. chests)

* Minimum radius: 30
* Minimum ideal radius: 40
* Maximum ideal radius: 60
* Maximum radius: 90
* `w`: 0.5

### Host

The host player's spawn logic is the same, but opponent (and maybe objective) positions are ignored. Death positions (of all players on the team who haven't respawned yet) are used as opponent positions instead.
