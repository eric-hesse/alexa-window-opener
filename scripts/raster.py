"""Mini-Renderer mit Z-Buffer (orthografisch), fuer saubere Vorschaubilder."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def render(items, view_dir, up=(0, 0, 1), size=(1400, 900), margin=40, bg=(255, 255, 255),
           light=(0.4, 0.6, 0.7), labels=None, title=None):
    d = np.asarray(view_dir, float); d /= np.linalg.norm(d)            # Blickrichtung (Kamera -> Szene)
    u = np.asarray(up, float); r = np.cross(d, u); r /= np.linalg.norm(r); u = np.cross(r, d)
    L = np.asarray(light, float); L /= np.linalg.norm(L)
    allv = np.vstack([m.vertices for m, _ in items])
    P = np.c_[allv @ r, allv @ u]
    lo, hi = P.min(0), P.max(0)
    W, H = size
    s = min((W - 2 * margin) / (hi[0] - lo[0]), (H - 2 * margin) / (hi[1] - lo[1]))
    off = np.array([(W - s * (hi[0] - lo[0])) / 2, (H - s * (hi[1] - lo[1])) / 2])
    zbuf = np.full((H, W), np.inf); img = np.zeros((H, W, 3)); img[:] = bg
    def proj(v):
        p = np.c_[v @ r, v @ u]; px = (p - lo) * s + off
        return np.c_[px[:, 0], H - px[:, 1], v @ d]
    for mesh, col in items:
        V = proj(mesh.vertices); Fc = mesh.faces; N = mesh.face_normals
        shade = 0.35 + 0.65 * np.abs(N @ L)
        facing = (N @ d) < 0
        col = np.asarray(col, float)
        for fi in range(len(Fc)):
            a, b, c = V[Fc[fi]]
            x0 = int(max(0, np.floor(min(a[0], b[0], c[0])))); x1 = int(min(W - 1, np.ceil(max(a[0], b[0], c[0]))))
            y0 = int(max(0, np.floor(min(a[1], b[1], c[1])))); y1 = int(min(H - 1, np.ceil(max(a[1], b[1], c[1]))))
            if x1 < x0 or y1 < y0: continue
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12: continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            w1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / den
            w2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / den
            w3 = 1 - w1 - w2
            msk = (w1 >= -1e-6) & (w2 >= -1e-6) & (w3 >= -1e-6)
            if not msk.any(): continue
            z = w1 * a[2] + w2 * b[2] + w3 * c[2]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            upd = msk & (z < sub)
            if not upd.any(): continue
            sub[upd] = z[upd]
            f = shade[fi] * (1.0 if facing[fi] else 0.75)
            img[y0:y1 + 1, x0:x1 + 1][upd] = np.clip(col * f, 0, 255)
    # Kanten aus Tiefenspruengen
    zz = np.where(np.isinf(zbuf), np.nan, zbuf)
    gx = np.abs(np.diff(zz, axis=1, prepend=np.nan)); gy = np.abs(np.diff(zz, axis=0, prepend=np.nan))
    edge = (np.nan_to_num(gx, nan=0) > 1.2) | (np.nan_to_num(gy, nan=0) > 1.2)
    edge |= np.isinf(zbuf) ^ np.roll(np.isinf(zbuf), 1, 0) | np.isinf(zbuf) ^ np.roll(np.isinf(zbuf), 1, 1)
    img[edge] = img[edge] * 0.35
    im = Image.fromarray(img.astype(np.uint8)); dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        fbig = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except Exception:
        font = fbig = ImageFont.load_default()
    if labels:
        for txt, pt3, dxy in labels:
            p = proj(np.asarray([pt3], float))[0]; q = (p[0] + dxy[0], p[1] + dxy[1])
            dr.line([(p[0], p[1]), q], fill=(30, 30, 30), width=2)
            tb = dr.textbbox(q, txt, font=font)
            dr.rectangle([tb[0] - 4, tb[1] - 3, tb[2] + 4, tb[3] + 3], fill=(255, 255, 255), outline=(60, 60, 60))
            dr.text(q, txt, fill=(20, 20, 20), font=font)
    if title:
        dr.text((20, 15), title, fill=(20, 20, 20), font=fbig)
    return im
