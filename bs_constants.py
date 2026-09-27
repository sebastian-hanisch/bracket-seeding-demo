"""Regler-Grenzen, Presets und Konstanten für die K.-o.-Setzlisten-Demo."""

DEFAULT_N_PLAYERS = 16
N_PLAYERS_MIN, N_PLAYERS_MAX = 4, 32

DEFAULT_RATING_SPREAD = 150.0
RATING_SPREAD_MIN, RATING_SPREAD_MAX = 0.0, 500.0

DEFAULT_SEED = 1
DEFAULT_LIVE_POLICY = "seeded"

MONTE_CARLO_REPS = 4000

# --- Presets ---------------------------------------------------------------
_BASE = {"n_players": DEFAULT_N_PLAYERS, "rating_spread": DEFAULT_RATING_SPREAD, "seed": DEFAULT_SEED}
PRESETS = {
    "Kleines Turnier (8 Spieler)": {**_BASE, "n_players": 8},
    "Ungerade Teilnehmerzahl mit Freilosen (10 Spieler)": {**_BASE, "n_players": 10},
    "Eng gestaffeltes Feld (Ratings dicht beieinander)": {**_BASE, "rating_spread": 50.0},
    "Stark gestaffeltes Feld (klare Favoriten)": {**_BASE, "rating_spread": 400.0},
}
PRESET_HELP = {
    "Kleines Turnier (8 Spieler)": "8 Spieler, 3 Runden, keine Freilose - der einfachste Fall.",
    "Ungerade Teilnehmerzahl mit Freilosen (10 Spieler)": "10 Spieler brauchen ein 16er-Feld: die obersten 6 Setzplätze bekommen automatisch ein Freilos in Runde 2 - ohne Sonderregel, allein aus der Setzliste.",
    "Eng gestaffeltes Feld (Ratings dicht beieinander)": "Kleine Rating-Unterschiede: die Setzung bringt dem Favoriten kaum eine höhere Siegchance, verhindert aber trotzdem ein frühes Spitzenduell.",
    "Stark gestaffeltes Feld (klare Favoriten)": "Große Rating-Unterschiede: der Favorit gewinnt ohnehin fast immer - der Unterschied zwischen Setzung und Zufallslosung wird kleiner.",
}
