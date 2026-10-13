"""Fensteroeffner v3 - JGA25-370 (6 V, 35 U/min, Encoder) direkt auf dem Ritzel,
TB6612FNG + ESP32 DevKit 30 Pin USB-C + Stromschienen-Stueck.
Original-Haken (case_okno) und Original-Zahnstange (okno_lin) bleiben.

Koordinaten = case_okno.stl:
  x = Motorachse (Ritzel aussen bei x -42.25..-32.25)
  y = von der Wand weg (Montageflaeche y = -1)
  z = Hoehe (0 = Oberkante)
"""
import pickle, sys, numpy as np, trimesh
import manifold3d as mf
from shapely import wkt
from shapely.geometry import Polygon, Point, box as sbox

SEG = 96
O = (13.0, -24.232)                 # Ritzel- = Motorachse (y, z)
X_PIN = (-42.25, -32.25)            # Ritzel (wie Original)
X_PL = (-32.0, -27.0)               # Frontplatte, Getriebestirn liegt bei x=-27 an
Y_BACK, Y_IN, Y_TOP, Y_LID = -1.0, 3.0, 44.5, 47.0
Z_TOP, Z_BOT, WALL = 0.0, -55.0, 1.5
X_END = (123.5, 126.0)              # Endwand

# Motor JGA25-370 (Masszeichnung)
GB_L, CAN_L, ENC_L = 25.0, 31.0, 15.5
X_GB = (X_PL[1], X_PL[1] + GB_L)                    # -27 .. -2
X_CAN = (X_GB[1], X_GB[1] + CAN_L)                  # -2 .. 29
X_ENC = (X_CAN[1], X_CAN[1] + ENC_L)                # 29 .. 44.5
R_GB, R_CAN, R_ENC = 12.5, 12.25, 12.5
SHAFT_L, BOSS_D, BOSS_L = 12.1, 7.0, 2.5
SCREW_R = 8.5                                       # 2x M3, Abstand 17

# Elektronik
TB_POCKET = (50.5, 72.0, -23.5, -2.0)               # x0,x1,z0,z1 (Modul 20,1 x 20,5)
RAIL_AREA = (52.0, 70.0, -42.0, -27.0)
ESP_X = (75.5, 104.5)                               # Board steht hochkant, USB nach unten
ESP_PED = (82.5, 97.5, -25.0, -12.0, 2.5)           # Sockel unter der Modul-Abschirmung
USB_NOTCH = (82.0, 98.0, 3.5)                       # x0,x1,y0 Kerbe in der Unterwand

TOWERS = [(4.0, -46.5), (113.5, -12.0), (113.5, -43.0)]
PILLARS = [(-24.0, -4.5), (-24.0, -50.5), (46.0, -4.5), (46.0, -50.5), (121.0, -3.5), (121.0, -51.5)]
T_OUT, T_SHAFT = 7.75, 6.0          # Turm aussen / Schacht fuer Schraubendreher
WS_HOLE, WS_HEAD = 2.75, 5.2        # Wandschraube 5 mm: Loch 5,5, Senkkopf bis 10,4

G = {k: (wkt.loads(w), i) for k, (w, i) in pickle.load(open("gears.pkl", "rb")).items()}


# ---------------- Helfer ----------------
def box(x0, x1, y0, y1, z0, z1):
    return mf.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def cyl_x(r, x0, x1, y, z, seg=SEG):
    return mf.Manifold.cylinder(x1 - x0, r, r, seg).rotate([0, 90, 0]).translate([x0, y, z])

def cyl_y(r, y0, y1, x, z, seg=SEG):
    return mf.Manifold.cylinder(y1 - y0, r, r, seg).rotate([-90, 0, 0]).translate([x, y0, z])

def cone_y(r0, r1, y0, y1, x, z, seg=SEG):
    return mf.Manifold.cylinder(y1 - y0, r0, r1, seg).rotate([-90, 0, 0]).translate([x, y0, z])

def cone_x(r0, r1, x0, x1, y, z, seg=SEG):
    return mf.Manifold.cylinder(x1 - x0, r0, r1, seg).rotate([0, 90, 0]).translate([x0, y, z])

