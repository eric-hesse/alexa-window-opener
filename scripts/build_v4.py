"""Fensteroeffner v4 - kompaktes Gehaeuse mit runden Ecken.
JGA25-370 direkt auf dem Ritzel, Elektronik liegt auf dem Boden (Stifte nach oben).

Koordinaten wie case_okno.stl:
  x = Motorachse (Ritzel aussen bei x -42.25..-32.25, Gehaeuse ab x = -32)
  y = von der Wand weg (Wand bei y = -1)
  z = Hoehe (0 = Oberkante, -40 = Unterkante)
"""
import pickle, numpy as np, trimesh
import manifold3d as mf
from shapely.geometry import Polygon, Point, box as sbox
from build_v3 import (box, cyl_x, cyl_y, cone_y, prism, to_trimesh, from_trimesh,
                      place_x, part_pinion, hook_part, G, SEG)

# ---------------- Hauptmasse ----------------
O = (13.0, -24.232)                 # Ritzel- = Motorachse (y, z)
X_PIN = (-42.25, -32.25)
X_FR, X_PL1 = -32.0, -27.0          # Frontplatte (5 mm), Getriebestirn bei x = -27
Y_BACK, Y_IN, Y_SPLIT, Y_FRONT = -1.0, 1.5, 34.0, 36.0
Z_TOP, Z_BOT, WZ = 0.0, -40.0, 1.8
ZI_TOP, ZI_BOT = Z_TOP - WZ, Z_BOT + WZ          # -1.8 / -38.2

# Motor JGA25-370
X_GB = (X_PL1, X_PL1 + 25.0)        # Getriebe  -27 .. -2
X_CAN = (X_GB[1], X_GB[1] + 31.0)   # Motor     -2 .. 29
X_ENC = (X_CAN[1], X_CAN[1] + 15.5) # Encoder   29 .. 44.5
R_GB, R_CAN, R_ENC = 12.5, 12.25, 12.5
SHAFT_L, BOSS_L, SCREW_R = 12.1, 2.5, 8.5

# Elektronik (liegt auf dem Boden, Stifte nach oben)
TB = (52.6, 73.4, 1.6, 22.4)        # Mulde fuer TB6612 (x0,x1,y0,y1), Chipseite unten
RAIL = (52.6, 73.4, 23.6, 33.6)     # Ablage Stromschiene
ESP_L, ESP_W = 51.5, 28.3
ESP_X0 = 74.5
ESP_X1 = ESP_X0 + ESP_L             # 126.0 = USB-Ende
ESP_YC = (Y_IN + Y_SPLIT) / 2       # 17.75
ESP_CF = -31.9                      # Unterseite Platine (Bauteilseite, zeigt nach unten)
USB_Z = ESP_CF - 1.6                # Mitte USB-Stecker
X_EW0 = ESP_X1 + 0.8                # Endwand innen
X_END = X_EW0 + 3.5                 # Endwand aussen  (130.3)

# Wandschrauben 5 mm Senkkopf: alle oben, Weg fuer den Kopf von vorne frei
WALL_SCREWS = [(16.0, -6.5), (63.0, -6.5), (106.0, -6.5)]
WS_HOLE, WS_HEAD, WS_PATH = 2.75, 5.2, 5.25
# Deckelschrauben M3
LID_SCREWS = [(-29.0, -5.6), (-29.0, -34.4), (46.0, -5.3), (48.6, -34.7), (122.8, -5.3)]
PILLARS = [(46.0, -5.3), (122.8, -5.3)]           # durchgehende Saeulen
BOSSES = [(48.6, -34.7)]                          # kurze Dome (unten, ueber dem Kabelraum)


# ---------------- 2D-Helfer ----------------
def rrect(x0, x1, z0, z1, r_ft, r_fb, r_rt, r_rb, n=24):
    """Rechteck in (x, z) mit Eckradien: f=vorne(x0) r=hinten(x1), t=oben(z1) b=unten(z0)."""
    pts = []
    def arc(cx, cz, r, a0, a1):
        for a in np.linspace(a0, a1, n):
            pts.append((cx + r * np.cos(a), cz + r * np.sin(a)))
    arc(x1 - r_rt, z1 - r_rt, r_rt, 0, np.pi / 2)
    arc(x0 + r_ft, z1 - r_ft, r_ft, np.pi / 2, np.pi)
    arc(x0 + r_fb, z0 + r_fb, r_fb, np.pi, 1.5 * np.pi)
    arc(x1 - r_rb, z0 + r_rb, r_rb, 1.5 * np.pi, 2 * np.pi)
    return Polygon(pts)

