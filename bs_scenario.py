"""Spielerfeld generieren: n Spieler mit Elo-Ratings, nach Rating absteigend zu Setzplätzen 1..n zugeordnet."""

from __future__ import annotations

import random
from dataclasses import dataclass

BASE_RATING = 2000.0


@dataclass(frozen=True)
class Player:
    seed: int
    rating: float


def generate_players(n_players: int, rating_spread: float, seed: int) -> list[Player]:
    """rating_spread = Standardabweichung der Ratings um BASE_RATING (0 = alle gleich stark)."""
    rng = random.Random(seed)
    ratings = [BASE_RATING + rng.gauss(0.0, rating_spread) for _ in range(n_players)]
    ratings.sort(reverse=True)
    return [Player(seed=i + 1, rating=r) for i, r in enumerate(ratings)]


def rating_by_seed(players: list[Player]) -> dict[int, float]:
    return {p.seed: p.rating for p in players}
