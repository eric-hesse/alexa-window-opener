# Bauanleitung – v4 (kompaktes Gehäuse)

> 🇬🇧 English version: [ASSEMBLY.md](ASSEMBLY.md)

**Motor:** JGA25-370 (6 V, 35 U/min, mit Encoder), Ritzel direkt auf der Welle
**Elektronik:** Motortreiber TB6612FNG, ESP32 DevKit (30 Pin, USB-C), Stück Stromschiene
**Außenmaße:** 17,9 × 4,0 × 3,7 cm (mit Haken). Gleich hoch wie das Original, steht nur 3,7 cm von der Wand ab.

> ⚠️ Die Gehäusedatei sowie Haken und Zahnstange basieren auf dem Cults3D-Modell
> ["Automatic window open/close er"](https://cults3d.com/de/modell-3d/werkzeuge/automatic-window-open-close-er) (Private-Use-Lizenz)
> und sind deshalb **nicht** in diesem Repository. Deckel und Ritzel liegen in [`cad/`](../cad).

## Was neu ist gegenüber v3

- Die Elektronik liegt flach auf dem Boden, die Stifte zeigen nach oben – dadurch viel flacher.
- Runde Ecken, Deckel mit Falz (rutscht innen in die Wand, keine sichtbare Fuge).
- Keine Schraubtürme und keine Löcher für die Wandschrauben im Deckel: Die 3 Wandschrauben sitzen oben in der Rückwand und werden **vor** dem Deckel eingedreht. Von außen sieht man nur die 5 kleinen Deckelschrauben.
- Das USB-Kabel kommt hinten unten aus der Stirnseite.

## Drucken (Bambu Lab P1S, Prusament ASA, Druckerhaube zu)

| Datei | Lage | Einstellungen |
|---|---|---|
| Gehäuse (`01_gehaeuse_v4.stl`) | Rückwand auf dem Druckbett (liegt schon richtig) | 0,2 mm Schicht, 4 Wände, 25 % Füllung, **keine Stützen**, Brim 5 mm (ASA verzieht sich bei langen Teilen) |
| [`cad/deckel.stl`](../cad/deckel.stl) – Deckel | Außenseite auf dem Druckbett | Keine Stützen, Brim 3 mm |
| [`cad/ritzel_D4.stl`](../cad/ritzel_D4.stl) – Ritzel | wie sie ist | 0,12 mm Schicht, 100 % Füllung, keine Stützen |
| [`cad/ritzel_D4_enger.stl`](../cad/ritzel_D4_enger.stl) – Ritzel, engere Bohrung | wie sie ist | Beide Ritzel drucken und das nehmen, das mit leichtem Druck auf die Welle geht |

## Das brauchst du

- 2× M3 × 6 (Zylinder- oder Linsenkopf) für den Motor – **nicht länger als 6 mm** (oder zwei M3 × 10 auf 6 mm kürzen)
- 5× M3 × 10 für den Deckel
- 3× Holzschraube 5 × 50 Senkkopf TX25 + 3× Dübel 6/40
- tesa Powerbond, Sekundenkleber, Kabelbinder (optional)
- Schraubendreher TX25 (der Schacht für den Schraubenkopf ist 10,5 mm breit)

## Zusammenbau

1. **Motor einlegen:** von vorne (offene Seite) rein, die Welle rutscht durch den Schlitz in der Frontplatte, die runde Getriebe-Stirnseite liegt flach an. Die 2 Gewindelöcher müssen oben und unten hinter den Löchern der Frontplatte sitzen. Zeigt das Motorkabel zur Rückwand oder nach unten, den Motor um 180° drehen – dann zeigt es nach oben oder vorne.
2. **Motor festschrauben:** 2× M3 × 6 von außen durch die Frontplatte in den Motor. Fest, nicht brutal.
3. **Ritzel:** erst trocken probieren (flache Seite der Welle an die flache Seite der Bohrung). Dann **einen** Tropfen Sekundenkleber hinten in die Bohrung, aufschieben und dabei einen doppelt gefalteten Papierstreifen als Abstandshalter zwischen Ritzel und Frontplatte klemmen. 10 Minuten trocknen lassen, Papier raus.
4. **Elektronik** – erst alle Kabel aufstecken, dann einkleben (siehe [Schaltplan](wiring.svg)):
   - **TB6612:** Chip-Seite nach **unten**, Powerbond auf den Chip, in die flache Mulde direkt hinter dem Motor (an der Rückwand) drücken.
   - **Stromschiene:** daneben, vorne an der offenen Seite (Powerbond).
   - **ESP32:** Seite mit der Metallkappe nach **unten**, Stifte zeigen nach oben, USB-Buchse zur Stirnseite hinten. Powerbond auf die Metallkappe. Zuerst das USB-Kabel einstecken und unten durch die Kerbe in der Stirnseite führen. Den ESP an die Leiste an der Rückwand und an die Stirnwand schieben, dann auf den Sockel drücken.
   - Kabelreste oben über dem ESP verstauen, dort ist Platz.
5. **An die Wand:**
   - Gehäuse an die Stelle halten und mit einem Bleistift durch die 3 Löcher oben in der Rückwand anzeichnen (Kabel kurz zur Seite drücken). Abstand: Loch 1 bis Loch 2 = 47 mm, Loch 2 bis Loch 3 = 43 mm, alle auf einer Linie 6,5 mm unter der Oberkante.
   - 6-mm-Löcher bohren, Dübel rein.
   - Gehäuse anhalten und die 3 Schrauben von vorne durch die Schächte eindrehen.
   - **Wichtig:** Ritzel und Haken müssen frei über die Mauerkante ragen, weil die Zahnstange dort hinter der Wandfläche vorbeiläuft. Die Mauerkante muss zwischen der Frontplatte und ca. 2,4 cm dahinter liegen – derselbe Bereich wie beim Original.
6. **Deckel:** hinten zuerst ansetzen, damit die Zunge in die USB-Kerbe rutscht, dann vorne die Zunge in den Wellenschlitz, Deckel andrücken (der Falz rutscht innen rein). 5× M3 × 10.
7. **Zahnstange** wie beim Original zwischen Ritzel und Haken einsetzen.

## Hinweise

- Der BOOT-Knopf am ESP zeigt nach unten und ist nicht erreichbar – den brauchst du nicht: Updates laufen über WLAN unter `fenster.local/update`, der WLAN-Reset kommt auf die Webseite.
- Platz für die Stromschiene: 20 × 10 mm. Ist dein Stück breiter als 10 mm, muss das Gehäuse leicht angepasst werden.
- Der Motor ist stärker als nötig. Die Firmware wird die Kraft begrenzen und bei Blockade stoppen, sonst brechen Zähne.
- Vor dem Drucken den Motor nachmessen (Lochabstand vorne 17 mm, Welle ca. 12 mm, Getriebe Ø 25 mm). Weicht etwas ab, muss das Gehäuse angepasst werden.

## Technische Daten

- Ritzel: 13 Zähne, passend zur Original-Zahnstange (Teilung 3,2 mm), gleiche Position wie beim Original
- Ca. 19 mm/s an der Zahnstange (bei 5 V aus USB) → 15 cm Weg in ca. 8 Sekunden
- Wandabstand der Ritzelachse: 14 mm wie beim Original
