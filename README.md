# CALCIFER'S-COOKOUT 🔥

_CS 12 PROJECT_

Welcome to ***"Calcifer's Cookout"***!

Help Calcifer go through all the different stages, and feed him with as many lumps of coal and potions to gain the highest possible score.

## Game Demo 🎮

This README explains how the stages are configurated in the `stages.json` file, and contains a description of some of the features found in this modified breakout game inspired by _Studio Ghibli's "Howl's Moving Castle"_.

# Stages Configuration File ⚙️

The `stages.json` file is used to configure the stages in the game.
### Global Values

- `P` (Points Contribution) 
- `G` (Power-Up Duration)
- `X` (Power-Up Drop Chance)
- `Q` (Streak Increment)

## Format

```json
{
  "P" : <int>,
  "G" : <int>,
  "X" : <int>,
  "Q" : <int>,
  "stages": [
    {
      "bricks": [           
        {
            "x": <int>,                          // x-pos of brick
            "y": <int>,                          // y-pos of brick
            "brick_type": <int>                  // type of brick
        }                                        // 1 - Regular (book) : (1 hit)
      ]                                          // 2 - Sturdy (bacon) : (2 hits)
    }                                            // 3 - Very Sturdy (egg) : (3 hits)
  ]                                              // 4 - Indestructible (stone slab) : (inf hits)
}                                                // 5 - Ball Maker (wood) : (1 hit)
```

# Features

**Streak** ⚡
- Each successive capture of score objects adds to the streak and increases the points by a factor of Q. If a score object falls to the bottom, it resets the streak.

**Power Ups** ⚡
- Aside from score objects, there is an X% chance of powerups spawning _(still has points)_.

  - _Life Up_ : This increases your life by 1.
  - _Antigravity_ : This disables the effect of gravity for G seconds.
  - _Paddle Speed_ : This increases the paddle speed.
  - _Double Points_ : This doubles the weight of the points received _(includes the added points from the streak)_.

### Built With
[`Pyxel`](https://github.com/kitao/pyxel) - A retro game engine for Python.

## Disclaimer ⚠️

This project is a part of a school assignment and is intended for educational purposes only. It is not a professional product and may contain limitations or inaccuracies. Any external content used in this project has been credited accordingly, and no copyright infringement is intended.
