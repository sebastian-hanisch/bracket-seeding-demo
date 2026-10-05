"""Unabhängiges Orakel für Setzliste und K.-o.-Simulation.

Rechenwege des Orakels (nicht der Code der Demo):
- Setzliste: Aufbau durch Spiegeln (Partner k+1-s je Verdopplungsstufe k), dazu die Summenregel im "Chalk"-Turnier
  (der jeweils bessere Setzplatz gewinnt: Summe je Runde 2^(R-r+1)+1).
- Kennzahlen: exakte Verteilungsrechnung über den Turnierbaum (Gewinner-Verteilung je Teilbaum mit den Elo-
  Erwartungswerten) statt Zufallsziehung; gegen monte_carlo_compare mit Vier-Sigma-Band.
- Überraschungsrate bei Freilosen: steigt unter der Setzliste (Voraussetzung der App-/README-Aussage).
"""

from __future__ import annotations

import random

import numpy as np
import pytest

from bs_bracket import build_bracket, standard_seed_order
from bs_elo import expected_score
from bs_evaluation import monte_carlo_compare
from bs_scenario import generate_players, rating_by_seed


def _mirror_order(size):
    order, k = [1], 1
    while k < size:
        k *= 2
        order = [x for s in order for x in (s, k + 1 - s)]
    return order


@pytest.mark.parametrize("size", [1, 2, 4, 8, 16, 32, 64, 128])
def test_seed_order_mirror_construction_and_chalk_sums(size):
    order = standard_seed_order(size)
    assert order == _mirror_order(size)
    cur = order
    while len(cur) > 1:
        assert {cur[i] + cur[i + 1] for i in range(0, len(cur), 2)} == {len(cur) + 1}
        cur = [min(cur[i], cur[i + 1]) for i in range(0, len(cur), 2)]


def exact_stats(ratings, slots):
    """(P(Setzplatz 1 siegt), P(1 und 2 treffen sich vor dem Finale), E[Überraschungen], E[Ausscheiderunde Setzplatz 1])."""
    seeds = sorted(ratings)
    idx = {s: i for i, s in enumerate(seeds)}
    seedv = np.array(seeds)
    p = np.zeros((len(seeds), len(seeds)))
    for a in seeds:
        for b in seeds:
            if a != b:
                p[idx[a], idx[b]] = expected_score(ratings[a], ratings[b])
    cur = []
    for s in slots:
        v = np.zeros(len(seeds))
        if s is not None:
            v[idx[s]] = 1.0
        cur.append(v)
    e_up = p_top2 = elim1 = 0.0
    rnd, n_rounds = 1, len(slots).bit_length() - 1
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur), 2):
            a, b = cur[i], cur[i + 1]
            if a.sum() == 0 or b.sum() == 0:
                nxt.append(a + b)
                continue
            joint = np.outer(a, b)
            nxt.append((joint * p).sum(axis=1) + (joint * p.T).sum(axis=0))
            e_up += (joint * p * (seedv[:, None] > seedv[None, :])).sum()
            e_up += (joint * p.T * (seedv[None, :] > seedv[:, None])).sum()
            if len(cur) > 2:
                p_top2 += a[idx[1]] * b[idx[2]] + a[idx[2]] * b[idx[1]]
            elim1 += rnd * (a[idx[1]] * (b * (1 - p[idx[1], :])).sum() + b[idx[1]] * (a * (1 - p[idx[1], :])).sum())
        cur, rnd = nxt, rnd + 1
    p1 = cur[0][idx[1]]
    return p1, p_top2, e_up, elim1 + (n_rounds + 1) * p1


def _exact_random(ratings, n, n_perm, seed):
    rng = random.Random(seed)
    acc = np.zeros(4)
    for _ in range(n_perm):
        e = exact_stats(ratings, list(build_bracket(n, "random", rng).round1_slots))
        acc += [e[0], e[1], e[2] / (n - 1), e[3]]
    return acc / n_perm


def test_exact_oracle_hand_example_two_equal_players():
    # 2 Spieler mit gleichem Rating: je 50 % Sieg, genau eine Partie, davon mit 50 % eine Überraschung.
    p1, p_top2, e_up, elim1 = exact_stats({1: 2000.0, 2: 2000.0}, [1, 2])
    assert (p1, p_top2, e_up) == pytest.approx((0.5, 0.0, 0.5))
    assert elim1 == pytest.approx(0.5 * 1 + 0.5 * 2)


@pytest.mark.parametrize("n, spread, seed", [(6, 150, 3), (10, 300, 1), (16, 150, 1)])
def test_seeded_statistics_match_exact_distribution(n, spread, seed):
    players = generate_players(n, spread, seed)
    stats = monte_carlo_compare(players, 3000, seed)["seeded"]
    p1, p_top2, e_up, elim1 = exact_stats(rating_by_seed(players), list(build_bracket(n).round1_slots))
    assert p_top2 == 0.0 == stats.p_top2_meet_before_final
    assert abs(stats.p_top_seed_wins - p1) < 4 * (0.25 / 3000) ** 0.5
    assert abs(stats.upset_rate - e_up / (n - 1)) < 0.03
    assert abs(stats.mean_elimination_round_seed1 - elim1) < 0.12


def test_random_policy_top2_meeting_probability_is_one_third_for_four_players():
    # 4 Spieler: zufällige Paarung -> Setzplatz 1 und 2 treffen sich im Halbfinale mit Wahrscheinlichkeit 1/3.
    players = generate_players(4, 150, 1)
    stats = monte_carlo_compare(players, 3000, 1)["random"]
    assert abs(stats.p_top2_meet_before_final - 1 / 3) < 4 * (2 / 9 / 3000) ** 0.5


def test_upset_rate_rises_under_seeding_when_there_are_byes():
    # 10 Spieler, Streuung 300: unter der Setzliste überspringen die Topgesetzten die leichten Runde-1-Partien,
    # die Überraschungsrate steigt gegenüber zufälliger Auslosung (exakt gerechnet, kein Monte-Carlo-Rauschen).
    players = generate_players(10, 300, 1)
    ratings = rating_by_seed(players)
    seeded = exact_stats(ratings, list(build_bracket(10).round1_slots))[2] / 9
    rand = _exact_random(ratings, 10, 150, 1)[2]
    assert seeded > rand + 0.02
