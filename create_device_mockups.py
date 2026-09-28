#!/usr/bin/env python3
"""
Build the Mobile Portfolio mockups for pcristo.dev.

Composites a raw iPhone simulator screenshot into the transparent screen cutout
of the device frame (`mockup_iphone2.png`), producing the `<slug>-mockup.png`
files used by the Mobile Portfolio cards in index.html.

The frame is an RGBA iPhone body whose screen area is a fully transparent
"hole" enclosed by the bezel, so the screen mask is derived by flood-filling
the alpha channel from the image border and keeping whatever transparency is
left over.

Usage:
    python3 create_device_mockups.py
"""

import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

FRAME = os.path.join(HERE, "mockup_iphone2.png")

MARKETING = os.path.join(os.path.dirname(HERE), "..")

# slug -> raw simulator screenshot (iPhone 17 Pro, 1206x2622)
APPS = {
    "syncro": os.path.normpath(os.path.join(
        MARKETING, "Syncro/iphone/EN",
        "Simulator Screenshot - iPhone 17 Pro - 2026-09-07 at 11.08.35.png",
    )),
    "aqualog": os.path.normpath(os.path.join(
        MARKETING, "AquaLog/iphone/en",
        "Simulator Screenshot - iPhone 17 Pro - 2026-09-22 at 18.59.52.png",
    )),
}


def screen_mask(frame):
    """Return (mask, bbox) for the transparent screen cutout of the frame."""
    alpha = np.asarray(frame)[:, :, 3]
    transparent = alpha < 128

    # The screen is the only transparency enclosed by the bezel, so for every
    # row that contains opaque pixels the hole is the transparent run between
    # the first and the last opaque pixel.
    hole = np.zeros_like(transparent)
    for y in range(transparent.shape[0]):
        row_opaque = np.where(~transparent[y])[0]
        if row_opaque.size == 0:
            continue
        left, right = row_opaque[0], row_opaque[-1]
        hole[y, left:right + 1] = transparent[y, left:right + 1]

    ys, xs = np.where(hole)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))

    # Feather the clip using the frame's own anti-aliased edge so the
    # screenshot meets the bezel cleanly.
    cover = np.where(hole, 255 - alpha, 0).astype("uint8")
    return cover, bbox


def build(frame, frame_mask, screenshot_path, out_path):
    bbox = frame_mask[1]
    x0, y0, x1, y1 = bbox
    size = (x1 - x0 + 1, y1 - y0 + 1)

    shot = Image.open(screenshot_path).convert("RGB").resize(size, Image.Resampling.LANCZOS)

    base = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = Image.fromarray(frame_mask[0][y0:y1 + 1, x0:x1 + 1])
    base.paste(shot, (x0, y0), mask)

    Image.alpha_composite(base, frame).save(out_path, "PNG")
    print(f"created {os.path.basename(out_path)}  screen {size[0]}x{size[1]}  from {os.path.basename(screenshot_path)}")


def main():
    frame = Image.open(FRAME).convert("RGBA")
    mask = screen_mask(frame)

    for slug, screenshot in APPS.items():
        if not os.path.exists(screenshot):
            print(f"skipping {slug} - screenshot not found: {screenshot}")
            continue
        build(frame, mask, screenshot, os.path.join(HERE, f"{slug}-mockup.png"))


if __name__ == "__main__":
    main()
