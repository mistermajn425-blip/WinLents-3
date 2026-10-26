"""Нарезает ассеты из макета (design.png) в src/assets.
Запуск: python tools/prepare_assets.py design.png   (нужен Pillow и numpy)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = sys.argv[1] if len(sys.argv) > 1 else "design.png"
OUT = os.path.join(os.path.dirname(__file__), "..", "src", "assets")
os.makedirs(os.path.join(OUT, "icons"), exist_ok=True)

img = Image.open(SRC).convert("RGB")
S = img.width / 1254  # координаты ниже даны для макета 1254x1254


def crop(b):
    return img.crop(tuple(int(v * S) for v in b))


def trim(im, thr=70, pad=4):
    bb = im.convert("L").point(lambda v: 255 if v > thr else 0).getbbox()
    if not bb:
        return im
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad))


def to_alpha(im):
    """Тёмный фон макета -> прозрачность (иконки и логотипы становятся PNG с альфой)."""
    a = np.asarray(im.convert("RGB")).astype(float)
    m = a.max(axis=2)
    rgb = np.where(m[..., None] > 0, a * 255 / np.maximum(m, 1)[..., None], 0)
    alpha = np.clip((m - 22) * 255 / 233, 0, 255)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype("uint8"), "RGBA")


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def gradient(cols, w=540, h=960):
    y, x = np.mgrid[0:h, 0:w]
    t = np.clip(0.35 * x / w + 0.65 * y / h, 0, 1) * (len(cols) - 1)
    i = np.minimum(t.astype(int), len(cols) - 2)
    f = (t - i)[..., None]
    c = np.array(cols, float)
    return Image.fromarray((c[i] * (1 - f) + c[i + 1] * f).astype("uint8"))


# --- иконки интерфейса: (центр x, центр y, полуширина, полувысота) ---
ICONS = {
    "home": (86, 663, 38, 38), "search": (195, 663, 38, 38), "plus": (315, 663, 38, 38),
    "inbox": (440, 663, 38, 38), "profile": (554, 663, 38, 38),
    "heart_on": (89, 747, 34, 34), "heart": (188, 747, 34, 34), "comment": (287, 747, 34, 34),
    "share": (380, 747, 34, 34), "save": (478, 747, 34, 34), "more": (556, 747, 34, 34),
    "fire": (89, 832, 34, 25), "explore": (213, 832, 34, 25), "friends": (329, 832, 34, 25),
    "music": (434, 832, 34, 25), "games": (547, 832, 34, 25),
}
for name, (cx, cy, hw, hh) in ICONS.items():
    to_alpha(trim(crop((cx - hw, cy - hh, cx + hw, cy + hh)))).save(f"{OUT}/icons/{name}.png")

# --- логотипы ---
to_alpha(trim(crop((375, 185, 755, 280)))).save(f"{OUT}/logo_wordmark.png")
to_alpha(trim(crop((805, 160, 972, 288)))).save(f"{OUT}/logo_stack.png")
to_alpha(trim(crop((36, 462, 183, 604)), thr=90)).save(f"{OUT}/icons/w_mark.png")

# --- иконка приложения (512x512) ---
ic = crop((35, 72, 345, 392))
for pt in [(0, 0), (ic.width - 1, 0), (0, ic.height - 1), (ic.width - 1, ic.height - 1)]:
    ImageDraw.floodfill(ic, pt, (0, 0, 0), thresh=22)
side = min(ic.size)
ic = ic.crop(((ic.width - side) // 2, (ic.height - side) // 2, (ic.width + side) // 2, (ic.height + side) // 2))
ic.resize((512, 512), Image.LANCZOS).save(f"{OUT}/icon.png")

# --- фоны ленты ---
sheets = {
    "feed_photo": crop((1020, 95, 1190, 375)),
    "feed_waves": crop((191, 930, 338, 1218)),
}
for name, im in sheets.items():
    cover(im, 540, 960).filter(ImageFilter.GaussianBlur(1.3)).save(f"{OUT}/{name}.jpg", quality=88)
gradient([(20, 229, 255), (139, 92, 246), (255, 61, 187)]).save(f"{OUT}/feed_grad_a.jpg", quality=88)
gradient([(10, 10, 14), (120, 40, 200), (255, 45, 111)]).save(f"{OUT}/feed_grad_b.jpg", quality=88)
print("OK", img.size)
