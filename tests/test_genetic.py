import pytest

import Genetic as ga_mod
import builtins

class DummyPlayer:
    def __init__(self):
        self.attributes = None


class DummyMonster:
    """
    Monster that returns deterministic (rounds, cumulative) based on player.attributes
    so we can test evaluation/selection without randomness.
    """
    def __init__(self, mapping=None, default=(0, 0.0)):
        self.mapping = mapping or {}
        self.default = default

    def mock_fight(self, player):
        key = tuple(player.attributes)
        return self.mapping.get(key, self.default)


@pytest.fixture(autouse=True)
def patch_constants(monkeypatch):
    """
    Make tests independent of your real Constants.py values.
    """
    monkeypatch.setattr(ga_mod, "NUM_ATTRIBUTES", 6, raising=False)
    monkeypatch.setattr(ga_mod, "MAX_ATTRIBUTE", 1000, raising=False)
    monkeypatch.setattr(ga_mod, "MIN_A", -1000, raising=False)
    monkeypatch.setattr(ga_mod, "MAX_A", 1000, raising=False)


def test_init_population_shape_and_bounds(monkeypatch):
    # Force randint to a predictable value
    monkeypatch.setattr(ga_mod.random, "randint", lambda a, b: a)  # always MIN_A

    g = ga_mod.Genetic(pop_size=5)
    g.init_population()

    assert len(g.population) == 5
    for indiv in g.population:
        assert len(indiv) == ga_mod.NUM_ATTRIBUTES
        assert all(ga_mod.MIN_A <= x <= ga_mod.MAX_A for x in indiv)


def test_init_population_seeding_overwrites_first(monkeypatch):
    monkeypatch.setattr(ga_mod.random, "randint", lambda a, b: 0)

    seed = [1, 2, 3, 4, 5, 6]
    g = ga_mod.Genetic(pop_size=4)
    g.init_population(seed=seed)

    assert g.population[0] == seed
    # Others are from randint stub (0)
    assert all(indiv == [0] * ga_mod.NUM_ATTRIBUTES for indiv in g.population[1:])


def test_calculate_diversity_empty_or_single():
    g = ga_mod.Genetic(pop_size=1)
    g.population = []
    assert g.calculate_diversity() == 0

    g.population = [[0] * ga_mod.NUM_ATTRIBUTES]
    assert g.calculate_diversity() == 0


def test_calculate_diversity_two_individuals_exact():
    g = ga_mod.Genetic(pop_size=2)
    g.population = [
        [0, 0, 0, 0, 0, 0],
        [1, 2, 3, 4, 5, 6],
    ]
    # Only one pair => diversity = L1 distance
    assert g.calculate_diversity() == sum([1, 2, 3, 4, 5, 6])


def test_evaluate_updates_best_and_returns_found4(monkeypatch):
    # Avoid printing noise during tests
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: None)

    indiv_a = [0, 0, 0, 0, 0, 0]
    indiv_b = [1, 1, 1, 1, 1, 1]
    indiv_c = [2, 2, 2, 2, 2, 2]

    mapping = {
        tuple(indiv_a): (2, 10.0),
        tuple(indiv_b): (3, 1.0),
        tuple(indiv_c): (4, -5.0),  # should trigger found4 True
    }

    monster = DummyMonster(mapping=mapping)
    player = DummyPlayer()

    g = ga_mod.Genetic(pop_size=3)
    g.population = [indiv_a, indiv_b, indiv_c]

    found4 = g.evaluate(monster, player)

    assert found4 is True
    assert len(g.fitness) == 3
    # Best should be the one with rounds=4 (highest priority)
    assert g.best_individual == indiv_c
    assert g.best_rounds == 4
    assert g.best_cum == -5.0
    assert g.best_fitness == pytest.approx(1000.0 * 4 + (-5.0))
    assert len(g.diversity_history) == 1


def test_select_parent_tournament_picks_best(monkeypatch):
    g = ga_mod.Genetic(pop_size=5)
    g.population = [
        [0] * ga_mod.NUM_ATTRIBUTES,
        [1] * ga_mod.NUM_ATTRIBUTES,
        [2] * ga_mod.NUM_ATTRIBUTES,
        [3] * ga_mod.NUM_ATTRIBUTES,
        [4] * ga_mod.NUM_ATTRIBUTES,
    ]
    # fitness tuples: (fit, rounds, cumulative)
    g.fitness = [
        (10, 0, 0),
        (50, 0, 0),  # best among sampled in this test
        (20, 0, 0),
        (5, 0, 0),
        (1, 0, 0),
    ]

    # Force tournament candidates to be [0,1,3,4] => best is index 1
    monkeypatch.setattr(ga_mod.random, "sample", lambda seq, k: [0, 1, 3, 4])

    parent = g.select_parent(k=4)
    assert parent == [1] * ga_mod.NUM_ATTRIBUTES
    # Ensure it's a copy
    parent[0] = 999
    assert g.population[1][0] == 1


def test_crossover_uniform(monkeypatch):
    g = ga_mod.Genetic(pop_size=2)

    p1 = [1, 1, 1, 1, 1, 1]
    p2 = [2, 2, 2, 2, 2, 2]

    # strategy < 0.3 => uniform
    seq = iter([0.1] + [0.4, 0.6, 0.4, 0.6, 0.4, 0.6])  # pick p1 then p2 alternately
    monkeypatch.setattr(ga_mod.random, "random", lambda: next(seq))

    child = g.crossover(p1, p2)
    assert child == [1, 2, 1, 2, 1, 2]


