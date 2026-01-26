from Instructions import *
from Constants import *
import pygame
import math
import numpy as np
from skfuzzy import control as ctrl
import skfuzzy as fuzz
import matplotlib.pyplot as plt
import Instructions

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
        self._path_index = 1
        self.best_path = None
        self.vision = [] # wall, obstacle, item, monster, door
        self.perception_distance = PERCEPTION_RADIUS * max(self.app.maze.tile_size_x, self.app.maze.tile_size_y)
        self.fuzzy_ctrl = self.setup_fuzzy_logic(self.app.maze)

        print('------------------------ RULES ------------------------')
        for rule in self.fuzzy_ctrl.ctrl.rules:
            print(rule)
        print('-------------------------------------------------------')

        # Display fuzzy variables
        for var in self.fuzzy_ctrl.ctrl.fuzzy_variables:
            var.view()
        plt.show()

    def drawClosestBricks(self, player, maze, display_surf):
        bricks = self.vision[1]

        distances = []
        px, py, w, h  = player.get_rect()
        px = px + w/2
        py = py + h/2

        gx, gy = self.tile_to_pixel_center(
          self.best_path[self._path_index], maze
        )
        vG = (gx - px, gy - py)
        nvG = norm(vG)
        # draw line to goal
        pygame.draw.line(display_surf, GREEN, (px, py), (gx, gy), 2)

        if len(bricks) == 0: return # no obstacles
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

    def getClosestBrickAndGoal(self, player, maze):
        bricks = self.vision[1]

        distances = []
        px, py, w, h  = player.get_rect()
        px = px + w/2
        py = py + h/2

        gx, gy = self.tile_to_pixel_center(
          self.best_path[self._path_index], maze
        )
        print("Goal pos: ", gx, gy)
        print("Player pos: ", px, py)
        if len(bricks) == 0: return (math.inf, math.inf), (gx - px, gy - py)

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
          if v0 == closestBrick:
              return (rx - px, ry - py), (gx - px, gy - py)
          else:
              continue
          
        return (math.inf, math.inf), (gx - px, gy - py)
    
    def getWallsDistance(self, player, maze):
        walls = self.vision[0]


        up_dist = math.inf
        down_dist = math.inf
        left_dist = math.inf
        right_dist = math.inf
        if len(walls) == 0: return up_dist, down_dist, left_dist, right_dist

        px, py, w, h  = player.get_rect()
        px = px + w/2
        py = py + h/2

        for i in range(len(walls)):
            rx, ry, w, h = walls[i]
            cx = rx + w/2
            cy = ry + h/2
            
            vO = (cx - px, cy - py)

            if abs(vO[0]) < w/2: # same column
                if vO[1] > 0: # wall is down
                    down_dist = min(down_dist, abs(vO[1]) - h/2)
                else: # wall is up
                    up_dist = min(up_dist, abs(vO[1]) - h/2)
            if abs(vO[1]) < h/2: # same line
                if vO[0] > 0: # wall is right
                    right_dist = min(right_dist, abs(vO[0]) - w/2)
                else: # wall is left
                    left_dist = min(left_dist, abs(vO[0]) - w/2)

        return up_dist, down_dist, left_dist, right_dist

    def get_instruction(self, keys=None, events=None):
        self.update_best_path(self.app.player, self.app.maze)
        u, d, l ,r = self.getWallsDistance(self.app.player, self.app.maze)
        (bdx, bdy), (gdx, gdy) = self.getClosestBrickAndGoal(self.app.player, self.app.maze)
        if self.best_path is not None:
          return self.call_fuzzy_logic(u, d, l, r, bdx, bdy, gdx, gdy)
        else:
          return None
        # Call logique floue

    
    def setup_fuzzy_logic(self, maze):

        goalDx = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'goalDx')
        goalDy = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'goalDy')

        obsDx = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'obsDx')
        obsDy = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'obsDy')

        wallDx = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'wallDx')
        wallDy = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'wallDy')

        moveDirection = ctrl.Consequent(np.linspace(0, 360, 361), 'moveDirection', defuzzify_method='mom')
        moveDirection['up'] = fuzz.trimf(moveDirection.universe, [0, 45, 90])
        moveDirection['right'] = fuzz.trimf(moveDirection.universe, [90, 135, 180])
        moveDirection['down'] = fuzz.trimf(moveDirection.universe, [180, 225, 270])
        moveDirection['left'] = fuzz.trimf(moveDirection.universe, [270, 315, 360])

        goalDx['left'] = fuzz.trimf(goalDx.universe, [-self.perception_distance, -self.perception_distance, self.perception_distance/4])
        goalDx['center'] = fuzz.trimf(goalDx.universe, [-self.perception_distance/8, 0, self.perception_distance/8])
        goalDx['right'] = fuzz.trimf(goalDx.universe, [-self.perception_distance/4, self.perception_distance, self.perception_distance])

        goalDy['up'] = fuzz.trimf(goalDy.universe, [-self.perception_distance, -self.perception_distance, self.perception_distance/4])
        goalDy['center'] = fuzz.trimf(goalDy.universe, [-self.perception_distance/8, 0, self.perception_distance/8])
        goalDy['down'] = fuzz.trimf(goalDy.universe, [-self.perception_distance/4, self.perception_distance, self.perception_distance])

        wallDy['up'] = fuzz.trimf(wallDy.universe, [-5, 0, 1])
        wallDy['down'] = fuzz.trimf(wallDy.universe, [-1, 0, 5])
        wallDx['left'] = fuzz.trimf(wallDx.universe, [-5, 0, 1])
        wallDx['right'] = fuzz.trimf(wallDx.universe, [-1, 0, 5])

        obsDx['left'] = fuzz.trapmf(obsDx.universe, [-20, -10, 0, 0])
        obsDx['right'] = fuzz.trapmf(obsDx.universe, [0, 0, 10, 20])

        obsDy['up'] = fuzz.trapmf(obsDy.universe, [-20, -10, 0, 0])
        obsDy['down'] = fuzz.trapmf(obsDy.universe, [0, 0, 10, 20])

        rules = []
        
        # Vibe coded (prompt: Do all 36 permutations, make no mistakes)
        # goalDx['left'] & goalDy['up'] with all obstacle combinations (6 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['up'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['right']))  # avoid obstacle: go opposite
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['up'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['up']))  # avoid left obs, go up
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['up'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['left']))  # avoid up obs, go left
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['up'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['left']))  # default: go to goal (left+up = left)
        
        # goalDx['left'] & goalDy['center'] with all obstacle combinations (4 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['center'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['down']))  # avoid left, prefer down
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['center'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['up']))  # avoid left, prefer up
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['center'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['left']))  # no conflict, go left
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['center'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['left']))  # no conflict, go left
        
        # goalDx['left'] & goalDy['down'] with all obstacle combinations (6 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['down'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['down']))  # avoid left obs, go down
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['down'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['right']))  # avoid obstacle: go opposite
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['down'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['left']))  # no conflict, go left
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['down'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['left']))  # avoid down obs, go left
        
        # goalDx['center'] & goalDy['up'] with all obstacle combinations (4 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['up'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['right']))  # avoid up, go right
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['up'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['up']))  # no conflict, go up
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['up'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['left']))  # avoid up, go left
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['up'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['up']))  # no conflict, go up
        
        # goalDx['center'] & goalDy['center'] with all obstacle combinations (4 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['center'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['right']))  # avoid left+up, go opposite
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['center'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['right']))  # avoid left, go right
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['center'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['down']))  # avoid right+up, go down
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['center'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['up']))  # default: prefer up
        
        # goalDx['center'] & goalDy['down'] with all obstacle combinations (4 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['down'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['down']))  # no conflict, go down
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['down'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['right']))  # avoid down, go right
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['down'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['down']))  # no conflict, go down
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['down'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['left']))  # avoid down, go left
        
        # goalDx['right'] & goalDy['up'] with all obstacle combinations (6 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['up'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['right']))  # avoid up obs, go right
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['up'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['right']))  # default: go to goal (right+up = right)
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['up'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['left']))  # avoid obstacle: go opposite
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['up'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['up']))  # avoid right obs, go up
        
        # goalDx['right'] & goalDy['center'] with all obstacle combinations (4 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['center'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['right']))  # no conflict, go right
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['center'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['right']))  # no conflict, go right
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['center'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['down']))  # avoid right, prefer down
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['center'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['up']))  # avoid right, prefer up
        
        # goalDx['right'] & goalDy['down'] with all obstacle combinations (6 rules)
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['down'] & obsDx['left'] & obsDy['up'], consequent=moveDirection['right']))  # no conflict, go right
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['down'] & obsDx['left'] & obsDy['down'], consequent=moveDirection['right']))  # avoid down obs, go right
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['down'] & obsDx['right'] & obsDy['up'], consequent=moveDirection['down']))  # avoid right obs, go down
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['down'] & obsDx['right'] & obsDy['down'], consequent=moveDirection['left']))  # avoid obstacle: go opposite

        # Wall avoidance rules
        rules.append(ctrl.Rule(antecedent=wallDy['up'], consequent=moveDirection['down']))
        rules.append(ctrl.Rule(antecedent=wallDy['down'], consequent=moveDirection['up']))
        rules.append(ctrl.Rule(antecedent=wallDx['left'], consequent=moveDirection['right']))
        rules.append(ctrl.Rule(antecedent=wallDx['right'], consequent=moveDirection['left']))

        # Goal-only fallback rules (when obstacles are far, ignore them)
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['up'], consequent=moveDirection['left']))
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['center'], consequent=moveDirection['left']))
        rules.append(ctrl.Rule(antecedent=goalDx['left'] & goalDy['down'], consequent=moveDirection['left']))
        
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['up'], consequent=moveDirection['up']))
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['center'], consequent=moveDirection['up']))  # default up when centered
        rules.append(ctrl.Rule(antecedent=goalDx['center'] & goalDy['down'], consequent=moveDirection['down']))
        
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['up'], consequent=moveDirection['right']))
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['center'], consequent=moveDirection['right']))
        rules.append(ctrl.Rule(antecedent=goalDx['right'] & goalDy['down'], consequent=moveDirection['right']))

        for r in rules:
            r.and_func = np.fmin
            r.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        sim = ctrl.ControlSystemSimulation(system) 
        return sim



    def call_fuzzy_logic(self, u, d, l, r, bdx, bdy, gdx, gdy):
        wall_dx = -l if np.abs(l) <= np.abs(r) else r
        wall_dy = -u if np.abs(u) <= np.abs(d) else d

        cgdx = np.clip(gdx, -self.perception_distance, self.perception_distance)
        cgdy = np.clip(gdy, -self.perception_distance, self.perception_distance)
        cbdx = np.clip(bdx, -self.perception_distance, self.perception_distance)
        cbdy = np.clip(bdy, -self.perception_distance, self.perception_distance)
        wdx = np.clip(wall_dx, -self.perception_distance, self.perception_distance)
        wdy = np.clip(wall_dy, -self.perception_distance, self.perception_distance)

        self.fuzzy_ctrl.input['wallDx'] = wdx
        self.fuzzy_ctrl.input['wallDy'] = wdy
        self.fuzzy_ctrl.input['goalDx'] = cgdx
        self.fuzzy_ctrl.input['goalDy'] = cgdy
        self.fuzzy_ctrl.input['obsDx'] = cbdx
        self.fuzzy_ctrl.input['obsDy'] = cbdy

        self.fuzzy_ctrl.compute()
        move_direction = self.fuzzy_ctrl.output['moveDirection']
        instruction = None
        if move_direction >= 0 and move_direction < 90:
            instruction = Action.UP
        elif move_direction >= 90 and move_direction < 180:
            instruction = Action.RIGHT
        elif move_direction >= 180 and move_direction < 270:
            instruction = Action.DOWN
        else:
            instruction = Action.LEFT
        print("Instruction: ", instruction, cgdx, cgdy, cbdx, cbdy, move_direction)
        return instruction
    
    def tile_to_pixel_center(self, tile, maze):
        # J'ai dit que les tuiles sont en coordonnées [x, y]
        x, y = tile
        return (x + 0.5) * maze.tile_size_x, (y + 0.5) * maze.tile_size_y

    def update_best_path(self, player, maze):
        """
        Follow a list of tiles (x, y). Returns an Action or None.
        """

        while self._path_index < len(self.best_path):
            tile_x, tile_y = self.best_path[self._path_index]
            target_x = tile_x * maze.tile_size_x
            target_y = tile_y * maze.tile_size_y
            pR = player.get_rect()
            gR = pygame.Rect(target_x, target_y, maze.tile_size_x, maze.tile_size_y)

            reached = gR.contains(pR) # colliderect

            if reached:
                self._path_index += 1
                return
            return