def prism_y(poly_xz, y0, y1):
    from shapely.geometry import MultiPolygon
    from shapely.affinity import scale
    polys = poly_xz.geoms if isinstance(poly_xz, MultiPolygon) else [poly_xz]
    out = None
    for pg in polys:
        p = scale(pg, 1.0, -1.0, origin=(0, 0))          # (x, z) -> (x, -z), Loecher bleiben erhalten
        m = prism(p, y1 - y0).rotate([-90, 0, 0]).translate([0, y0, 0])
        out = m if out is None else out + m
    return out

OUTER = rrect(X_FR, X_END, Z_BOT, Z_TOP, 0.8, 4.0, 6.0, 6.0)
INNER = rrect(X_PL1, X_EW0, ZI_BOT, ZI_TOP, 0.5, 1.0, 3.0, 3.0)


def body():
    a = prism_y(OUTER.buffer(-0.6, join_style=1), Y_BACK, Y_BACK + 0.01)
    b = prism_y(OUTER, Y_BACK + 0.6, Y_FRONT - 1.5)
    c = prism_y(OUTER.buffer(-1.5, join_style=1), Y_FRONT - 0.01, Y_FRONT)
    return mf.Manifold.batch_hull([a, b, c])


# ---------------- Gehaeuse (Wanne) ----------------
def build_tub():
    t = body() ^ box(-60, 200, Y_BACK - 1, Y_SPLIT, -60, 10)
    t = t - prism_y(INNER, Y_IN, Y_SPLIT + 1)

    # Rueckwand an den Wandschrauben verstaerkt
    for x, z in WALL_SCREWS:
        t = t + cyl_y(7.0, Y_IN - 0.01, 3.5, x, z)
    # Motor-Saettel
    for xa, xb in ((-24.0, -20.0), (3.0, 7.0), (25.0, 28.5)):
        t = t + box(xa, xb, Y_IN - 0.01, O[0], ZI_BOT - 0.01, ZI_TOP + 0.01)
    # Deckelsaeulen und -dome
    for x, z in PILLARS:
        t = t + cyl_y(3.5, Y_IN - 0.01, Y_SPLIT, x, z)
    for x, z in BOSSES:
        t = t + cyl_y(3.5, 24.5, Y_SPLIT, x, z)
        # 45-Grad-Stuetze zum Boden (druckbar ohne Stuetzmaterial)
        t = t + mf.Manifold.batch_hull([cyl_y(3.5, 24.5, 24.6, x, z),
                                        box(x - 3.5, x + 3.5, 17.5, 17.6, ZI_BOT - 0.01, ZI_BOT + 0.5)])
    # ESP: Sockel unter der Metallkappe + Anlage an der Rueckseite
    xs = ESP_X0 + 14.5
    t = t + box(xs - 7, xs + 7, ESP_YC - 7, ESP_YC + 7, ZI_BOT - 0.01, ESP_CF - 4.1)
    t = t + box(ESP_X0 + 4, ESP_X1 - 4, Y_IN - 0.01, ESP_YC - ESP_W / 2 - 0.25, ZI_BOT - 0.01, ESP_CF + 1.2)

    # alles auf die Aussenform begrenzen, dann den Original-Haken anfuegen
    t = t ^ (body() ^ box(-60, 200, Y_BACK - 1, Y_SPLIT, -60, 10))
    t = t + (hook_part() ^ box(-80, X_FR + 0.05, Y_BACK - 1, 40, -12, 1))

    # --- Motor ---
    t = t - cyl_x(R_GB + 0.25, X_GB[0] - 0.01, X_GB[1], *O)
    t = t - cyl_x(R_CAN + 0.3, X_CAN[0], X_CAN[1], *O)
    t = t - cyl_x(R_ENC + 0.5, X_ENC[0], X_ENC[1] + 2.0, *O)
    # Schlitz Welle Ø4 / Lagerbund Ø7, offen nach vorne
    t = t - cyl_x(2.7, X_FR - 1, X_PL1 + 1, *O) - box(X_FR - 1, X_PL1 + 1, O[0], Y_SPLIT + 1, O[1] - 2.7, O[1] + 2.7)
    t = t - cyl_x(3.8, X_PL1 - BOSS_L - 0.2, X_PL1 + 1, *O) - box(X_PL1 - BOSS_L - 0.2, X_PL1 + 1, O[0], Y_SPLIT + 1, O[1] - 3.8, O[1] + 3.8)
    # Motorschrauben M3 x 6, Kopf versenkt
    for dz in (+SCREW_R, -SCREW_R):
        t = t - cyl_x(1.7, X_FR - 1, X_PL1 + 1, O[0], O[1] + dz)
        t = t - cyl_x(3.2, X_FR - 1, X_FR + 3.2, O[0], O[1] + dz)
    for dy in (+SCREW_R, -SCREW_R):          # Getriebeschraubenkoepfe
        t = t - cyl_x(3.75, X_PL1 - 1.6, X_PL1 + 1, O[0] + dy, O[1])

    # Wandschrauben: Loch, Senkung, Weg fuer Kopf + Schraubendreher
    for x, z in WALL_SCREWS:
        t = t - cyl_y(WS_HOLE, Y_BACK - 1, 4.0, x, z)
        t = t - cone_y(WS_HOLE, WS_HEAD, 3.5 - (WS_HEAD - WS_HOLE), 3.5 + 0.001, x, z)
        t = t - cyl_y(WS_PATH, 3.5, Y_SPLIT + 1, x, z)
    # Deckelschrauben: Kernloch 2,6, 9 tief
    for x, z in LID_SCREWS:
        t = t - cyl_y(1.3, Y_SPLIT - 9, Y_SPLIT + 1, x, z)
    # Mulde fuer TB6612
    x0, x1, y0, y1 = TB
    t = t - box(x0, x1, y0, y1, ZI_BOT - 0.6, ZI_BOT + 0.01)
    # USB-Kerbe in der Endwand
    t = t - box(X_EW0 - 0.1, X_END + 1, ESP_YC - 7.0, Y_SPLIT + 1, ZI_BOT + 0.1, USB_Z + 4.6)
    return t


