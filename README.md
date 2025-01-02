# CALCIFER'S-COOKOUT
<b>CS 12 Project

Welcome to "Calcifer's Cookout"! This README explains how the stages are configurated in the `stages.json` file, contains an `installation guide`, and a description of the features found in this modified breakout game inspired by Studio Ghibli's "Howl's Moving Castle".

# Stages Configuration File

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
        }                                        // 1 - Regular (book)
      ]                                          // 2 - Sturdy (bacon)
    }                                            // 3 - Very Sturdy (egg)
  ]                                              // 4 - Indestructible (stone slab)
}                                                // 5 - Ball Maker (wood)
```

### Built With

`Pyxel` - A retro game engine for Python.

<b>Disclaimer:
This project is a part of a school assignment and is intended for educational purposes only. It is not a professional product and may contain limitations or inaccuracies. Any external content used in this project has been credited accordingly, and no copyright infringement is intended.
