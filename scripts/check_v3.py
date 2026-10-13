import itertools, numpy as np, trimesh, pickle
import build_v3 as B

tub = B.build_tub(); lid = B.build_lid()
A = {"tub": tub, "lid": lid}
A["pinion"] = B.place_x(B.part_pinion(), B.X_PIN[0], *B.O)
A["motor"] = B.motor_model()
esp, plug = B.esp_model()
A["esp"] = esp; A["usb_plug"] = plug
A["tb6612"] = B.tb_model(); A["rail"] = B.rail_model()
# Schrauben M3x6 Zylinderkopf (Kopf 5,5 x 3) von vorne
scr = None
for dz in (+B.SCREW_R, -B.SCREW_R):
    s = B.cyl_x(2.75, B.X_PL[0] + 0.15, B.X_PL[0] + 3.0, B.O[0], B.O[1] + dz) + \
        B.cyl_x(1.45, B.X_PL[0] + 3.0, B.X_PL[0] + 3.0 + 6.0, B.O[0], B.O[1] + dz)
    scr = s if scr is None else scr + s
A["m3x6"] = scr
expected = {("m3x6", "motor"), ("motor", "pinion")}   # Schraube im Gewinde / Welle im Ritzel
bad = 0
for a, b in itertools.combinations(A, 2):
    v = (A[a] ^ A[b]).volume()
    if v > 1e-3:
        tag = "(gewollt)" if (a, b) in expected or (b, a) in expected else "<-- PROBLEM"
        bad += tag.startswith("<")
        print(f"{a:9s} x {b:9s}: {v:8.3f} mm3 {tag}")
print("Probleme:", bad)
# Schraubeneingriff im Motor
print("M3 Eingriff in Motor: %.2f mm (Gewinde 4,5 tief)" % (B.X_PL[0] + 3.0 + 6.0 - B.X_PL[1]))
# Motor von oben einlegen: Bahn frei?
sweep = None
for dy in np.arange(0.0, 36.0, 1.5):
    m = B.motor_model().translate([0, dy, 0])
    sweep = m if sweep is None else sweep + m
print("Einlegebahn Motor x Gehaeuse: %.3f mm3" % (sweep ^ tub).volume())
# Ritzel-Wellen-Eingriff
print("Welle im Ritzel: %.2f mm" % ((B.X_PL[0] - B.X_PIN[1]) * 0 + (B.X_PIN[1] - (B.X_GB[0] - B.SHAFT_L))))
# Mindestabstand Ritzel zu Gehaeuse
tp = B.to_trimesh(A["pinion"]); tt = B.to_trimesh(tub)
q = trimesh.proximity.ProximityQuery(tt)
print("min. Spalt Ritzel-Gehaeuse: %.2f mm" % np.min(np.abs(q.signed_distance(tp.sample(20000)))))
import sys; tm=None

pickle.dump({k: B.to_trimesh(v) for k, v in A.items()}, open("assembly_v3.pkl", "wb"))
