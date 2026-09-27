"""Elo-Erwartungswert gegen bekannte Referenzwerte."""

from __future__ import annotations

import random

import pytest

from bs_elo import expected_score, simulate_match


def test_equal_ratings_give_fifty_fifty():
    assert expected_score(2000, 2000) == pytest.approx(0.5)


def test_two_hundred_point_gap_gives_known_reference_value():
    # Standard-Richtwert aus jeder Elo-Tabelle: ~76 % für den 200-Punkte-Favoriten.
    assert expected_score(2200, 2000) == pytest.approx(0.7597, abs=0.001)


def test_four_hundred_point_gap_gives_known_reference_value():
    # 400 Punkte Unterschied: 1/(1+10^-1) = 10/11 ~ 0.9091.
    assert expected_score(2400, 2000) == pytest.approx(10 / 11, abs=0.0005)


@pytest.mark.parametrize("ra, rb", [(2000, 1800), (2500, 1200), (1000, 1000), (1600, 2400)])
def test_symmetry(ra, rb):
    assert expected_score(ra, rb) + expected_score(rb, ra) == pytest.approx(1.0)


def test_higher_rating_always_has_higher_expected_score():
    assert expected_score(2200, 2000) > 0.5
    assert expected_score(2000, 2200) < 0.5


def test_simulate_match_win_rate_matches_expected_score_over_many_trials():
    rng = random.Random(7)
    wins = sum(simulate_match(2200, 2000, rng) for _ in range(20_000))
    rate = wins / 20_000
    assert rate == pytest.approx(expected_score(2200, 2000), abs=0.02)


def test_simulate_match_is_deterministic_given_same_rng_state():
    a = simulate_match(2000, 2000, random.Random(1))
    b = simulate_match(2000, 2000, random.Random(1))
    assert a == b
