# Validation test

Goal: Test the integrations of the different modules together, and validate that the agent behaves as expected in different mazes.
Known issues: the fuzzy logic doesn't work for obstacle avoidance, the player can sometimes get stuck because of that.

## mazeSmall_0:
  - find A* path: ✓
  - Fuzzy logic follows goal: ✓
  - Fuzzy logic avoids walls: ✓
  - Complete Maze: ✓

## mazeSmall_1:
  - find A* path: ✓
  - Fuzzy logic follows goal: ✓
  - Fuzzy logic avoids walls: ✓
  - Fuzzy logic avoids obstacles: X
  - Complete Maze: X

## mazeSmall_2:
  - find A* path: ✓
  - Fuzzy logic follows goal: ✓
  - Fuzzy logic avoids walls: ✓
  - Fuzzy logic avoids obstacles: X
  - Kills all monsters: ✓
  - Opens all doors: ✓
  - Complete Maze: X (depends on obstacle positions)

## mazeLarge_2:
  - find A* path: ✓
  - Fuzzy logic follows goal: ✓
  - Fuzzy logic avoids walls: ✓
  - Fuzzy logic avoids obstacles: X
  - Kills all monsters: ✓
  - Opens all doors: ✓
  - Complete Maze: X