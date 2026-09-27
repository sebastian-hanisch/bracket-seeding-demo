"""Regressionstest gegen die öffentlich bekannte Standard-16er-Setzliste und Eigenschaftstests."""

from __future__ import annotations

import random

import pytest

from bs_bracket import Bracket, build_bracket, byes, n_rounds, next_power_of_two, round1_matches, standard_seed_order

# Öffentlich bekannte Standard-16er-Setzliste (Tennis-Grand-Slam-/NCAA-Raster), von Hand nachgerechnet.
KNOWN_16_ORDER = [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]


def test_standard_seed_order_matches_known_16_bracket():
    assert standard_seed_order(16) == KNOWN_16_ORDER


@pytest.mark.parametrize("size", [2, 4, 8, 16, 32, 64])
def test_standard_seed_order_round1_sum_property(size):
    # Wikipedia "Seeding (sports)": Summe beider Setzplätze je Partie ist innerhalb einer Runde konstant
    # (für Runde 1: size+1 - 17 für ein 16er-Feld, wie im Artikel genannt).
    order = standard_seed_order(size)
    sums = {order[i] + order[i + 1] for i in range(0, size, 2)}
    assert sums == {size + 1}


@pytest.mark.parametrize("size", [2, 4, 8, 16, 32, 64])
def test_standard_seed_order_is_a_permutation(size):
    order = standard_seed_order(size)
    assert sorted(order) == list(range(1, size + 1))


@pytest.mark.parametrize("size", [0, 3, 5, 6, 7, 9])
def test_standard_seed_order_rejects_non_power_of_two(size):
    with pytest.raises(ValueError):
        standard_seed_order(size)


@pytest.mark.parametrize(
    "n, expected",
    [(1, 1), (2, 2), (3, 4), (4, 4), (5, 8), (8, 8), (9, 16), (16, 16), (17, 32), (100, 128)],
)
def test_next_power_of_two(n, expected):
    assert next_power_of_two(n) == expected


@pytest.mark.parametrize("n_players", [4, 8, 16, 32])
def test_power_of_two_field_has_no_byes(n_players):
    bracket = build_bracket(n_players)
    assert byes(bracket) == []
    for match in round1_matches(bracket):
        assert match.seed_a is not None and match.seed_b is not None


@pytest.mark.parametrize(
    "n_players, expected_byes",
    [(10, {1, 2, 3, 4, 5, 6}), (7, {1}), (5, {1, 2, 3}), (100, set(range(1, 29)))],
)
def test_byes_go_to_exactly_the_top_seeds(n_players, expected_byes):
    bracket = build_bracket(n_players)
    assert set(byes(bracket)) == expected_byes
    assert len(byes(bracket)) == bracket.bracket_size - n_players


@pytest.mark.parametrize("n_players", list(range(2, 65)))
def test_every_real_seed_appears_in_exactly_one_round1_slot(n_players):
    bracket = build_bracket(n_players)
    real_seeds = [s for s in bracket.round1_slots if s is not None]
    assert sorted(real_seeds) == list(range(1, n_players + 1))


@pytest.mark.parametrize("n_players", list(range(2, 65)))
def test_no_match_has_two_phantoms(n_players):
    bracket = build_bracket(n_players)
    for match in round1_matches(bracket):
        assert not (match.seed_a is None and match.seed_b is None)


@pytest.mark.parametrize("n_players", [4, 8, 16, 32, 64])
def test_seed_one_and_two_never_meet_before_the_final_seeded(n_players):
    # Seed 1 und 2 liegen in der Standard-Setzliste stets in verschiedenen Hälften -> können sich erst im
    # letzten Spiel (dem Finale) treffen. Wir prüfen das strukturell: sie liegen in verschiedenen Hälften
    # von round1_slots (und damit auf jeder gröberen Ebene, da die Konstruktion rekursiv halbiert).
    bracket = build_bracket(n_players)
    idx1 = bracket.round1_slots.index(1)
    idx2 = bracket.round1_slots.index(2)
    half = bracket.bracket_size // 2
    assert (idx1 < half) != (idx2 < half)


@pytest.mark.parametrize("n_players", [8, 16, 32])
def test_top_four_seeds_are_spread_across_the_four_quarters(n_players):
    bracket = build_bracket(n_players)
    quarter = bracket.bracket_size // 4
    quarters = {s: bracket.round1_slots.index(s) // quarter for s in (1, 2, 3, 4)}
    assert len(set(quarters.values())) == 4


def test_random_policy_places_all_real_seeds_and_keeps_phantom_count():
    rng = random.Random(42)
    bracket = build_bracket(10, policy="random", rng=rng)
    real_seeds = [s for s in bracket.round1_slots if s is not None]
    assert sorted(real_seeds) == list(range(1, 11))
    assert bracket.round1_slots.count(None) == 6


def test_random_policy_requires_rng():
    with pytest.raises(ValueError):
        build_bracket(10, policy="random")


def test_random_policy_byes_are_not_always_the_top_seeds():
    # Über genug Wiederholungen sollten Freilose bei policy="random" auch mal NICHT die Topplätze treffen -
    # sonst wäre policy="random" versehentlich identisch zu policy="seeded".
    saw_non_top_bye = False
    for trial_seed in range(200):
        rng = random.Random(trial_seed)
        bracket = build_bracket(10, policy="random", rng=rng)
        if set(byes(bracket)) != {1, 2, 3, 4, 5, 6}:
            saw_non_top_bye = True
            break
    assert saw_non_top_bye


def test_invalid_policy_rejected():
    with pytest.raises(ValueError):
        build_bracket(8, policy="coinflip")


def test_too_few_players_rejected():
    with pytest.raises(ValueError):
        build_bracket(1)


@pytest.mark.parametrize("n_players, expected_rounds", [(2, 1), (3, 2), (4, 2), (8, 3), (9, 4), (16, 4), (100, 7)])
def test_n_rounds(n_players, expected_rounds):
    bracket = build_bracket(n_players)
    assert n_rounds(bracket) == expected_rounds
