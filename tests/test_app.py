"""Rauchtests der Streamlit-Oberfläche per AppTest: Standard, jedes Preset, Randgrößen, Politik-Wechsel."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import bs_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    if setup is not None:
        setup(at)
        at.run()
        assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Setzliste gegen Zufallslosung" in h.value for h in at.markdown)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders(name):
    p = C.PRESETS[name]

    def setup(at):
        at.session_state["n_players_slider"] = p["n_players"]
        at.session_state["rating_spread_slider"] = p["rating_spread"]
        at.session_state["seed_input"] = p["seed"]

    _run(setup)


def test_extreme_settings_render():
    def small(at):
        at.session_state["n_players_slider"] = C.N_PLAYERS_MIN
        at.session_state["rating_spread_slider"] = C.RATING_SPREAD_MIN

    _run(small)

    def large(at):
        at.session_state["n_players_slider"] = C.N_PLAYERS_MAX
        at.session_state["rating_spread_slider"] = C.RATING_SPREAD_MAX

    _run(large)


def test_odd_player_count_renders():
    def setup(at):
        at.session_state["n_players_slider"] = 10

    _run(setup)


def test_random_live_policy_renders():
    def setup(at):
        at.session_state["live_policy_radio"] = "random"

    _run(setup)


def test_resimulate_button_changes_live_seed():
    at = _run()
    assert at.session_state.get("live_seed", 0) == 0
    resim_button = next(b for b in at.button if "Neu simulieren" in (b.label or ""))
    resim_button.click().run()
    assert not at.exception
    assert at.session_state["live_seed"] == 1


def test_upset_rate_sentence_follows_the_measured_direction():
    # Mit Freilosen (10 Spieler, Streuung 300) steigt die Überraschungsrate unter der Setzliste (exakt gerechnet in
    # test_oracle_bracket.py); der Text darf dann nicht "sinkt um -x" sagen.
    def setup(at):
        at.session_state["n_players_slider"] = 10
        at.session_state["rating_spread_slider"] = 300.0

    at = _run(setup)
    text = " ".join(m.value for m in at.markdown)
    assert "Überraschungsrate\n  steigt um" in text
    assert "sinkt um **-" not in text