def test_crossover_arithmetic(monkeypatch):
    g = ga_mod.Genetic(pop_size=2)
    p1 = [10, 10, 10, 10, 10, 10]
    p2 = [0, 0, 0, 0, 0, 0]

    # strategy in [0.3,0.6) => arithmetic
    monkeypatch.setattr(ga_mod.random, "random", lambda: 0.4)
    monkeypatch.setattr(ga_mod.random, "uniform", lambda a, b: 0.5)  # alpha=0.5

    child = g.crossover(p1, p2)
    assert child == [5, 5, 5, 5, 5, 5]


def test_crossover_two_point(monkeypatch):
    g = ga_mod.Genetic(pop_size=2)
    p1 = [1, 1, 1, 1, 1, 1]
    p2 = [9, 9, 9, 9, 9, 9]

    monkeypatch.setattr(ga_mod.random, "random", lambda: 0.7)  # in [0.6,0.8)
    # choose points [2,5]
    monkeypatch.setattr(ga_mod.random, "sample", lambda seq, k: [2, 5])

    child = g.crossover(p1, p2)
    assert child == [1, 1, 9, 9, 9, 1]


def test_mutate_no_mutation_returns_same_object(monkeypatch):
    g = ga_mod.Genetic(pop_size=2, mutation_prob=0.15)
    indiv = [1] * ga_mod.NUM_ATTRIBUTES

    # random() > mutation_prob => no mutation
    monkeypatch.setattr(ga_mod.random, "random", lambda: 0.99)

    out = g.mutate(indiv)
    # Important: your code returns the same list (not a copy) in this branch
    assert out is indiv


def test_mutate_aggressive_multi_attribute_changes_some(monkeypatch):
    g = ga_mod.Genetic(pop_size=2, mutation_prob=1.0)  # always mutate
    indiv = [0] * ga_mod.NUM_ATTRIBUTES

    # First random() -> pass mutation gate (<=1.0)
    # Second random() -> mutation_type < 0.3 => aggressive
    # Next randoms decide whether full reset vs step; we force full reset path
    rseq = iter([0.0, 0.1] + [0.0] * 20)  # lots of 0.0 => choose reset branch
    monkeypatch.setattr(ga_mod.random, "random", lambda: next(rseq))

    # m=3 genes
    monkeypatch.setattr(ga_mod.random, "randint", lambda a, b: 3 if (a, b) == (3, 8) else ga_mod.MAX_A)
    # choose indices [0,1,2]
    monkeypatch.setattr(ga_mod.random, "sample", lambda seq, k: [0, 1, 2])

    out = g.mutate(indiv)
    assert out is not indiv
    assert out[:3] == [ga_mod.MAX_A, ga_mod.MAX_A, ga_mod.MAX_A]
    assert out[3:] == [0] * (ga_mod.NUM_ATTRIBUTES - 3)
    assert all(ga_mod.MIN_A <= x <= ga_mod.MAX_A for x in out)


def test_next_generation_keeps_elites(monkeypatch):
    g = ga_mod.Genetic(pop_size=6, elite_size=2)
    g.population = [
        [0]*ga_mod.NUM_ATTRIBUTES,  # best
        [1]*ga_mod.NUM_ATTRIBUTES,  # second best
        [2]*ga_mod.NUM_ATTRIBUTES,
        [3]*ga_mod.NUM_ATTRIBUTES,
        [4]*ga_mod.NUM_ATTRIBUTES,
        [5]*ga_mod.NUM_ATTRIBUTES,
    ]
    g.fitness = [
        (100, 0, 0),
        (90, 0, 0),
        (10, 0, 0),
        (9, 0, 0),
        (8, 0, 0),
        (7, 0, 0),
    ]

    # Make reproduction deterministic:
    # - always select parent index 0
    monkeypatch.setattr(g, "select_parent", lambda k=4: g.population[0][:])
    # - crossover returns parent1
    monkeypatch.setattr(g, "crossover", lambda p1, p2: p1[:])
    # - mutate returns child unchanged
    monkeypatch.setattr(g, "mutate", lambda indiv: indiv)

    g.next_generation()

    assert len(g.population) == 6
    # Elites preserved at front
    assert g.population[0] == [0]*ga_mod.NUM_ATTRIBUTES
    assert g.population[1] == [1]*ga_mod.NUM_ATTRIBUTES


def test_random_restart_keeps_best(monkeypatch):
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: None)

    g = ga_mod.Genetic(pop_size=6)
    g.population = [
        [0]*ga_mod.NUM_ATTRIBUTES,  # best
        [1]*ga_mod.NUM_ATTRIBUTES,  # second
        [2]*ga_mod.NUM_ATTRIBUTES,
        [3]*ga_mod.NUM_ATTRIBUTES,
        [4]*ga_mod.NUM_ATTRIBUTES,
        [5]*ga_mod.NUM_ATTRIBUTES,
    ]
    g.fitness = [
        (100, 0, 0),
        (90, 0, 0),
        (10, 0, 0),
        (9, 0, 0),
        (8, 0, 0),
        (7, 0, 0),
    ]

    # make randint deterministic
    monkeypatch.setattr(ga_mod.random, "randint", lambda a, b: 42)

    g.random_restart(keep_best=2)

    assert len(g.population) == 6
    assert g.population[0] == [0]*ga_mod.NUM_ATTRIBUTES
    assert g.population[1] == [1]*ga_mod.NUM_ATTRIBUTES
    # Rest are random-filled with 42
    for indiv in g.population[2:]:
        assert indiv == [42]*ga_mod.NUM_ATTRIBUTES
