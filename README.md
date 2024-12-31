# CALCIFER'S-COOKOUT
CS 12 Project

# Stages Configuration File

The `stages.json` file is used to configure the stages in the game. Each stage is defined by their P (type: int) its "weight" contribution to score, and a list of bricks (type: list[dict[str, int]]).

## Format

```json
{
  "P" : <int>,              // Points Contribution 
  "stages": [
    {
      "bricks": [           // List of bricks in the stage
        {
          "x": <int>,       // X position of the brick
          "y": <int>,       // Y position of the brick
          "brick_type": <int> // Type of the brick (1, 2, 3, or 4)
        }
      ]
    }
  ]
}
