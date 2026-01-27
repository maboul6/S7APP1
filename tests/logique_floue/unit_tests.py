import math
import builtins

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Controller import Controller
from Instructions import Action


class DummyMaze:
    tile_size_x = 40
    tile_size_y = 40


class DummyPlayer:
    pass


class DummyApp:
    def __init__(self):
        self.maze = DummyMaze()
        self.player = DummyPlayer()


@pytest.fixture(autouse=True)
def mute_print(monkeypatch):
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: None)


@pytest.fixture
def controller():
    return Controller(DummyApp())


def test_goal_right_no_walls(controller):
    action = controller.call_fuzzy_logic(
        u=math.inf,
        d=math.inf,
        l=math.inf,
        r=math.inf,
        bdx=0,
        bdy=0,
        gdx=30,
        gdy=0,
    )
    assert action == Action.RIGHT


def test_goal_left_no_walls(controller):
    action = controller.call_fuzzy_logic(
        u=math.inf,
        d=math.inf,
        l=math.inf,
        r=math.inf,
        bdx=0,
        bdy=0,
        gdx=-30,
        gdy=0,
    )
    assert action == Action.LEFT


def test_goal_down_no_walls(controller):
    action = controller.call_fuzzy_logic(
        u=math.inf,
        d=math.inf,
        l=math.inf,
        r=math.inf,
        bdx=0,
        bdy=0,
        gdx=0,
        gdy=30,
    )
    assert action == Action.DOWN


def test_goal_up_no_walls(controller):
    action = controller.call_fuzzy_logic(
        u=math.inf,
        d=math.inf,
        l=math.inf,
        r=math.inf,
        bdx=0,
        bdy=0,
        gdx=0,
        gdy=-30,
    )
    assert action == Action.UP


def test_goal_right_but_wall_right_close(controller):
    action = controller.call_fuzzy_logic(
        u=math.inf,
        d=math.inf,
        l=100,
        r=2,
        bdx=0,
        bdy=0,
        gdx=30,
        gdy=0,
    )
    assert action == Action.LEFT


def test_goal_up_but_wall_up_close(controller):
    action = controller.call_fuzzy_logic(
        u=2,
        d=100,
        l=math.inf,
        r=math.inf,
        bdx=0,
        bdy=0,
        gdx=0,
        gdy=-30,
    )
    assert action == Action.DOWN
