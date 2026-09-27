"""Ein Turnierbaum-Durchlauf und der Monte-Carlo-Vergleich gesetzt gegen zufällig.

Wichtige, VORHER GEMESSENE Befunde (nicht angenommen, siehe README): Setzplatz 1 und 2 treffen sich unter
policy="seeded" STRUKTURELL NIE vor dem Finale (0 %, bewiesen in tests/test_bracket.py über die
Halbierungs-Eigenschaft der Setzliste) - bei zufälliger Auslosung dagegen mit spürbarer Wahrscheinlichkeit.
Die Siegchance des Favoriten und die Gesamt-Überraschungsrate unterscheiden sich zwischen den Politiken nur
MODERAT (wenige Prozentpunkte, kein Invarianz- und kein Dramatik-Fall) - beides real mit 15.000+ Wiederholungen
gemessen, nicht behauptet.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from bs_bracket import Bracket, build_bracket
from bs_elo import simulate_match
from bs_scenario import Player, rating_by_seed


@dataclass(frozen=True)
class TournamentResult:
    champion: int
    n_matches: int
    n_upsets: int
    top2_met_before_final: bool
    elimination_round: dict[int, int]  # Setzplatz -> Runde, in der er ausschied (Champion fehlt)
    rounds: tuple[tuple[int | None, ...], ...]  # Belegung je Runde (rounds[0] = Runde-1-Slots, rounds[-1] = [Sieger])


def simulate_tournament(players: list[Player], policy: str, rng: random.Random) -> TournamentResult:
    ratings = rating_by_seed(players)
    bracket_rng = rng if policy == "random" else None
    bracket: Bracket = build_bracket(len(players), policy=policy, rng=bracket_rng)

    slots: list[int | None] = list(bracket.round1_slots)
    rounds: list[tuple[int | None, ...]] = [tuple(slots)]
    n_matches = 0
    n_upsets = 0
    top2_met_before_final = False
    elimination_round: dict[int, int] = {}
    round_number = 1

    while len(slots) > 1:
        next_slots: list[int | None] = []
        for i in range(0, len(slots), 2):
            a, b = slots[i], slots[i + 1]
            if a is None:
                next_slots.append(b)
                continue
            if b is None:
                next_slots.append(a)
                continue

            n_matches += 1
            a_wins = simulate_match(ratings[a], ratings[b], rng)
            winner, loser = (a, b) if a_wins else (b, a)
            if winner > loser:  # größerer Setzplatz = schwächer gesetzt
                n_upsets += 1
            if {a, b} == {1, 2} and len(slots) > 2:
                top2_met_before_final = True
            elimination_round[loser] = round_number
            next_slots.append(winner)
        slots = next_slots
        rounds.append(tuple(slots))
        round_number += 1

    return TournamentResult(
        champion=slots[0],
        n_matches=n_matches,
        n_upsets=n_upsets,
        top2_met_before_final=top2_met_before_final,
        elimination_round=elimination_round,
        rounds=tuple(rounds),
    )


@dataclass(frozen=True)
class PolicyStats:
    p_top_seed_wins: float
    p_top2_meet_before_final: float
    upset_rate: float
    mean_elimination_round_seed1: float
    n_reps: int


def monte_carlo_compare(players: list[Player], n_reps: int, seed: int) -> dict[str, PolicyStats]:
    n_rounds_total = 0
    size = 1
    while size < len(players):
        size *= 2
    tmp = size
    while tmp > 1:
        tmp //= 2
        n_rounds_total += 1

    result: dict[str, PolicyStats] = {}
    for policy in ("seeded", "random"):
        champ_wins = 0
        top2_meets = 0
        total_upsets = 0
        total_matches = 0
        elim_rounds_seed1 = []
        for i in range(n_reps):
            rng = random.Random(seed * 1_000_003 + i)
            r = simulate_tournament(players, policy, rng)
            if r.champion == 1:
                champ_wins += 1
                elim_rounds_seed1.append(n_rounds_total + 1)  # gewinnt das Finale = "scheidet" nie aus
            else:
                elim_rounds_seed1.append(r.elimination_round.get(1, 0))
            if r.top2_met_before_final:
                top2_meets += 1
            total_upsets += r.n_upsets
            total_matches += r.n_matches

        result[policy] = PolicyStats(
            p_top_seed_wins=champ_wins / n_reps,
            p_top2_meet_before_final=top2_meets / n_reps,
            upset_rate=total_upsets / total_matches,
            mean_elimination_round_seed1=sum(elim_rounds_seed1) / len(elim_rounds_seed1),
            n_reps=n_reps,
        )
    return result
