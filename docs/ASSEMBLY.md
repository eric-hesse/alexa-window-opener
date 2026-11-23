# Build guide – v4 (compact housing)

> 🇩🇪 German version: [ANLEITUNG.md](ANLEITUNG.md)

**Motor:** JGA25-370 (6 V, 35 rpm, with encoder), pinion directly on the shaft
**Electronics:** TB6612FNG motor driver, ESP32 DevKit (30 pin, USB-C), small power rail
**Outer size:** 17.9 × 4.0 × 3.7 cm (including hook). Same height as the original, sticks out only 3.7 cm from the wall.

> ⚠️ The housing file and the hook/rack are based on the Cults3D model
> ["Automatic window open/close er"](https://cults3d.com/de/modell-3d/werkzeuge/automatic-window-open-close-er) (private-use license)
> and are therefore **not** included in this repository. Lid and pinion are in [`cad/`](../cad).

## What's new compared to v3

- The electronics lie flat on the floor of the housing with the pins pointing up, which makes the housing much flatter.
- Rounded corners and a rebated lid that slides into the walls, so there is no visible seam.
- No screw towers and no holes for the wall screws in the lid: the 3 wall screws sit at the top of the back wall and go in **before** the lid. From outside you only see the 5 small lid screws.
- The USB cable exits at the bottom of the rear end.

## Printing (Bambu Lab P1S, Prusament ASA, enclosure closed)

| File | Orientation | Settings |
|---|---|---|
| Housing (`01_gehaeuse_v4.stl`) | Back wall on the bed (already oriented) | 0.2 mm layers, 4 walls, 25 % infill, **no supports**, 5 mm brim (ASA warps on long parts) |
| [`cad/deckel.stl`](../cad/deckel.stl) – lid | Outside face on the bed | No supports, 3 mm brim |
| [`cad/ritzel_D4.stl`](../cad/ritzel_D4.stl) – pinion | as is | 0.12 mm layers, 100 % infill, no supports |
| [`cad/ritzel_D4_enger.stl`](../cad/ritzel_D4_enger.stl) – pinion, tighter bore | as is | Print both pinions and use the one that slides onto the shaft with light pressure |

## Parts you need

- 2× M3 × 6 (cheese or pan head) for the motor – **not longer than 6 mm** (or cut two M3 × 10 down to 6 mm)
- 5× M3 × 10 for the lid
- 3× countersunk wood screws 5 × 50 TX25 + 3× wall plugs 6/40
- Double-sided mounting tape (e.g. tesa Powerbond), superglue, cable ties (optional)
- TX25 screwdriver (the slot for the screw head is 10.5 mm wide)

## Assembly

1. **Insert the motor** from the open side. The shaft slides through the slot in the front plate and the round gearbox face sits flat against it. The two threaded holes must line up with the holes in the front plate (top and bottom). If the motor cable points to the back wall or down, turn the motor 180° so it points up or to the front.
2. **Screw the motor** to the front plate from outside with 2× M3 × 6. Tight, but not brutal.
3. **Pinion:** test it dry first (flat side of the shaft to the flat side of the bore). Then put **one** drop of superglue at the back of the bore, push the pinion on and clamp a double-folded strip of paper between pinion and front plate as a spacer. Let it dry for 10 minutes, then remove the paper.
4. **Electronics** – plug in all wires first, then stick the boards in place (see [wiring diagram](wiring.svg)):
   - **TB6612:** chip side **down**, mounting tape on the chip, press it into the shallow recess right behind the motor (against the back wall).
   - **Power rail:** next to it, at the front of the open side (mounting tape).
   - **ESP32:** side with the metal shield **down**, pins pointing up, USB socket towards the rear end. Tape on the metal shield. Plug in the USB cable first and route it through the notch at the bottom of the rear end. Push the ESP against the rib on the back wall and the end wall, then press it onto its base.
   - Store spare cable length above the ESP, there is room for it.
5. **Mount on the wall:**
   - Hold the housing in place and mark the 3 holes at the top of the back wall with a pencil (push the cables aside briefly). Spacing: hole 1 to hole 2 = 47 mm, hole 2 to hole 3 = 43 mm, all on one line 6.5 mm below the top edge.
   - Drill 6 mm holes and insert the wall plugs.
   - Hold the housing against the wall and drive the 3 screws in from the front through the slots.
   - **Important:** pinion and hook must stick out freely beyond the edge of the wall, because the rack runs past behind the wall surface. The wall edge has to lie between the front plate and about 2.4 cm behind it – the same area as on the original.
6. **Lid:** put the rear end on first so the tongue slides into the USB notch, then the front tongue into the shaft slot, and press the lid on (the rebate slides inside). Fasten with 5× M3 × 10.
7. Insert the **rack** between pinion and hook, as on the original.

## Notes

- The BOOT button on the ESP faces down and can't be reached – you don't need it: updates run over Wi-Fi at `fenster.local/update`, and the Wi-Fi reset will be on the web page.
- The power rail has a 20 × 10 mm spot. If yours is wider than 10 mm, the housing needs a small change.
- The motor is stronger than necessary. The firmware will limit the force and stop on a stall, otherwise gear teeth can break.
- Measure the motor before printing (front hole spacing 17 mm, shaft about 12 mm, gearbox Ø 25 mm). If something differs, the housing has to be adjusted.

## Technical data

- Pinion: 13 teeth, matching the original rack (pitch 3.2 mm), in the same position as on the original
- About 19 mm/s at the rack (at 5 V from USB) → 15 cm of travel in about 8 seconds
- Distance of the pinion axis from the wall: 14 mm, as on the original