# ---------------- Deckel ----------------
def window_icon():
    """kleines Fenster-Symbol (0,5 mm vertieft) im Deckel."""
    cx, cz, w, h, lw = 112.0, -20.0, 12.0, 16.0, 1.1
    outer = sbox(cx - w / 2, cz - h / 2, cx + w / 2, cz + h / 2)
    inner = sbox(cx - w / 2 + lw, cz - h / 2 + lw, cx + w / 2 - lw, cz + h / 2 - lw)
    g = outer.difference(inner)
    g = g.union(sbox(cx - lw / 2, cz - h / 2, cx + lw / 2, cz + h / 2))
    g = g.union(sbox(cx - w / 2, cz - lw / 2, cx + w / 2, cz + lw / 2))
    return prism_y(g.buffer(0.15, join_style=1), Y_FRONT - 0.5, Y_FRONT + 1)

def build_lid():
    lid = body() ^ box(-60, 200, Y_SPLIT, Y_FRONT + 1, -60, 10)
    # Falz (sitzt innen an den Waenden, 1,8 tief)
    ring = INNER.buffer(-0.25, join_style=1).difference(INNER.buffer(-1.45, join_style=1))
    lip = prism_y(ring, 32.2, Y_SPLIT + 0.01)
    for x, z in PILLARS + BOSSES:
        lip = lip - cyl_y(3.5 + 0.4, 30, 40, x, z)
    # unten neben dem TB6612 frei lassen: dort liegt die Stromschiene bis an den Deckel
    lip = lip - box(RAIL[0] - 1.5, RAIL[1] + 1.0, 30, 40, ZI_BOT - 1, ZI_BOT + 3)
    lid = lid + lip
    # Zunge schliesst den Wellenschlitz in der Frontplatte
    lid = lid + box(X_FR + 0.2, X_PL1 - BOSS_L - 0.4, O[0] + 2.9, Y_SPLIT + 0.01, O[1] - 2.45, O[1] + 2.45)
    # Zunge schliesst die USB-Kerbe bis knapp ueber den Stecker
    lid = lid + (box(X_EW0 + 0.15, X_END + 1, ESP_YC + 7.0, Y_SPLIT + 0.01, ZI_BOT + 0.3, USB_Z + 4.4)
                 ^ body())
    # Niederhalter fuer den Motor
    for xa, xb, r in ((-16.0, -11.0, R_GB), (13.0, 18.0, R_CAN)):
        lid = lid + box(xa, xb, O[0] + r + 0.35, Y_SPLIT + 0.01, O[1] - 4, O[1] + 4)
    # Schraubloecher mit leichter Senkung
    for x, z in LID_SCREWS:
        lid = lid - cyl_y(1.7, Y_SPLIT - 3, Y_FRONT + 1, x, z)
        lid = lid - cone_y(1.7, 2.6, Y_FRONT - 0.9, Y_FRONT + 0.001, x, z)
    lid = lid - window_icon()
    return lid


