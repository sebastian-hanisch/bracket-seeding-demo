"""Plotly-Visualisierungen: Turnierbaum eines simulierten Laufs und der Politik-Vergleich (gesetzt/zufällig).
Alle Figuren laufen durch `lock_axes` (Touch-Scrolling-Konvention des Portfolios)."""

from __future__ import annotations

import plotly.graph_objects as go

from bs_evaluation import PolicyStats, TournamentResult

BLUE = "#1f77b4"
ORANGE = "#d68a2e"
GOLD = "#e8b923"
GRAY = "#8a8f98"
NAVY = "#14233B"
GREEN = "#2ca02c"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_bracket_tree(result: TournamentResult) -> go.Figure:
    rounds = result.rounds
    positions: list[list[float]] = [list(range(len(rounds[0])))]
    for r in range(1, len(rounds)):
        prev = positions[r - 1]
        positions.append([(prev[2 * i] + prev[2 * i + 1]) / 2 for i in range(len(rounds[r]))])

    fig = go.Figure()

    for r in range(len(rounds) - 1):
        for i, winner in enumerate(rounds[r + 1]):
            y_next = positions[r + 1][i]
            children = [j for j in (2 * i, 2 * i + 1) if j < len(rounds[r])]
            real_child_seeds = [rounds[r][j] for j in children if rounds[r][j] is not None]
            is_real_match = len(real_child_seeds) == 2
            is_upset = False
            if is_real_match and winner is not None:
                loser = real_child_seeds[0] if real_child_seeds[1] == winner else real_child_seeds[1]
                is_upset = winner > loser
            for j in children:
                if rounds[r][j] is None:
                    continue
                line_color = ORANGE if is_upset else GRAY
                fig.add_trace(
                    go.Scatter(
                        x=[r, r + 1],
                        y=[positions[r][j], y_next],
                        mode="lines",
                        line=dict(color=line_color, width=2),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

    for r in range(len(rounds)):
        for i, seed in enumerate(rounds[r]):
            if seed is None:
                continue
            is_champion = r == len(rounds) - 1
            is_top2 = seed in (1, 2)
            color = GOLD if is_champion else (ORANGE if is_top2 else BLUE)
            fig.add_trace(
                go.Scatter(
                    x=[r],
                    y=[positions[r][i]],
                    mode="markers+text",
                    text=[str(seed)],
                    textposition="middle center",
                    textfont=dict(color="white", size=11),
                    marker=dict(size=26, color=color, line=dict(width=2, color="white")),
                    hovertext=f"Setzplatz {seed}" + (" (Sieger)" if is_champion else ""),
                    hoverinfo="text",
                    showlegend=False,
                )
            )

    n_rounds = len(rounds) - 1
    round_labels = [f"R{r + 1}" for r in range(n_rounds)] + ["Sieger"]
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(rounds))), ticktext=round_labels)
    fig.update_yaxes(visible=False, autorange="reversed")
    fig.update_layout(
        template="plotly_white",
        height=max(360, 24 * len(rounds[0])),
        margin=dict(l=10, r=10, t=10, b=30),
    )
    return lock_axes(fig)


def build_policy_comparison_chart(stats: dict[str, PolicyStats]) -> go.Figure:
    seeded, rand = stats["seeded"], stats["random"]
    metrics = ["P(Favorit gewinnt)", "P(Setzplatz 1&2 vor dem Finale)", "Überraschungsrate"]
    seeded_vals = [seeded.p_top_seed_wins, seeded.p_top2_meet_before_final, seeded.upset_rate]
    random_vals = [rand.p_top_seed_wins, rand.p_top2_meet_before_final, rand.upset_rate]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Gesetzt", x=metrics, y=seeded_vals, marker_color=ORANGE, text=[f"{v * 100:.1f} %" for v in seeded_vals], textposition="outside"))
    fig.add_trace(go.Bar(name="Zufällig", x=metrics, y=random_vals, marker_color=GRAY, text=[f"{v * 100:.1f} %" for v in random_vals], textposition="outside"))
    fig.update_yaxes(title="Anteil", tickformat=".0%", rangemode="tozero", fixedrange=True)
    fig.update_xaxes(fixedrange=True)
    fig.update_layout(
        template="plotly_white",
        barmode="group",
        height=380,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig
