"""Elo-Erwartungswert-Formel (Arpad Elo, USCF/FIDE-Standard) und Partie-Simulation.

E_A = 1 / (1 + 10^((R_B - R_A) / 400)) - der Erwartungswert (= Gewinnwahrscheinlichkeit bei binärem Ausgang)
für Spieler A gegen Spieler B. Referenzwert aus jeder Elo-Tabelle: 200 Rating-Punkte Unterschied entsprechen
rund 76 % Gewinnwahrscheinlichkeit für den Favoriten (Testfixtur in tests/test_elo.py).
"""

from __future__ import annotations

import random


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def simulate_match(rating_a: float, rating_b: float, rng: random.Random) -> bool:
    """True, wenn Spieler A gewinnt."""
    return rng.random() < expected_score(rating_a, rating_b)
