from Instructions import *
from Constants import *
import pygame
import math
import numpy as np


BEST_PATH = [
    (1, 0),
    (1, 1),
    (1, 2),
    (2, 2),
    (3, 2),
    (4, 2),
    (5, 2),
    (5, 1),
    (6, 1),
    (7, 1),
    (8, 1),
    (9, 1),
    (10, 1),
    (11, 1),
    (12, 1),
    (13, 1),
    (14, 1),
    (14, 2),
    (14, 3),
    (13, 3),
    (13, 4),
    (13, 5),
    (13, 6),
    (13, 7),
    (13, 8),
    (13, 9),
    (13, 10),
    (12, 10),
    (11, 10),
    (11, 9),
    (10, 9),
    (9, 9),
    (9, 10),
    (8, 10),
    (7, 10),
    (6, 10),
    (6, 9),
    (5, 9),
    (4, 9),
    (4, 10),
    (3, 10),
    (2, 10),
    (1, 10),
    (1, 11),
]

def norm(v):
    mag = np.linalg.norm(v)

    if mag == 0:
        return v
    
    return v / mag

def dot(vx, vy):
  dot = np.dot(vx, vy)
  
  if dot < 0:
      return math.inf
  return dot


class Controller:
    def __init__(self, app=None):
        self.app = app
        self._path_index = 0
        self.best_path = None
        self.vision = [] # wall, obstacle, item, monster, door

    # passage 4 directions
    def getClosestBrick(self, player, maze, display_surf):
        bricks = self.vision[1]
        if len(bricks) == 0: return # no obstacles

        distances = []
        px, py, w, h  = player.get_rect()
        px = px + w/2
        py = py + h/2

        gx, gy = self.tile_to_pixel_center(
          self.best_path[self._path_index], maze
        )
        vG = (gx - px, gy - py)
        nvG = norm(vG)

        # calculate distance for all bricks
        for i in range(len(bricks)):
            rx, ry, w, h = bricks[i]
            cx = rx + w/2
            cy = ry + h/2
            
            vO = (cx - px, cy - py)
            distances.append((vO, cx, cy))

        # find closest brick
        closestBrick = min(distances, key=lambda item: dot(item[0], nvG))[0]

        # draw lines to each bricks
        for i in range(len(distances)):
          v0, rx, ry = distances[i]
          color = RED if v0 == closestBrick else BLUE
          pygame.draw.line(display_surf, color, (px, py), (rx, ry), 2)

        # draw line to goal
        pygame.draw.line(display_surf, GREEN, (px, py), (gx, gy), 2)


    def get_instruction(self, keys=None, events=None):
        return self.follow_best_path(
            self.app.player,
            self.app.maze,
        )
    
    def tile_to_pixel_center(self, tile, maze):
        # J'ai dit que les tuiles sont en coordonnées [x, y]
        x, y = tile
        return (x + 0.5) * maze.tile_size_x, (y + 0.5) * maze.tile_size_y

    def follow_best_path(self, player, maze, reach_px=None):
        """
        Follow a list of tiles (x, y). Returns an Action or None.
        """

        while self._path_index < len(self.best_path):
            tile_x, tile_y = self.best_path[self._path_index]
            target_x = tile_x * maze.tile_size_x
            target_y = tile_y * maze.tile_size_y
            pR = player.get_rect()
            gR = pygame.Rect(target_x, target_y, maze.tile_size_x, maze.tile_size_y)

            reached = gR.colliderect(pR)
            print(reached, self._path_index)

            x, y, w, h = pR
            dx = target_x - x + w / 2
            dy = target_y - y + h / 2

            if reached:
                self._path_index += 1
                continue
            if abs(dx) > abs(dy):
                return None#Action.RIGHT if dx > 0 else Action.LEFT
            return None#Action.DOWN if dy > 0 else Action.UP
        return None
