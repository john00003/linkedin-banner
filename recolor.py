#!/usr/bin/env python3
"""Crop + flip + gradient-map the Ubuntu 'Anomaly' wallpaper into a LinkedIn banner plate.

Anomaly is effectively a single-hue luminance ramp (flat plum #2D001D background ->
orange -> pale yellow highlights). That means a 1D *gradient map* keyed on luminance
reproduces it exactly in a new palette -- no hand-painted 3D LUT needed.
"""
import numpy as np
from PIL import Image

SRC = "/usr/share/backgrounds/iryge-Anomaly.png"   # 3840x2160 lossless original
OUT = "banner_plate.png"
W, H = 1584, 396                                    # LinkedIn personal profile banner

# --- crop window on the 3840x2160 source (must be 4:1) -----------------------
CROP_X, CROP_W = 1920, 1920          # right half
CROP_H = CROP_W // 4                 # 480
CROP_Y = 980                         # vertical centre of the rays + wave

# --- gradient stops: t in [0,1] -> RGB --------------------------------------
# t=0   headshot backdrop grey; t=1  bright sage, lifted off the shirt colour.
STOPS = [
    (0.00, (0x33, 0x33, 0x35)),   # flat background  ~ headshot grey
    (0.12, (0x3B, 0x3E, 0x3A)),   # first hint of green in the faint lines
    (0.35, (0x4E, 0x5A, 0x46)),
    (0.60, (0x6C, 0x7C, 0x5C)),
    (0.80, (0x83, 0x8C, 0x76)),   # exact shirt colour
    (0.93, (0xA8, 0xBC, 0x8C)),
    (1.00, (0xD2, 0xE0, 0xB4)),   # highlight
]

# luminance range actually present in the source (p1 .. p99.9)
L_LO, L_HI = 10.0, 176.0


def ramp(n=256):
    """Piecewise-linear interpolate STOPS into an n-entry lookup table."""
    ts = np.array([s[0] for s in STOPS])
    cs = np.array([s[1] for s in STOPS], float)
    x = np.linspace(0, 1, n)
    return np.stack([np.interp(x, ts, cs[:, ch]) for ch in range(3)], axis=1)


def main():
    src = Image.open(SRC).convert("RGB")
    tile = src.crop((CROP_X, CROP_Y, CROP_X + CROP_W, CROP_Y + CROP_H))
    tile = tile.transpose(Image.FLIP_LEFT_RIGHT)          # busy side -> left
    tile = tile.resize((W, H), Image.LANCZOS)

    a = np.asarray(tile, float)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    t = np.clip((lum - L_LO) / (L_HI - L_LO), 0, 1)

    lut = ramp()
    idx = (t * 255).round().astype(np.uint8)
    out = lut[idx].round().clip(0, 255).astype(np.uint8)

    Image.fromarray(out).save(OUT)
    print(f"wrote {OUT}  {W}x{H}")


def write_cube(path="anomaly_sage.cube", n=33):
    """Same transform baked as a portable 33^3 .cube LUT (ffmpeg/Resolve/Photoshop)."""
    lut = ramp(1024)
    g = np.linspace(0, 1, n)
    b, gr, r = np.meshgrid(g, g, g, indexing="ij")
    lum = (0.2126 * r + 0.7152 * gr + 0.0722 * b) * 255.0
    t = np.clip((lum - L_LO) / (L_HI - L_LO), 0, 1)
    rgb = lut[(t * 1023).round().astype(int)] / 255.0
    with open(path, "w") as f:
        f.write(f"TITLE \"Anomaly -> sage/grey\"\nLUT_3D_SIZE {n}\n")
        for v in rgb.reshape(-1, 3):
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
    write_cube()