# ---------------- Modelle zur Pruefung / fuer Bilder ----------------
def motor_model():
    m = cyl_x(R_GB, *X_GB, *O) + cyl_x(R_CAN, *X_CAN, *O) + cyl_x(R_ENC - 0.5, *X_ENC, *O)
    m = m + cyl_x(3.5, X_GB[0] - BOSS_L, X_GB[0], *O)
    m = m + cyl_x(2.0, X_GB[0] - SHAFT_L, X_GB[0] - BOSS_L, *O)
    return m

def esp_model():
    y0, y1 = ESP_YC - ESP_W / 2, ESP_YC + ESP_W / 2
    pcb = box(ESP_X0, ESP_X1, y0, y1, ESP_CF, ESP_CF + 1.6)
    xs = ESP_X0 + 14.5
    shield = box(xs - 8.5, xs + 8.5, ESP_YC - 9, ESP_YC + 9, ESP_CF - 3.1, ESP_CF)
    usb = box(ESP_X1 - 7.5, ESP_X1 + 0.7, ESP_YC - 4.5, ESP_YC + 4.5, ESP_CF - 3.2, ESP_CF)
    parts = pcb + shield + usb
    for yr in (ESP_YC - 11.43, ESP_YC + 11.43):
        parts = parts + box(ESP_X0 + 6, ESP_X0 + 44, yr - 1.27, yr + 1.27, ESP_CF + 1.6, ESP_CF + 4.1)   # Stiftleiste
        parts = parts + box(ESP_X0 + 6, ESP_X0 + 44, yr - 1.27, yr + 1.27, ESP_CF + 4.1, ESP_CF + 18.1)  # Dupont-Stecker
    plug = box(ESP_X1 + 0.7, ESP_X1 + 22, ESP_YC - 6.25, ESP_YC + 6.25, USB_Z - 4.0, USB_Z + 4.0)
    return parts, plug

def tb_model():
    x0, x1, y0, y1 = TB
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    zb = ZI_BOT - 0.6 + 1.0 + 1.2
    pcb = box(xc - 10.05, xc + 10.05, yc - 10.25, yc + 10.25, zb, zb + 1.6)
    for xr in (xc - 8.9, xc + 8.9):
        pcb = pcb + box(xr - 1.27, xr + 1.27, yc - 10, yc + 10, zb + 1.6, zb + 4.1)
        pcb = pcb + box(xr - 1.27, xr + 1.27, yc - 10, yc + 10, zb + 4.1, zb + 18.1)
    return pcb

def rail_model():
    x0, x1, y0, y1 = RAIL
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    r = box(xc - 7.5, xc + 7.5, yc - 4.5, yc + 4.5, ZI_BOT, ZI_BOT + 1 + 8.5)
    return r + box(xc - 6.5, xc + 6.5, yc - 2.5, yc + 2.5, ZI_BOT + 9.5, ZI_BOT + 23.5)

def screw_models():
    s = None
    for dz in (+SCREW_R, -SCREW_R):
        m = cyl_x(2.75, X_FR + 0.15, X_FR + 3.0, O[0], O[1] + dz) + cyl_x(1.45, X_FR + 3.0, X_FR + 9.0, O[0], O[1] + dz)
        s = m if s is None else s + m
    return s

def wall_screw_paths():
    p = None
    for x, z in WALL_SCREWS:
        m = cyl_y(4.9, 3.5, Y_SPLIT + 5, x, z)
        p = m if p is None else p + m
    return p


if __name__ == "__main__":
    import sys
    tub, lid = build_tub(), build_lid()
    for k, v in {"tub": tub, "lid": lid}.items():
        t = to_trimesh(v)
        print(k, t.is_watertight, np.round(t.bounds, 2).tolist(), "%.1f cm3" % (t.volume / 1000))
