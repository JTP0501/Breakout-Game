# Breakout-Game
CS 12 Project

# Stages Configuration File

The `stages.json` file is used to configure the levels in the game. Each stage is defined by a list of bricks and their attributes.

## Format

```json
{
  "stages": [
    {
      "id": <int>,            // Stage ID
      "bricks": [             // List of bricks in the stage
        {
          "x": <float>,       // X position of the brick
          "y": <float>,       // Y position of the brick
          "brick_type": <int> // Type of the brick (1, 2, 3, or 4)
        }
      ]
    }
  ]
}
