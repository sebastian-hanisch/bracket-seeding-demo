"""Monte-Carlo-Vergleich: Richtung und Größenordnung der gemessenen Effekte, mit Toleranzband
(plattform-robust - keine harten Gleichheiten auf Zufallsergebnissen, s. feedback_ci_platform_robust_tests)."""

from __future__ import annotations

import random

from bs_bracket import build_bracket
from bs_evaluation import monte_carlo_compare, simulate_tournament
from bs_scenario import generate_players


def test_seeded_top2_never_meet_before_final_even_measured():
    # Strukturell bewiesen in test_bracket.py; hier zusätzlich über viele Simulationen bestätigt.
    players = generate_players(16, rating_spread=150, seed=1)
    stats = monte_carlo_compare(players, n_reps=2000, seed=1)
    assert stats["seeded"].p_top2_meet_before_final == 0.0


def test_random_policy_top2_sometimes_meet_before_final():
    players = generate_players(16, rating_spread=150, seed=1)
    stats = monte_carlo_compare(players, n_reps=2000, seed=1)
    assert stats["random"].p_top2_meet_before_final > 0.05


def test_seeded_policy_increases_favourite_win_probability():
    players = generate_players(32, rating_spread=150, seed=1)
    stats = monte_carlo_compare(players, n_reps=4000, seed=1)
    assert stats["seeded"].p_top_seed_wins > stats["random"].p_top_seed_wins


def test_seeded_policy_reduces_upset_rate():
    players = generate_players(32, rating_spread=150, seed=1)
    stats = monte_carlo_compare(players, n_reps=4000, seed=1)
    assert stats["seeded"].upset_rate < stats["random"].upset_rate


def test_seeded_policy_keeps_top_seed_alive_longer_on_average():
    players = generate_players(32, rating_spread=150, seed=1)
    stats = monte_carlo_compare(players, n_reps=4000, seed=1)
    assert stats["seeded"].mean_elimination_round_seed1 >= stats["random"].mean_elimination_round_seed1


def test_effect_shrinks_as_field_gets_very_lopsided_in_rating():
    # Bei extrem großer Streuung gewinnt der Favorit ohnehin fast immer - der Unterschied zwischen den
    # Politiken wird kleiner (gemessen, nicht als exakte Invarianz behauptet).
    players = generate_players(32, rating_spread=500, seed=1)
    stats = monte_carlo_compare(players, n_reps=4000, seed=1)
    gap = stats["seeded"].p_top_seed_wins - stats["random"].p_top_seed_wins
    assert 0.0 <= gap < 0.10


def test_monte_carlo_compare_matches_count_is_n_minus_one_per_tournament_on_average():
    # Jedes Match eliminiert genau einen Spieler - Gesamtzahl Matches ist IMMER n-1, unabhängig von Politik
    # und Freilosverteilung. Direkt an simulate_tournament geprüft (kein Sweep nötig).
    players = generate_players(11, rating_spread=150, seed=3)
    for policy in ("seeded", "random"):
        rng = random.Random(42)
        result = simulate_tournament(players, policy, rng)
        assert result.n_matches == 10


def test_simulate_tournament_champion_is_a_valid_seed():
    players = generate_players(9, rating_spread=150, seed=2)
    rng = random.Random(5)
    result = simulate_tournament(players, "seeded", rng)
    assert 1 <= result.champion <= 9


def test_simulate_tournament_random_policy_needs_bracket_rng_internally():
    # Regressionsschutz: simulate_tournament darf mit policy="random" nicht crashen (baut intern den
    # Zufalls-Bracket selbst aus dem übergebenen rng).
    players = generate_players(6, rating_spread=150, seed=4)
    rng = random.Random(9)
    result = simulate_tournament(players, "random", rng)
    assert result.champion in {p.seed for p in players}


def test_build_bracket_and_simulate_use_independent_players_list_consistently():
    players = generate_players(20, rating_spread=200, seed=6)
    bracket = build_bracket(len(players))
    assert bracket.n_players == 20


def test_simulate_tournament_rounds_progression_shape():
    players = generate_players(10, rating_spread=150, seed=8)
    rng = random.Random(11)
    result = simulate_tournament(players, "seeded", rng)
    # 10 Spieler -> 16er-Feld -> 4 Runden; rounds hat 5 Einträge (Start + je Runde ein Ergebnis).
    assert len(result.rounds) == 5
    assert len(result.rounds[0]) == 16
    assert result.rounds[-1] == (result.champion,)
    assert sorted(s for s in result.rounds[0] if s is not None) == list(range(1, 11))