def poly_cs(poly):
    rings = [np.asarray(poly.exterior.coords)[:-1]]
    rings += [np.asarray(r.coords)[:-1] for r in poly.interiors]
    return mf.CrossSection([r.tolist() for r in rings], mf.FillRule.EvenOdd)

def prism(poly, h):
    return mf.Manifold.extrude(poly_cs(poly), h)

def to_trimesh(man):
    mesh = man.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)
    pass
    return t

def from_trimesh(t):
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32),
                               tri_verts=np.asarray(t.faces, dtype=np.uint32)))

def place_x(part, x0, cy, cz, flip=False):
    part = part.rotate([0, -90, 0]) if flip else part.rotate([0, 90, 0])
    return part.translate([x0, cy, cz])


# ---------------- Ritzel mit D-Bohrung ----------------
def d_bore(r, flat):
    return Point(0, 0).buffer(r, resolution=64).intersection(sbox(-r - 1, -r - 1, flat, r + 1))

def part_pinion(r=2.2, flat=1.72):
    """13 Z, 10 breit. Lokales z=0 = Aussenseite (geschlossen, liegt auf dem Druckbett).
    D-Sackloch von der Motorseite, 7,3 tief (Welle steckt 6,85 drin)."""
    L = X_PIN[1] - X_PIN[0]
    depth = 7.3
    p = prism(G['pin'][0], L)
    p = p - prism(d_bore(r, flat), depth + 1).translate([0, 0, L - depth])
    # kleine Fase am Bohrungseingang
    p = p - mf.Manifold.cylinder(0.6, r, r + 0.6, SEG).translate([0, 0, L - 0.6 + 0.001])
    return p


# ---------------- Gehaeuse ----------------
def hook_part():
    orig = from_trimesh(trimesh.load("/mnt/user-data/uploads/case_okno.stl"))
    hook = orig ^ box(-80, X_PL[0] + 0.05, -5, 40, -60, 5)
    # Unterseite des Hakens (y=0) bis aufs Druckbett (y=-1) verlaengern -> keine Stuetzen noetig
    t = to_trimesh(hook)
    sec = t.section(plane_origin=[0, 0.3, 0], plane_normal=[0, 1, 0])
    polys = []
    for d in sec.discrete:
        pg = Polygon(d[:, [0, 2]]).buffer(0)
        if pg.area > 1: polys.append(pg)
    from shapely.ops import unary_union
    foot = unary_union(polys)
    # foot liegt in (x, z); extrudieren entlang y
    fm = prism(foot, 1.3)                     # extrudiert in lokal z -> spaeter auf y drehen
    # lokal (X=x, Y=z, Z=extr)  ->  Welt (x, y, z): y = -Z ... einfacher: Rx(+90): (X,Y,Z)->(X,-Z,Y)
    fm = fm.rotate([90, 0, 0])                # (x, z, e) -> (x, -e, z)
    fm = fm.translate([0, 0.3, 0])            # y = 0.3 - e  -> 0.3 .. -1.0
    return hook + fm


