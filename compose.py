#!/usr/bin/env python3
"""Build a LinkedIn banner from Ubuntu's 'Anomaly' wallpaper (CC BY-SA 4.0, Ian Ryge).

Pipeline:  crop (4:1) -> horizontal flip -> luminance gradient-map -> scrim -> text.
The gradient map is the whole trick: Anomaly is a single-hue luminance ramp, so
remapping luminance through a new colour ramp restages it in any palette you like.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC  = "/usr/share/backgrounds/iryge-Anomaly.png"     # 3840x2160 lossless
JUSTIFY_TAGLINE = True   # stretch tagline tracking to span the full ASCII block
TAG_TRACK = 1.6          # fixed tracking used when JUSTIFY_TAGLINE is False
OUT  = "linkedin_banner_justified.png" if JUSTIFY_TAGLINE else "linkedin_banner.png"
W, H = 1584, 396                                       # LinkedIn profile banner

CROP_X, CROP_Y, CROP_W = 1120, 1200, 1920              # 4:1 window, chosen for a calm right side
CROP_H = CROP_W // 4

L_LO, L_HI = 10.0, 176.0                               # luminance range present in the source

STOPS = [                                              # t in [0,1] -> RGB
    (0.00, (0x2E, 0x2E, 0x30)),   # flat background ~ headshot grey
    (0.12, (0x37, 0x3A, 0x36)),
    (0.35, (0x4A, 0x56, 0x42)),
    (0.60, (0x68, 0x78, 0x58)),
    (0.80, (0x83, 0x8C, 0x76)),   # exact shirt sage
    (0.93, (0xA8, 0xBC, 0x8C)),
    (1.00, (0xD2, 0xE0, 0xB4)),   # highlight
]

MONO = "/usr/share/fonts/truetype/jetbrainsmononerd/JetBrainsMonoNerdFontMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/jetbrainsmononerd/JetBrainsMonoNerdFontMono-Medium.ttf"
TAGLINE = "GPU PROGRAMMING   ·   STORAGE   ·   OPEN SOURCE"

ART_INK  = (0xEC, 0xF2, 0xE0)
TAG_INK  = (0xA6, 0xBA, 0x8A)


def ramp(n=256):
    ts = np.array([s[0] for s in STOPS])
    cs = np.array([s[1] for s in STOPS], float)
    x = np.linspace(0, 1, n)
    return np.stack([np.interp(x, ts, cs[:, ch]) for ch in range(3)], axis=1)


def plate():
    src = Image.open(SRC).convert("RGB")
    tile = src.crop((CROP_X, CROP_Y, CROP_X + CROP_W, CROP_Y + CROP_H))
    tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
    tile = tile.resize((W, H), Image.LANCZOS)

    a = np.asarray(tile, float)
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    t = np.clip((lum - L_LO) / (L_HI - L_LO), 0, 1)
    out = ramp()[(t * 255).round().astype(np.uint8)]

    # scrim: fade the right-hand half down so the type has clean contrast
    x = np.linspace(0, 1, W)
    k = np.clip((x - 0.34) / 0.34, 0, 1)
    out *= (1.0 - 0.42 * k)[None, :, None]
    return Image.fromarray(out.round().clip(0, 255).astype(np.uint8))


def track(d, xy, text, font, fill, extra=0.0):
    """Draw text with letter-spacing; returns total advance width."""
    x, y = xy
    for ch in text:
        if d:
            d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + extra
    return x - xy[0]


def justify_tracking(text, font, width):
    """Letter-spacing that makes `text` span exactly `width` px, first ink to last."""
    n = len(text)
    if n < 2:
        return 0.0
    natural = sum(font.getlength(c) for c in text)
    return (width - natural) / (n - 1)


def main():
    img = plate()
    d = ImageDraw.Draw(img)
    art = open("ascii_name.txt").read().rstrip("\n").split("\n")
    cols = max(len(l) for l in art)

    target_w = 830                                     # how wide the name block sits
    size = 2
    while ImageFont.truetype(MONO, size + 1).getlength("M") * cols <= target_w:
        size += 1
    f_art = ImageFont.truetype(MONO, size)
    adv = f_art.getlength("M")
    line_h = round(size * 1.02)

    block_w = adv * cols
    right = W - 96                                     # right margin
    x0 = right - block_w
    art_h = line_h * len(art)

    f_tag = ImageFont.truetype(SANS, 19)
    if JUSTIFY_TAGLINE:
        tag_extra = justify_tracking(TAGLINE, f_tag, block_w)
        tag_w = block_w                       # flush with both edges of the name
    else:
        tag_extra = TAG_TRACK
        tag_w = track(None, (0, 0), TAGLINE, f_tag, None, extra=TAG_TRACK)

    total = art_h + 30 + 24
    y0 = (H - total) // 2

    for i, line in enumerate(art):
        d.text((x0, y0 + i * line_h), line, font=f_art, fill=ART_INK)

    # rule + tagline, right-aligned to the same edge as the name
    ry = y0 + art_h + 20
    d.line([(right - tag_w, ry), (right, ry)], fill=(0x62, 0x72, 0x52), width=1)
    track(d, (right - tag_w, ry + 12), TAGLINE, f_tag, TAG_INK, extra=tag_extra)

    img.save(OUT)
    print(f"wrote {OUT} {img.size}  art size={size}px block={block_w:.0f}px tag={tag_w:.0f}px"
          f"  justify={JUSTIFY_TAGLINE} track={tag_extra:.2f}px")


if __name__ == "__main__":
    main()
