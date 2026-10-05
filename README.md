# K.-o.-System und Setzliste (Bracket-Seeding) – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-bracket-seeding-demo.streamlit.app/)**

Zweites Stück der **Turnierplanung-Linie** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations
Research und Machine Learning". Ein **K.-o.-Turnier** braucht nur ⌈log₂ n⌉ Runden bis zum Sieger, statt der
n−1 Runden eines Rundenturniers (Stück 1 dieser Linie) – dafür scheidet aus, wer einmal verliert. Die
**Setzliste** ist der Standard-Algorithmus (Tennis-Grand-Slams, NCAA, der **FIDE World Cup** mit seinem
256er-K.-o.-Baum), der die stärksten Teilnehmer im Turnierbaum so verteilt, dass sie sich frühestens im
**Finale** treffen können. Diese Demo baut die Setzliste exakt nach diesem Standard und misst per Monte-Carlo-
Simulation (Elo-Erwartungswert je Partie), was sie wirklich bringt – strukturell und in Zahlen.

Die Linie:

```
Rundenturnier (Stück 1, gebaut+gepusht+deployed)
 ├─ K.-o.-System + Setzliste (dieses Stück)
 └─ Schweizer System (FIDE-Dutch-Regelwerk, volle C1-C21-Kriterienhierarchie)   [gebaut: schweizer-system-demo]
```

## Ergebnis (Zahlen aus den Tests)

| Frage | Ergebnis |
|---|---|
| Stimmt die Setzliste mit der öffentlich bekannten Standardtafel überein? | ✅ Für 16 Plätze exakt `[1,16,8,9,4,13,5,12,2,15,7,10,3,14,6,11]` – dieselbe Reihenfolge wie z. B. Tennis-Grand-Slam-Raster. |
| Treffen sich Setzplatz 1 und 2 je vor dem Finale? | ✅ **Strukturell nie** unter der Setzliste (bewiesen über die Halbierungs-Eigenschaft, für n = 4…64 getestet) – bei zufälliger Auslosung dagegen in 7–45 % der Turniere (Messraster n = 4, 8, 10, 16, 20, 32 × Rating-Streuung 0…500, Zufalls-Seed 1, 4.000 Wiederholungen): selten bei großem Feld mit gleich starken Spielern, oft bei klaren Favoriten. |
| Wie werden Freilose bei Nicht-Zweierpotenz verteilt? | ✅ Automatisch die obersten Setzplätze (kein Sonderfall nötig) – bei 10 Spielern exakt die Plätze 1–6, deckungsgleich mit dem realen FIDE-World-Cup-Muster (oberste Gesetzte bekommen ein Freilos in Runde 2). |
| Erhöht Setzung die Siegchance des Favoriten? | ⚠️ Ja, aber **moderat**: im selben Messraster bei Streuung 50…300 zwischen +0,3 und +4,6 Prozentpunkten (4.000 Wiederholungen je Politik, Monte-Carlo-Streuung eines Unterschieds etwa 1 Prozentpunkt), bei Streuung 0 oder 500 teils um null oder knapp darunter – kein dramatischer Sprung. |
| Sinkt die Gesamt-Überraschungsrate durch Setzung? | ⚠️ **Nur bei Zweierpotenz-Feldern** (n = 4, 8, 16, 32 im Messraster, Streuung 50…300): sinkt um 0,8 bis 4,4 Prozentpunkte. Bei Feldern mit Freilosen (n = 10, 20) **steigt** sie dagegen um 0,5 bis 6,1 Prozentpunkte – ursprünglich als Invarianz vermutet, dann widerlegt. |

## Was die Demo zeigt

- **Ein simuliertes Turnier**: kompletter Turnierbaum mit Live-Ergebnis, Politik umschaltbar (gesetzt/zufällig),
  ▶️ „Neu simulieren“ für einen neuen Zufallslauf. Orange Kanten markieren Überraschungen, orange Knoten
  Setzplatz 1 und 2, gold den Sieger.
- **Setzliste gegen Zufallslosung**: Balkenvergleich über drei Kennzahlen (P(Favorit gewinnt), P(Setzplatz 1&2
  vor dem Finale), Überraschungsrate), aus 4.000 Monte-Carlo-Wiederholungen je Politik.
- **Presets**: kleines Turnier (8), ungerade Teilnehmerzahl mit Freilosen (10), eng gestaffeltes Feld, stark
  gestaffeltes Feld.

## Was diese Demo (ehrlich) zeigt und was nicht