def build_tub():
    X0, X1 = X_PL[0], X_END[1]
    outer = box(X0, X1, Y_BACK, Y_TOP, Z_BOT, Z_TOP)
    inner = box(X_PL[1], X_END[0], Y_IN, Y_TOP + 1, Z_BOT + WALL, Z_TOP - WALL)
    tub = outer - inner

    # Motor-Saettel (Getriebe + Motorbecher)
    for xa, xb in ((-24.0, -19.0), (6.0, 10.0), (20.0, 24.0)):
        tub = tub + box(xa, xb, Y_IN - 0.01, O[0], Z_BOT + 1, Z_TOP - 1)
    # Wandschrauben-Tuerme und Deckelsaeulen
    for tx, tz in TOWERS:
        tub = tub + cyl_y(T_OUT, Y_IN - 0.01, Y_TOP, tx, tz)
    for px, pz in PILLARS:
        tub = tub + cyl_y(3.5, Y_IN - 0.01, Y_TOP, px, pz)

    # Elektronik: Rahmen fuer TB6612, Sockel fuer ESP32
    x0, x1, z0, z1 = TB_POCKET
    fr = box(x0 - 1.2, x1 + 1.2, Y_IN - 0.01, Y_IN + 2.0, z0 - 1.2, z1 + 1.2) - box(x0, x1, Y_IN - 1, Y_IN + 3, z0, z1)
    tub = tub + fr
    ex0, ex1, ez0, ez1, eh = ESP_PED
    tub = tub + box(ex0, ex1, Y_IN - 0.01, Y_IN + eh, ez0, ez1)
    # seitliche Fuehrungsleisten fuer das ESP (nur unten, ausserhalb der Stiftreihen)
    for xa, xb in ((ESP_X[0] - 1.2, ESP_X[0]), (ESP_X[1], ESP_X[1] + 1.2)):
        tub = tub + box(xa, xb, Y_IN - 0.01, Y_IN + 8.0, -53.5, -36.0)

    tub = tub + hook_part()

    # --- Motor-Freiraum ---
    tub = tub - cyl_x(R_GB + 0.25, X_GB[0] - 0.01, X_GB[1], *O)
    tub = tub - cyl_x(R_CAN + 0.3, X_CAN[0], X_CAN[1], *O)
    tub = tub - cyl_x(R_ENC + 0.5, X_ENC[0], X_ENC[1] + 2.5, *O)
    # Einlege-Schlitz in der Frontplatte (Welle Ø4 / Lagerbund Ø7), offen nach oben (+y)
    tub = tub - cyl_x(2.7, X_PL[0] - 1, X_PL[1] + 1, *O) - box(X_PL[0] - 1, X_PL[1] + 1, O[0], Y_TOP + 1, O[1] - 2.7, O[1] + 2.7)
    tub = tub - cyl_x(3.8, X_PL[1] - BOSS_L - 0.2, X_PL[1] + 1, *O) - box(X_PL[1] - BOSS_L - 0.2, X_PL[1] + 1, O[0], Y_TOP + 1, O[1] - 3.8, O[1] + 3.8)
    # Motorschrauben M3 (oben/unten), Kopf versenkt in der Frontplatte (Ritzel laeuft davor)
    for dz in (+SCREW_R, -SCREW_R):
        tub = tub - cyl_x(1.7, X_PL[0] - 1, X_PL[1] + 1, O[0], O[1] + dz)
        tub = tub - cyl_x(3.2, X_PL[0] - 1, X_PL[0] + 3.2, O[0], O[1] + dz)
    # Platz fuer die zwei Getriebe-Kreuzschlitzkoepfe (links/rechts)
    for dy in (+SCREW_R, -SCREW_R):
        tub = tub - cyl_x(3.75, X_PL[1] - 1.6, X_PL[1] + 1, O[0] + dy, O[1])

    # Wandschrauben: Loch 5,5 + Senkung, Schacht fuer den Schraubendreher
    for tx, tz in TOWERS:
        tub = tub - cyl_y(WS_HOLE, Y_BACK - 1, Y_IN + 1, tx, tz)
        tub = tub - cone_y(WS_HOLE, WS_HEAD, Y_IN - (WS_HEAD - WS_HOLE), Y_IN + 0.001, tx, tz)
        tub = tub - cyl_y(T_SHAFT, Y_IN, Y_TOP + 1, tx, tz)
    # Deckelschrauben M3: Kernloch 2,6, 12 tief
    for px, pz in PILLARS:
        tub = tub - cyl_y(1.3, Y_TOP - 12, Y_TOP + 1, px, pz)

    # USB-Kabel: Kerbe in der Unterwand unter dem ESP
    nx0, nx1, ny0 = USB_NOTCH
    tub = tub - box(nx0, nx1, ny0, Y_TOP + 1, Z_BOT - 1, Z_BOT + WALL + 0.5)
    return tub


