"""K.-o.-System und Setzliste (Bracket-Seeding) - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo EIN
Verfahren - die Standard-Setzliste für K.-o.-Turniere - an einem wachsenden Beispiel. Zweites Stück der
Turnierplanung-Linie der "Konzepte"-Reihe (siehe README für die Einordnung und Stück 1, Rundenturnier).

Lauffähig mit: streamlit run app.py
"""

import random

import streamlit as st

import bs_constants as C
from bs_evaluation import monte_carlo_compare, simulate_tournament
from bs_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from bs_scenario import generate_players
from bs_visualization import build_bracket_tree, build_policy_comparison_chart

st.set_page_config(page_title="K.-o.-Setzliste – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _players(n_players, rating_spread, seed):
    return generate_players(n_players, rating_spread, seed)


@st.cache_data(show_spinner="Turnier wird simuliert ...")
def _tournament(n_players, rating_spread, seed, policy, live_seed):
    players = _players(n_players, rating_spread, seed)
    rng = random.Random(live_seed)
    return simulate_tournament(players, policy, rng)


@st.cache_data(show_spinner="Monte-Carlo-Vergleich läuft (mehrere tausend Turniere) ...")
def _compare(n_players, rating_spread, seed):
    players = _players(n_players, rating_spread, seed)
    return monte_carlo_compare(players, n_reps=C.MONTE_CARLO_REPS, seed=seed)


st.title("🏆 K.-o.-System und Setzliste")
st.markdown(
    """
In einem **K.-o.-Turnier** ("Ausscheidungsturnier") scheidet aus, wer verliert - bei n Teilnehmern reichen
**⌈log₂ n⌉ Runden** bis zum Sieger, statt der n−1 Runden eines Rundenturniers. Damit sich die stärksten
Teilnehmer nicht schon in Runde 1 gegenseitig ausschalten, gibt es die **Setzliste**: ein Standard-Algorithmus
(überall in Turniersoftware verwendet, von Tennis-Grand-Slams bis zum **FIDE World Cup** mit seinem
256er-K.-o.-Baum) verteilt die Setzplätze so auf den Turnierbaum, dass Setzplatz 1 und 2 sich frühestens im
**Finale** treffen können.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren vergleichen, zeigt "
    "diese Demo - zweites Stück der Turnierplanung-Linie der \"Konzepte\"-Reihe - **ein** Verfahren an einem "
    "wachsenden Beispiel: die Setzliste ist eine strukturelle Garantie (WER auf WEN trifft), keine Garantie "
    "für das Ergebnis selbst - wie stark der Unterschied wirklich ist, misst diese Demo live."
)

with st.expander("So funktioniert die Setzliste", expanded=True):
    st.markdown(
        r"""
1. **Rekursive Verdopplung**: beginnend bei `[1]` wird die Liste wiederholt verdoppelt - jeder Setzplatz $s$
   bekommt einen Partner $m-s$ (wobei $m$ die neue Länge plus 1 ist), bis die volle Feldgröße erreicht ist. Für
   16 Plätze ergibt das `[1,16,8,9,4,13,5,12,2,15,7,10,3,14,6,11]` - dieselbe Reihenfolge, die z. B.
   Tennis-Grand-Slam-Raster verwenden.
2. **Garantie**: durch die Konstruktion liegen Setzplatz 1 und 2 immer in verschiedenen Hälften, 1-4 in
   verschiedenen Vierteln, und so weiter - sie können sich erst treffen, wenn ihre Hälfte/ihr Viertel/... im
   Turnierbaum zusammenläuft.
3. **Freilose ohne Sonderregel**: ist die Teilnehmerzahl keine Zweierpotenz, wird die nächstgrößere Feldgröße
   genommen und die überzähligen Plätze als "Phantome" behandelt - ein echter Spieler gegen ein Phantom rückt
   automatisch vor. Das erzeugt von selbst das reale Turniermuster (z. B. FIDE World Cup: die obersten
   50 Gesetzten bekommen ein Freilos in Runde 2).
4. **Was die Setzliste NICHT tut**: sie ändert keine einzelne Gewinnwahrscheinlichkeit - nur WER auf WEN und
   WANN trifft. Ob das die Siegchance des Favoriten am Ende trotzdem spürbar erhöht, misst der Vergleich unten.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_players = st.slider(
        "Teilnehmerzahl", *bounds("n_players_slider"), key="n_players_slider",
        help="Bei Nicht-Zweierpotenzen bekommen die obersten Setzplätze automatisch ein Freilos.",
    )
    rating_spread = st.slider(
        "Rating-Streuung", *bounds("rating_spread_slider"), key="rating_spread_slider", step=10.0,
        help="Standardabweichung der Elo-Ratings um 2000. 0 = alle gleich stark, groß = klare Favoriten.",
    )
    seed = st.number_input("Zufalls-Seed (Spielerfeld)", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Spielerfeld auslosen", width="stretch", on_click=randomize_seed, help="Würfelt ein neues Rating-Feld.")

    st.markdown("**Live-Turnierbaum**")
    live_policy = st.radio(
        "Politik", options=["seeded", "random"], key="live_policy_radio",
        format_func=lambda p: "Gesetzt (Setzliste)" if p == "seeded" else "Zufällige Auslosung",
    )

sync_query_params(n_players, rating_spread, seed)

n_players = int(n_players)
rating_spread = float(rating_spread)
seed = int(seed)

st.markdown("---")
st.markdown("## 🎯 Ein simuliertes Turnier")

sim_key = (n_players, rating_spread, seed, live_policy)
if "live_seed" not in st.session_state or st.session_state.get("sim_owner") != sim_key:
    st.session_state["live_seed"] = 0
    st.session_state["sim_owner"] = sim_key

sim_col, btn_col = st.columns([5, 1])
with btn_col:
    if st.button("🎲 Neu simulieren", width="stretch"):
        st.session_state["live_seed"] += 1

result = _tournament(n_players, rating_spread, seed, live_policy, st.session_state["live_seed"])
st.plotly_chart(build_bracket_tree(result), width="stretch", key=f"bracket_{sim_key}_{st.session_state['live_seed']}")
st.caption(
    f"Sieger: Setzplatz **{result.champion}**"
    + (" 🏆" if result.champion == 1 else "")
    + f" · {result.n_matches} Partien, davon {result.n_upsets} Überraschungen (Sieg des schwächer gesetzten Spielers)"
    + (" · Setzplatz 1 und 2 trafen sich vor dem Finale" if result.top2_met_before_final else " · Setzplatz 1 und 2 trafen sich nicht vor dem Finale")
    + ". Orange Verbindungslinien markieren eine Überraschung, orange Knoten sind Setzplatz 1 und 2, gold der Sieger."
)

st.markdown("---")
st.markdown("## 🎯 Setzliste gegen Zufallslosung: was ändert sich wirklich?")
st.caption(
    f"{C.MONTE_CARLO_REPS} simulierte Turniere je Politik, gleiches Spielerfeld, gleiche Elo-Erwartungswerte -"
    " nur die Zuordnung zum Turnierbaum unterscheidet sich."
)
stats = _compare(n_players, rating_spread, seed)
st.plotly_chart(build_policy_comparison_chart(stats), width="stretch", key="policy_comparison")

seeded, rand = stats["seeded"], stats["random"]
gap_win = (seeded.p_top_seed_wins - rand.p_top_seed_wins) * 100
gap_upset = (rand.upset_rate - seeded.upset_rate) * 100
upset_phrase = (
    f"sinkt um **{gap_upset:.1f} Prozentpunkte**" if gap_upset >= 0
    else f"steigt um **{-gap_upset:.1f} Prozentpunkte**"
)
win_phrase = (
    f"steigt durch die Setzung um **{gap_win:+.1f} Prozentpunkte**" if gap_win >= 0
    else f"sinkt durch die Setzung um **{-gap_win:.1f} Prozentpunkte**"
)
bye_note = (
    " Bei Nicht-Zweierpotenzen bekommen die obersten Gesetzten Freilose und überspringen die leichten"
    " Runde-1-Partien; übrig bleiben Partien zwischen ähnlich stark gesetzten Spielern mit vielen Überraschungen -"
    " deshalb kann die Überraschungsrate unter der Setzliste auch steigen."
    if n_players & (n_players - 1) else ""
)
st.markdown(
    f"""
- **Strukturell exakt**: unter der Setzliste treffen sich Setzplatz 1 und 2 **nie** vor dem Finale (bewiesen
  durch die Konstruktion, hier über {C.MONTE_CARLO_REPS} Läufe bestätigt: {seeded.p_top2_meet_before_final * 100:.0f} %)
  - bei zufälliger Auslosung dagegen in **{rand.p_top2_meet_before_final * 100:.0f} %** der Turniere.
- **Gemessen, moderat**: die Siegchance des Favoriten {win_phrase}
  ({seeded.p_top_seed_wins * 100:.1f} % gegen {rand.p_top_seed_wins * 100:.1f} %), die Gesamt-Überraschungsrate
  {upset_phrase}. Beides keine große Verschiebung; zur Einordnung: die Monte-Carlo-Streuung eines
  Unterschieds beträgt etwa 1 Prozentpunkt bei {C.MONTE_CARLO_REPS} Läufen je Politik - der Hauptbeitrag der Setzliste ist strukturell (WER auf WEN trifft),
  nicht eine große Verschiebung der Gesamtwahrscheinlichkeiten.{bye_note}
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Setzlisten-Rekursion.** Für eine Feldgröße $2^k$ wird die Reihenfolge rekursiv aus $[1]$ aufgebaut: bei
aktueller Länge $\ell$ wird jeder Eintrag $s$ zu $(s,\, 2\ell+1-s)$ - das verdoppelt die Länge und hält die
Summe je Paarung konstant ($2\ell+1$). Nach $k$ Schritten ist jede Paarung in Runde 1 eindeutig, und die
Konstruktion garantiert per Induktion: die Setzplätze $1,\dots,2^{j}$ liegen für jedes $j < k$ vollständig in
verschiedenen $2^{k-j}$-Blöcken - insbesondere 1 und 2 in verschiedenen Hälften.

**Freilose.** Bei $n$ Teilnehmern ohne Zweierpotenz sei $N = 2^{\lceil \log_2 n \rceil}$. Setzplätze $> n$ sind
Phantome; ein echter Spieler gegen ein Phantom erhält ein Freilos. Da $N/2 < n \le N$ (außer $n$ ist selbst eine
Zweierpotenz), gibt es nie zwei Phantome in derselben Partie.

**Elo-Erwartungswert** (Arpad Elo): $E_A = \dfrac{1}{1+10^{(R_B-R_A)/400}}$ - die Gewinnwahrscheinlichkeit von A
gegen B bei Ratingdifferenz $R_A - R_B$. Referenzwert: 200 Punkte Unterschied ≈ 76 % für den Favoriten.

**Invariante über beide Politiken.** Da jede Partie genau einen Spieler eliminiert, ist die Gesamtzahl der
Partien in JEDEM Turnier unabhängig von Politik und Freilosverteilung exakt $n-1$ (geprüft in
`tests/test_evaluation.py`).

Implementiert in `bs_bracket.py` (Setzliste, Freilose), `bs_elo.py` (Erwartungswert) und `bs_evaluation.py`
(Turniersimulation, Monte-Carlo-Vergleich).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html)."
)
