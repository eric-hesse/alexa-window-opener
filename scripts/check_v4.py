import itertools, pickle, numpy as np, trimesh
import build_v4 as B

tub, lid = B.build_tub(), B.build_lid()
esp, plug = B.esp_model()
A = {"tub": tub, "lid": lid, "pinion": B.place_x(B.part_pinion(), B.X_PIN[0], *B.O),
     "motor": B.motor_model(), "esp": esp, "usb_plug": plug, "tb6612": B.tb_model(),
     "rail": B.rail_model(), "m3x6": B.screw_models()}
expected = {("motor", "pinion"), ("motor", "m3x6"), ("esp", "usb_plug")}
bad = 0
print("=== Ueberschneidungen ===")
for a, b in itertools.combinations(A, 2):
    v = (A[a] ^ A[b]).volume()
    if v > 1e-3:
        ok = (a, b) in expected or (b, a) in expected
        bad += not ok
        print(f"{a:9s} x {b:9s}: {v:8.3f} mm3 {'(gewollt)' if ok else '<-- PROBLEM'}")
print("Probleme:", bad)

# Motor von vorne einlegen
sweep = None
for dy in np.arange(0.0, 26.0, 1.0):
    m = B.motor_model().translate([0, dy, 0])
    sweep = m if sweep is None else sweep + m
print("Einlegebahn Motor x Gehaeuse: %.3f mm3" % (sweep ^ tub).volume())

# Wandschrauben: Weg fuer Kopf/Schraubendreher frei (bei eingebautem Motor + Platinen)
paths = B.wall_screw_paths()
for k in ("tub", "motor", "esp", "tb6612", "rail"):
    print("Schraubweg x %-7s: %.3f mm3" % (k, (paths ^ A[k]).volume()))

# Deckel: Absenken (letzte 3 mm) kollisionsfrei?
lsweep = None
for dy in np.arange(0.0, 3.01, 0.5):
    m = lid.translate([0, dy, 0]); lsweep = m if lsweep is None else lsweep + m
for k in ("tub", "esp", "tb6612", "rail", "motor"):
    print("Deckel aufsetzen x %-7s: %.3f mm3" % (k, (lsweep ^ A[k]).volume()))

# Abstaende
def mind(a, b, n=20000):
    q = trimesh.proximity.ProximityQuery(B.to_trimesh(b))
    return np.min(np.abs(q.signed_distance(B.to_trimesh(a).sample(n))))
print("Spalt Ritzel-Gehaeuse %.2f mm" % mind(A["pinion"], tub))
print("Spalt ESP-Deckel %.2f mm, TB-Deckel %.2f mm" % (mind(esp, lid, 8000), mind(A["tb6612"], lid, 8000)))
print("Spalt ESP-Gehaeuse %.2f mm" % mind(esp, tub, 8000))
pickle.dump({k: B.to_trimesh(v) for k, v in A.items()}, open("assembly_v4.pkl", "wb"))
