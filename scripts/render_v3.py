import pickle, numpy as np, trimesh
from raster import render
import build_v3 as B

A = pickle.load(open("assembly_v3.pkl", "rb"))
C = dict(tub=(235, 120, 40), lid=(235, 150, 80), pinion=(200, 40, 40), motor=(150, 155, 165),
         esp=(30, 60, 140), usb_plug=(60, 60, 60), tb6612=(200, 30, 120), rail=(240, 240, 240), m3x6=(90, 90, 90))
O = B.O
lab_in = [
    ("Ritzel (aufgeklebt)", (-37, O[0] + 8, O[1]), (-140, -150)),
    ("Motor JGA25-370", (10, O[0] + 12, O[1] + 4), (60, -230)),
    ("Platz fuer Motorkabel", (38, O[0] + 14, O[1] + 4), (-20, -250)),
    ("TB6612 (in den Rahmen)", (61, 7, -12), (-60, -220)),
    ("Stromschiene", (61, 12, -35), (-120, 150)),
    ("ESP32 (USB nach unten)", (90, 13, -20), (40, -260)),
    ("USB-Kabel raus", (90, 6, -60), (60, 90)),
    ("Wandschraube 1", (4, 44, -46.5), (-200, 90)),
    ("Wandschraube 2+3", (113.5, 44, -12), (-80, -200)),
]
tclip = B.to_trimesh(B.build_tub() - B.box(-26.9, 123.4, 2.0, 50, -1.6, 1))
items = [(tclip, C["tub"])] + [(A[k], C[k]) for k in ("pinion", "motor", "esp", "usb_plug", "tb6612", "rail")]
im = render(items, view_dir=(-0.12, -1.0, -0.28), up=(0, 0, 1), size=(1600, 1000), labels=lab_in,
            title="Innen (ohne Deckel, obere Wand weggeschnitten)")
im.save("vorschau_1_innen.png")

# Front: Motorschrauben
lab_f = [("M3 x 6", (-32.5, O[0], O[1] + 8.5), (120, -200)),
         ("M3 x 6", (-32.5, O[0], O[1] - 8.5), (120, 120)),
         ("Schlitz: Welle von oben einlegen", (-32, O[0] + 25, O[1]), (90, -330)),
         ("Motorwelle (D-Form)", (-38, O[0], O[1]), (150, -20))]
items = [(A["tub"], C["tub"]), (A["motor"], C["motor"]), (A["m3x6"], C["m3x6"])]
im = render(items, view_dir=(1.0, -0.35, -0.3), up=(0, 0, 1), size=(1400, 950), labels=lab_f,
            title="Vorne: erst Motor anschrauben, dann Ritzel aufstecken")
im.save("vorschau_2_motor_vorne.png")

# Fertig
items = [(A["tub"], C["tub"]), (A["lid"], C["lid"]), (A["pinion"], C["pinion"]), (A["usb_plug"], C["usb_plug"])]
lab_z = [("6x M3 x 10 (Deckel)", (46, 47, -4.5), (40, -120)),
         ("Zugang Wandschrauben", (113.5, 47, -12), (40, -110))]
im = render(items, view_dir=(-0.4, -1.0, -0.5), up=(0, 0, 1), size=(1500, 900), labels=lab_z,
            title="Fertig  (ca. 17,5 x 5,5 x 4,8 cm)")
im.save("vorschau_3_fertig.png")
