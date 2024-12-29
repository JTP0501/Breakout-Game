# CALCIFER'S-COOKOUT
CS 12 Project

# Stages Configuration File

The `stages.json` file is used to configure the stages in the game. Each stage is defined by their stage id (type: int), P (type: int) its "weight" contribution to score, and a list of bricks (type: list[dict[str, int]]).

## Format

```json
{
  "stages": [
    {
      "id": <int>,            // Stage ID
      "P" : <int>,            // Points Contribution
      "bricks": [             // List of bricks in the stage
        {
          "x": <int>,       // X position of the brick
          "y": <int>,       // Y position of the brick
          "brick_type": <int> // Type of the brick (1, 2, 3, or 4)
        }
      ]
    }
  ]
}
