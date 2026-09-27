"""Setzlisten-Algorithmus für K.-o.-Turniere: rekursive Verdopplung, Freilos-Ableitung, Baumaufbau.

Der Algorithmus ist die überall in Turniersoftware (Tennis-Grand-Slams, NCAA, ...) verwendete Standard-
Setzliste - für 16 Plätze reproduziert er exakt [1,16,8,9,4,13,5,12,2,15,7,10,3,14,6,11] (Regressionstest in
tests/test_bracket.py), unabhängig bestätigt durch die von Wikipedia ("Seeding (sports)") genannte Eigenschaft,
dass die Summe beider Setzplätze je Partie innerhalb einer Runde konstant ist (17 in Runde 1, 9 im Viertelfinale
usw.). Freilose bei Nicht-Zweierpotenz ergeben sich automatisch: Setzplätze über der echten Teilnehmerzahl sind
"Phantome", ein echter Spieler gegen ein Phantom rückt ohne Partie vor - genau das FIDE-World-Cup-Muster (die
obersten gesetzten Spieler bekommen ein Freilos in Runde 2), ohne dass dafür eine Sonderregel nötig ist.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


def standard_seed_order(size: int) -> list[int]:
    """Setzlisten-Reihenfolge für ein Feld der Größe `size` (muss eine Zweierpotenz sein)."""
    if size < 1 or size & (size - 1) != 0:
        raise ValueError("size muss eine Zweierpotenz sein")
    seeds = [1]
    while len(seeds) < size:
        m = 2 * len(seeds) + 1
        seeds = [x for s in seeds for x in (s, m - s)]
    return seeds


def next_power_of_two(n: int) -> int:
    size = 1
    while size < n:
        size *= 2
    return size


@dataclass(frozen=True)
class Match:
    seed_a: int | None
    seed_b: int | None


@dataclass(frozen=True)
class Bracket:
    n_players: int
    bracket_size: int
    policy: str
    round1_slots: tuple[int | None, ...]  # bracket_size Einträge, None = Phantom (Freilos für den Gegner)


def build_bracket(n_players: int, policy: str = "seeded", rng: random.Random | None = None) -> Bracket:
    """Baut die Runde-1-Belegung des Turnierbaums.

    policy="seeded": Standard-Setzliste (rekursive Verdopplung), Phantome sind die Setzplätze > n_players -
    dadurch bekommen automatisch die höchsten Setzplätze ein Freilos.
    policy="random": dieselbe Baumstruktur, aber die n_players echten Setzplätze und die Phantom-Plätze werden
    zufällig auf die Slots verteilt - Freilose treffen dann zufällige Spieler, nicht die Topplätze.
    """
    if n_players < 2:
        raise ValueError("n_players muss mindestens 2 sein")
    if policy not in ("seeded", "random"):
        raise ValueError("policy muss 'seeded' oder 'random' sein")

    bracket_size = next_power_of_two(n_players)
    order = standard_seed_order(bracket_size)
    slots: list[int | None] = [seed if seed <= n_players else None for seed in order]

    if policy == "random":
        if rng is None:
            raise ValueError("policy='random' braucht ein rng")
        rng.shuffle(slots)

    return Bracket(n_players=n_players, bracket_size=bracket_size, policy=policy, round1_slots=tuple(slots))


def round1_matches(bracket: Bracket) -> list[Match]:
    slots = bracket.round1_slots
    return [Match(seed_a=slots[i], seed_b=slots[i + 1]) for i in range(0, len(slots), 2)]


def byes(bracket: Bracket) -> list[int]:
    """Setzplätze, die in Runde 1 gegen ein Phantom stehen (Freilos)."""
    result = []
    for match in round1_matches(bracket):
        if match.seed_a is None and match.seed_b is not None:
            result.append(match.seed_b)
        elif match.seed_b is None and match.seed_a is not None:
            result.append(match.seed_a)
    return result


def n_rounds(bracket: Bracket) -> int:
    r = 0
    size = bracket.bracket_size
    while size > 1:
        size //= 2
        r += 1
    return r