def build_lid():
    lid = box(X_PL[0], X_END[1], Y_TOP, Y_LID, Z_BOT, Z_TOP)
    # Zunge schliesst den Wellen-Schlitz in der Frontplatte
    lid = lid + box(X_PL[0] + 0.2, X_PL[1] - BOSS_L - 0.4, O[0] + 7.3, Y_TOP, O[1] - 2.45, O[1] + 2.45)
    # Zunge schliesst die USB-Kerbe bis knapp ueber den Stecker
    nx0, nx1, _ = USB_NOTCH
    lid = lid + box(nx0 + 0.25, nx1 - 0.25, 13.5, Y_TOP, Z_BOT, Z_BOT + WALL)
    # Niederhalter fuer den Motor
    for xa, xb, r in ((-16.0, -11.0, R_GB), (12.0, 17.0, R_CAN)):
        lid = lid + box(xa, xb, O[0] + r + 0.35, Y_TOP, O[1] - 4, O[1] + 4)
    for px, pz in PILLARS:
        lid = lid - cyl_y(1.7, Y_TOP - 1, Y_LID + 1, px, pz)
        lid = lid - cone_y(1.7, 3.3, Y_LID - 1.6, Y_LID + 0.001, px, pz)
    for tx, tz in TOWERS:
        lid = lid - cyl_y(T_SHAFT + 0.25, Y_TOP - 1, Y_LID + 1, tx, tz)
    return lid


# ---------------- Modelle fuer Pruefung / Bilder ----------------
def motor_model():
    m = cyl_x(R_GB, *X_GB, *O) + cyl_x(R_CAN, *X_CAN, *O) + cyl_x(R_ENC - 0.5, *X_ENC, *O)
    m = m + cyl_x(BOSS_D / 2, X_GB[0] - BOSS_L, X_GB[0], *O)
    m = m + cyl_x(2.0, X_GB[0] - SHAFT_L, X_GB[0] - BOSS_L, *O)
    return m

def esp_model():
    # PCB 51,5 x 28,3 x 1,6 hochkant; Bauteilseite zur Wand
    ex0, ex1, ez0, ez1, eh = ESP_PED
    yb = Y_IN + eh + 1.0 + 3.1                 # Unterseite PCB (Bauteilseite)
    xc = (ESP_X[0] + ESP_X[1]) / 2
    pcb = box(xc - 14.15, xc + 14.15, yb, yb + 1.6, -53.5, -2.0)
    shield = box(xc - 9, xc + 9, yb - 3.1, yb, -27, -9)
    usb = box(xc - 4.5, xc + 4.5, yb - 3.2, yb, -53.5 - 0.6, -46)
    hdr = box(xc - 14, xc - 11.5, yb + 1.6, yb + 4.1, -50, -6) + box(xc + 11.5, xc + 14, yb + 1.6, yb + 4.1, -50, -6)
    pins = box(xc - 13.1, xc - 12.5, yb + 4.1, yb + 10.1, -50, -6) + box(xc + 12.5, xc + 13.1, yb + 4.1, yb + 10.1, -50, -6)
    plug = box(xc - 6.2, xc + 6.2, yb - 1.6 - 3.8, yb - 1.6 + 3.8, -73, -53.5)
    return pcb + shield + usb + hdr + pins, plug

def tb_model():
    x0, x1, z0, z1 = TB_POCKET
    xc, zc = (x0 + x1) / 2, (z0 + z1) / 2
    yb = Y_IN + 1.0 + 1.2
    pcb = box(xc - 10.05, xc + 10.05, yb, yb + 1.6, zc - 10.25, zc + 10.25)
    hdr = box(xc - 10, xc + 10, yb + 1.6, yb + 4.1, zc + 6.5, zc + 9) + box(xc - 10, xc + 10, yb + 1.6, yb + 4.1, zc - 9, zc - 6.5)
    return pcb + hdr

def rail_model():
    x0, x1, z0, z1 = RAIL_AREA
    return box(x0 + 1, x1 - 1, Y_IN + 1.0, Y_IN + 1.0 + 8.5, z0 + 2, z1 - 2)


if __name__ == "__main__":
    tub = build_tub(); lid = build_lid()
    pin = part_pinion(); pin_t = part_pinion(r=2.1, flat=1.62)
    parts = {"tub": tub, "lid": lid, "pin": pin, "pin_tight": pin_t}
    pickle.dump({k: to_trimesh(v) for k, v in parts.items()}, open("parts_v3.pkl", "wb"))
    for k, v in parts.items():
        t = to_trimesh(v)
        print(f"{k}: watertight={t.is_watertight} vol={t.volume/1000:.1f} cm3 bounds={np.round(t.bounds,2).tolist()}")
