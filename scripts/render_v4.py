import pickle, sys, numpy as np, trimesh
from raster import render
import build_v4 as B

A = pickle.load(open("assembly_v4.pkl", "rb"))
C = dict(tub=(206, 210, 216), lid=(226, 229, 233), pinion=(214, 92, 60), motor=(150, 155, 165),
         esp=(40, 70, 150), usb_plug=(55, 55, 58), tb6612=(170, 40, 120), rail=(245, 245, 240),
         m3x6=(80, 80, 80))
O = B.O
which = sys.argv[1:] or ["zu", "innen", "explo", "hinten"]

def mv(m, d):
    t = m.copy(); t.apply_translation(d); return t

if "zu" in which:
    items = [(A["tub"], C["tub"]), (A["lid"], C["lid"]), (A["pinion"], C["pinion"]), (A["usb_plug"], C["usb_plug"])]
    im = render(items, view_dir=(0.55, -1.0, -0.55), up=(0, 0, 1), size=(1600, 900),
                title="Fertig: 17,9 x 4,0 x 3,7 cm (mit Haken)")
    im.save("v4_1_fertig.png")

if "innen" in which:
    lab = [("Ritzel", (-37, O[0] + 7, O[1] + 4), (-60, -200)),
           ("Motor JGA25-370", (8, O[0] + 12, O[1] + 3), (-80, -260)),
           ("TB6612 (Chip nach unten)", (63, 12, -20), (60, 260)),
           ("Stromschiene", (63, 29, -29), (-60, 300)),
           ("ESP32 (Stifte nach oben)", (100, 18, -30), (-80, 230)),
           ("USB-Kabel", (140, 18, -33.5), (20, -200)),
           ("Wandschraube 1", (16, 3.6, -6.5), (-60, -230)),
           ("Wandschraube 2", (63, 3.6, -6.5), (-60, -230)),
           ("Wandschraube 3", (106, 3.6, -6.5), (-60, -230))]
    tclip = B.to_trimesh(B.build_tub() - B.box(-26.9, B.X_EW0 - 0.1, 1.0, 50, -2.0, 1))
    items = [(tclip, C["tub"])] + [(A[k], C[k]) for k in ("pinion", "motor", "esp", "usb_plug", "tb6612", "rail")]
    im = render(items, view_dir=(0.12, -1.0, -0.42), up=(0, 0, 1), size=(1700, 1050), labels=lab,
                title="Innen (Deckel ab, obere Wand im Bild weggeschnitten)")
    im.save("v4_2_innen.png")

if "explo" in which:
    items = [(A["tub"], C["tub"]), (mv(A["lid"], (0, 120, 0)), C["lid"]),
             (mv(A["pinion"], (-30, 0, 0)), C["pinion"]), (mv(A["m3x6"], (-48, 0, 0)), C["m3x6"]),
             (mv(A["motor"], (0, 35, 0)), C["motor"]),
             (mv(A["esp"], (0, 60, 0)), C["esp"]), (mv(A["tb6612"], (0, 60, 0)), C["tb6612"]),
             (mv(A["rail"], (0, 60, 0)), C["rail"])]
    lab = [("1. Motor von vorne einlegen", (20, O[0] + 47, O[1] + 12), (80, -60)),
           ("2. 2x M3 x 6 von vorne", (-80, O[0], O[1] + 8.5), (-260, -150)),
           ("3. Ritzel aufkleben", (-67, O[0] + 7, O[1] - 6), (-200, 140)),
           ("4. Elektronik einkleben", (100, 78, -20), (60, -120)),
           ("5. Deckel drauf, 5x M3 x 10", (40, 156, -20), (40, -90))]
    im = render(items, view_dir=(0.3, -1.0, -1.1), up=(0, 0, 1), size=(1700, 1200), labels=lab,
                title="Zusammenbau")
    im.save("v4_3_zusammenbau.png")

if "hinten" in which:
    lab = [("Wandschraube 1", (16, -1, -6.5), (-120, -110)),
           ("Wandschraube 2", (63, -1, -6.5), (-60, -120)),
           ("Wandschraube 3", (106, -1, -6.5), (40, -110)),
           ("Mauerkante muss im blauen Bereich liegen", (-20, -1.5, -30), (-80, 150))]
    zone = trimesh.creation.box(extents=[24, 0.4, 40]); zone.apply_translation([-20, -1.3, -20])
    items = [(A["tub"], C["tub"]), (A["pinion"], C["pinion"]), (zone, (120, 170, 230))]
    im = render(items, view_dir=(0.35, 1.0, -0.3), up=(0, 0, 1), size=(1600, 800), labels=lab,
                title="Rueckseite (liegt an der Wand)")
    im.save("v4_4_rueckseite.png")
