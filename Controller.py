from Instructions import *

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


class Controller:
    def __init__(self, app=None):
        self.app = app
        self._path_index = 0
        self.best_path = None

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

        reach_px = 2  # consider the checkpoint hit when within 16 pixels

        while self._path_index < len(self.best_path):
            target_x, target_y = self.tile_to_pixel_center(
                self.best_path[self._path_index], maze
            )
            x, y = player.get_position()
            x += player.size_x * 0.5
            y += player.size_y * 0.5
            dx = target_x - x
            dy = target_y - y
            if abs(dx) <= reach_px and abs(dy) <= reach_px:
                self._path_index += 1
                continue
            if abs(dx) > abs(dy):
                return Action.RIGHT if dx > 0 else Action.LEFT
            return Action.DOWN if dy > 0 else Action.UP
        return None
