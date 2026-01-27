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
        self.fuzzy_ctrl = self.setup_fuzzy_logic(self.app.maze, self.app.player)

        # print('------------------------ RULES ------------------------')
        # for rule in self.fuzzy_ctrl.ctrl.rules:
        #     print(rule)
        # print('-------------------------------------------------------')

        # # Display fuzzy variables
        # for var in self.fuzzy_ctrl.ctrl.fuzzy_variables:
        #     var.view()
        # plt.show()

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

        px, py, pw, ph = player.get_rect()
        px = px + pw/2
        py = py + ph/2

        for i in range(len(walls)):
            rx, ry, ww, wh = walls[i]
            cx = rx + ww/2
            cy = ry + wh/2
            
            vO = (cx - px, cy - py)

            # Check if player hitbox overlaps with wall horizontally (for vertical movement)
            if abs(vO[0]) < (ww + pw)/2: # hitboxes overlap horizontally
                if vO[1] > 0: # wall is down
                    # Distance from player bottom edge to wall top edge
                    down_dist = min(down_dist, abs(vO[1]) - wh/2 - ph/2)
                else: # wall is up
                    # Distance from player top edge to wall bottom edge
                    up_dist = min(up_dist, abs(vO[1]) - wh/2 - ph/2)
            
            # Check if player hitbox overlaps with wall vertically (for horizontal movement)
            if abs(vO[1]) < (wh + ph)/2: # hitboxes overlap vertically
                if vO[0] > 0: # wall is right
                    # Distance from player right edge to wall left edge
                    right_dist = min(right_dist, abs(vO[0]) - ww/2 - pw/2)
                else: # wall is left
                    # Distance from player left edge to wall right edge
                    left_dist = min(left_dist, abs(vO[0]) - ww/2 - pw/2)

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

    
    def setup_fuzzy_logic(self, maze, player):
        
        size_x = 0.9 * PLAYER_SIZE * maze.tile_size_x
        size_y = PLAYER_SIZE * maze.tile_size_x

        goalDx = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'goalDx')
        goalDy = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'goalDy')

        obsDx = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'obsDx')
        obsDy = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'obsDy')

        wallDx = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'wallDx')
        wallDy = ctrl.Antecedent(np.arange(-self.perception_distance, self.perception_distance + 1, 1), 'wallDy')

        # Separate X and Y movement outputs
        moveX = ctrl.Consequent(np.arange(-1, 1.1, 0.1), 'moveX', defuzzify_method='centroid')
        moveX['left'] = fuzz.trimf(moveX.universe, [-1, -1, -0.2])
        moveX['neutral'] = fuzz.trimf(moveX.universe, [-0.2, 0, 0.2])
        moveX['right'] = fuzz.trimf(moveX.universe, [0.2, 1, 1])

        moveY = ctrl.Consequent(np.arange(-1, 1.1, 0.1), 'moveY', defuzzify_method='centroid')
        moveY['up'] = fuzz.trimf(moveY.universe, [-1, -1, -0.2])
        moveY['neutral'] = fuzz.trimf(moveY.universe, [-0.2, 0, 0.2])
        moveY['down'] = fuzz.trimf(moveY.universe, [0.2, 1, 1])

        goalDx['left'] = fuzz.trimf(goalDx.universe, [-self.perception_distance, -self.perception_distance, self.perception_distance/4])
        goalDx['center'] = fuzz.trimf(goalDx.universe, [-self.perception_distance/4, 0, self.perception_distance/4])
        goalDx['right'] = fuzz.trimf(goalDx.universe, [-self.perception_distance/4, self.perception_distance, self.perception_distance])

        goalDy['up'] = fuzz.trimf(goalDy.universe, [-self.perception_distance, -self.perception_distance, self.perception_distance/4])
        goalDy['center'] = fuzz.trimf(goalDy.universe, [-self.perception_distance/4, 0, self.perception_distance/4])
        goalDy['down'] = fuzz.trimf(goalDy.universe, [-self.perception_distance/4, self.perception_distance, self.perception_distance])

        wallDy['up'] = fuzz.trapmf(wallDy.universe, [-size_y, -size_y/2, 0, 1])
        wallDy['down'] = fuzz.trapmf(wallDy.universe, [-1, 0, size_y/2, size_y])
        wallDx['left'] = fuzz.trapmf(wallDx.universe, [-size_x, -size_x/2, 0, 1])
        wallDx['right'] = fuzz.trapmf(wallDx.universe, [-1, 0, size_x/2, size_x])

        obsDx['left'] = fuzz.trapmf(obsDx.universe, [-size_x, -size_x/2, 0, 1])
        obsDx['center'] = fuzz.trapmf(obsDx.universe, [-size_x/4, 0, 1, size_x/4])
        obsDx['right'] = fuzz.trapmf(obsDx.universe, [-1, 0, size_x/2, size_x])

        obsDy['up'] = fuzz.trapmf(obsDy.universe, [-size_y, -size_y/2, -1, 1])
        obsDy['center'] = fuzz.trapmf(obsDy.universe, [-size_y/4, -1, 1, size_y/4])
        obsDy['down'] = fuzz.trapmf(obsDy.universe, [-1, 0, size_y/2, size_y])

        rules = []
        # Goal-based rules
        rules.append(ctrl.Rule(antecedent=goalDx['left'], consequent=moveX['left']))
        rules.append(ctrl.Rule(antecedent=goalDx['right'], consequent=moveX['right']))
        rules.append(ctrl.Rule(antecedent=goalDx['center'], consequent=moveX['neutral']))
        
        rules.append(ctrl.Rule(antecedent=goalDy['up'], consequent=moveY['up']))
        rules.append(ctrl.Rule(antecedent=goalDy['down'], consequent=moveY['down']))
        rules.append(ctrl.Rule(antecedent=goalDy['center'], consequent=moveY['neutral']))
        
        # Wall avoidance rules (higher priority by being more specific)
        rules.append(ctrl.Rule(antecedent=wallDy['up'], consequent=moveY['down']))
        rules.append(ctrl.Rule(antecedent=wallDy['down'], consequent=moveY['up']))
        rules.append(ctrl.Rule(antecedent=wallDx['left'], consequent=moveX['right']))
        rules.append(ctrl.Rule(antecedent=wallDx['right'], consequent=moveX['left']))

        # Obstacle avoidance rules
        rules.append(ctrl.Rule(antecedent=obsDy['up'], consequent=moveY['down']))
        rules.append(ctrl.Rule(antecedent=obsDy['down'], consequent=moveY['up']))
        rules.append(ctrl.Rule(antecedent=obsDx['left'], consequent=moveX['right']))
        rules.append(ctrl.Rule(antecedent=obsDx['right'], consequent=moveX['left']))
        
        # Combined wall + goal rules for better navigation
        rules.append(ctrl.Rule(antecedent=wallDy['up'] & goalDx['left'], consequent=(moveY['down'], moveX['left'])))
        rules.append(ctrl.Rule(antecedent=wallDy['up'] & goalDx['right'], consequent=(moveY['down'], moveX['right'])))
        rules.append(ctrl.Rule(antecedent=wallDy['down'] & goalDx['left'], consequent=(moveY['up'], moveX['left'])))
        rules.append(ctrl.Rule(antecedent=wallDy['down'] & goalDx['right'], consequent=(moveY['up'], moveX['right'])))
        
        rules.append(ctrl.Rule(antecedent=wallDx['left'] & goalDy['up'], consequent=(moveX['right'], moveY['up'])))
        rules.append(ctrl.Rule(antecedent=wallDx['left'] & goalDy['down'], consequent=(moveX['right'], moveY['down'])))
        rules.append(ctrl.Rule(antecedent=wallDx['right'] & goalDy['up'], consequent=(moveX['left'], moveY['up'])))
        rules.append(ctrl.Rule(antecedent=wallDx['right'] & goalDy['down'], consequent=(moveX['left'], moveY['down'])))

        # combined obstacle + goal rules
        rules.append(ctrl.Rule(antecedent=obsDy['up'] & goalDx['left'], consequent=(moveY['down'], moveX['left'])))
        rules.append(ctrl.Rule(antecedent=obsDy['up'] & goalDx['right'], consequent=(moveY['down'], moveX['right'])))
        rules.append(ctrl.Rule(antecedent=obsDy['down'] & goalDx['left'], consequent=(moveY['up'], moveX['left'])))
        rules.append(ctrl.Rule(antecedent=obsDy['down'] & goalDx['right'], consequent=(moveY['up'], moveX['right'])))

        rules.append(ctrl.Rule(antecedent=obsDx['left'] & goalDy['up'], consequent=(moveX['right'], moveY['up'])))
        rules.append(ctrl.Rule(antecedent=obsDx['left'] & goalDy['down'], consequent=(moveX['right'], moveY['down'])))
        rules.append(ctrl.Rule(antecedent=obsDx['right'] & goalDy['up'], consequent=(moveX['left'], moveY['up'])))
        rules.append(ctrl.Rule(antecedent=obsDx['right'] & goalDy['down'], consequent=(moveX['left'], moveY['down'])))

        for r in rules:
            r.and_func = np.fmin
            r.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        sim = ctrl.ControlSystemSimulation(system) 
        return sim



    def call_fuzzy_logic(self, u, d, l, r, bdx, bdy, gdx, gdy):
        # Choose the closest wall and assign direction:
        # Negative = wall on left/up, Positive = wall on right/down
        if l < r:
            wall_dx = -l  # Wall on left, negative value
        else:
            wall_dx = r   # Wall on right, positive value
            
        if u < d:
            wall_dy = -u  # Wall above, negative value
        else:
            wall_dy = d   # Wall below, positive value

        cgdx = np.clip(gdx, -self.perception_distance, self.perception_distance)
        cgdy = np.clip(gdy, -self.perception_distance, self.perception_distance)
        cbdx = np.clip(bdx, -self.perception_distance, self.perception_distance)
        cbdy = np.clip(bdy, -self.perception_distance, self.perception_distance)
        
        # Amplify wall importance (adjust multiplier to tune strength: 1.5-3.0)
        WALL_WEIGHT = 1.0
        wdx = np.clip(wall_dx * WALL_WEIGHT, -self.perception_distance, self.perception_distance)
        wdy = np.clip(wall_dy * WALL_WEIGHT, -self.perception_distance, self.perception_distance)
        
        # Avoid exact zero to prevent ambiguous membership (both left and right would be 1.0)
        EPSILON = 1
        if abs(wdx) < EPSILON:
            wdx = -EPSILON if gdx >= 0 else EPSILON  # Bias based on goal direction
        if abs(wdy) < EPSILON:
            wdy = -EPSILON if gdy >= 0 else EPSILON

        print("\n========== FUZZY LOGIC DEBUG ==========")
        print(f"Raw distances - u:{u:.1f} d:{d:.1f} l:{l:.1f} r:{r:.1f}")
        print(f"Inputs - wallDx:{wdx:.1f} wallDy:{wdy:.1f} goalDx:{cgdx:.1f} goalDy:{cgdy:.1f} obsDx:{cbdx:.1f} obsDy:{cbdy:.1f}")

        # Store input values for debugging
        input_values = {'wallDx': wdx, 'wallDy': wdy, 'goalDx': cgdx, 'goalDy': cgdy, 'obsDx': cbdx, 'obsDy': cbdy}

        self.fuzzy_ctrl.input['wallDx'] = wdx
        self.fuzzy_ctrl.input['wallDy'] = wdy
        self.fuzzy_ctrl.input['goalDx'] = cgdx
        self.fuzzy_ctrl.input['goalDy'] = cgdy
        self.fuzzy_ctrl.input['obsDx'] = cbdx
        self.fuzzy_ctrl.input['obsDy'] = cbdy

        # Debug membership values
        print("\n--- Membership Values ---")
        for var in self.fuzzy_ctrl.ctrl.fuzzy_variables:
            if var.label in ['wallDx', 'wallDy', 'goalDx', 'goalDy', 'obsDx', 'obsDy']:
                print(f"{var.label}: (value={input_values[var.label]:.1f}, range=[{var.universe[0]:.1f}, {var.universe[-1]:.1f}])")
                for term_name, term_mf in var.terms.items():
                    input_val = input_values[var.label]
                    membership = fuzz.interp_membership(var.universe, term_mf.mf, input_val)
                    # Show all memberships, even zero ones
                    print(f"  {term_name}: {membership:.3f}")

        self.fuzzy_ctrl.compute()
        
        move_x = self.fuzzy_ctrl.output['moveX']
        move_y = self.fuzzy_ctrl.output['moveY']
        
        # Debug rule activations - compute manually
        print("\n--- Rule Activations ---")
        for i, rule in enumerate(self.fuzzy_ctrl.ctrl.rules):
            # Manually compute activation strength by evaluating antecedent
            activation = None
            try:
                # Get all antecedent terms and their memberships
                antecedent_terms = []
                for clause in str(rule).split('IF ')[1].split(' THEN')[0].split(' AND '):
                    clause = clause.strip()
                    if '[' in clause and ']' in clause:
                        var_name = clause.split('[')[0]
                        term_name = clause.split('[')[1].split(']')[0]
                        if var_name in input_values:
                            var = [v for v in self.fuzzy_ctrl.ctrl.fuzzy_variables if v.label == var_name][0]
                            term_mf = var.terms[term_name]
                            membership = fuzz.interp_membership(var.universe, term_mf.mf, input_values[var_name])
                            antecedent_terms.append((var_name, term_name, membership))
                
                # Compute activation using fmin (AND)
                if antecedent_terms:
                    activation = min([m for _, _, m in antecedent_terms])
                    if activation > 0.01:
                        print(f"Rule {i}: activation={activation:.3f}")
                        for var_name, term_name, membership in antecedent_terms:
                            print(f"  {var_name}[{term_name}]={membership:.3f}", end="")
                        print(f" -> {str(rule).split('THEN ')[1].split('AND')[0].strip()}")
            except:
                pass
        
        print(f"\n--- Output ---")
        print(f"moveX: {move_x:.3f}, moveY: {move_y:.3f}")
        
        # Determine final action based on X and Y outputs
        # Choose the dominant direction
        if abs(move_x) > abs(move_y):
            instruction = Action.LEFT if move_x < 0 else Action.RIGHT
        elif abs(move_y) > abs(move_x):
            instruction = Action.UP if move_y < 0 else Action.DOWN
        else:
            # If equal, prefer vertical movement
            if abs(move_y) > 0.1:
                instruction = Action.UP if move_y < 0 else Action.DOWN
            elif abs(move_x) > 0.1:
                instruction = Action.LEFT if move_x < 0 else Action.RIGHT
            else:
                instruction = Action.UP  # Default when no clear direction
        
        print(f"Final instruction: {instruction}")
        print("========================================\n")
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

            reached = gR.colliderect(pR) # colliderect

            if reached:
                self._path_index += 1
                return
            return