Die Setzliste ist eine **strukturelle** Garantie (WER auf WEN trifft), keine Garantie für das Ergebnis selbst:
sie ändert keine einzelne Elo-Gewinnwahrscheinlichkeit. Der ursprünglich vermutete Befund "Überraschungsrate ist
zwischen beiden Politiken exakt gleich" hat sich bei der Messung **nicht bestätigt**. Bei Zweierpotenz-Feldern senkt
Setzung die Gesamt-Überraschungsrate leicht, weil sie früh systematisch Favorit-gegen-Außenseiter-Paarungen erzeugt
statt zufällig verteilter Rating-Gefälle. Bei Feldern mit Freilosen kehrt sich das um: die obersten Gesetzten
überspringen die leichten Runde-1-Partien, übrig bleiben Partien zwischen ähnlich stark gesetzten Spielern (bei
10 Spielern und Streuung 300: 2 Runde-1-Partien mit im Schnitt 0,70 Überraschungen gegenüber 3 Partien mit 0,55
bei zufälliger Auslosung). Die Überraschungsrate ist hier die Zahl der Siege des schlechter gesetzten Spielers je Partie;
sie sagt nichts darüber, ob der Favorit häufiger gewinnt. Dieser Fund steht so in Code und Tests, nicht schöngerechnet.

## Modell und Verfahren

- **Setzlisten-Rekursion** (`bs_bracket.py`): `seeds=[1]`, dann wiederholt `s → (s, 2·len(seeds)+1−s)`, bis die
  volle Feldgröße erreicht ist. Garantiert per Konstruktion: Setzplätze 1…2ʲ liegen für jedes j immer
  vollständig in verschiedenen 2^(k−j)-Blöcken.
- **Freilose**: `next_pow2 = kleinste Zweierpotenz ≥ n`; Setzplätze > n sind Phantome, ein echter Spieler gegen
  ein Phantom rückt automatisch vor.
- **Elo-Erwartungswert** (`bs_elo.py`, Arpad Elo/USCF/FIDE-Standard): $E_A = 1/(1+10^{(R_B-R_A)/400})$.
- **Turniersimulation & Monte-Carlo-Vergleich** (`bs_evaluation.py`): spielt den ganzen Baum durch, vergleicht
  Politik "gesetzt" gegen "zufällig" über viele Wiederholungen.
- **Quellen**: [handbook.fide.com](https://handbook.fide.com) (FIDE World Cup, Freilos-Muster),
  [en.wikipedia.org/wiki/Seeding_(sports)](https://en.wikipedia.org/wiki/Seeding_(sports)) (Summeneigenschaft
  je Runde, unabhängige Bestätigung der Setzlisten-Konstruktion).

## Verifikation

- **Gegen die öffentlich bekannte Standardtafel**: `tests/test_bracket.py` vergleicht die 16er-Setzliste exakt.
- **Eigenschaftstests** über n = 2…64: Permutationseigenschaft, Summeneigenschaft je Runde, Setzplatz 1&2 nie vor
  dem Finale, oberste vier Setzplätze in vier verschiedenen Vierteln, Freilos-Zuordnung bei Nicht-Zweierpotenz,
  kein Match mit zwei Phantomen gleichzeitig.
- **Elo-Referenzwerte**: 0/200/400-Punkte-Differenzen gegen bekannte Richtwerte, Symmetrie, Simulationsrate
  gegen den Erwartungswert über 20.000 Läufe.
- **Monte-Carlo-Vergleich**: Richtung der gemessenen Effekte (nicht harte Gleichheiten, plattform-robust).
- **Streamlit-Rauchtests** (`tests/test_app.py`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-Oberfläche |
| `bs_constants.py` | Regler-Grenzen, Presets |
| `bs_presets.py` | Permalink- und Preset-Logik |
| `bs_scenario.py` | Spielerfeld generieren (Ratings, Setzplätze) |
| `bs_bracket.py` | Setzlisten-Algorithmus, Freilos-Ableitung |
| `bs_elo.py` | Elo-Erwartungswert, Partie-Simulation |
| `bs_evaluation.py` | Turniersimulation, Monte-Carlo-Vergleich |
| `bs_visualization.py` | Plotly: Turnierbaum, Politik-Vergleich |
| `tests/` | Standardtafel-Abgleich, Eigenschaftstests, Elo-Referenzwerte, Monte-Carlo, Rauchtests |

## Lokal starten

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\streamlit run app.py
```

## Tests ausführen

```bash
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\python -m pytest tests -v
```

Die CI (`.github/workflows/tests.yml`) läuft auf Ubuntu mit Python 3.12, bei jedem Push und wöchentlich mit den
jeweils neuesten Bibliotheksversionen.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html).
