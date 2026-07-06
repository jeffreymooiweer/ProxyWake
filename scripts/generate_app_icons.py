#!/usr/bin/env python3
"""Generate frontend/public icon assets from docs/assets/icon.png."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'docs' / 'assets' / 'icon.png'
OUTPUT_DIR = ROOT / 'frontend' / 'public'

# UI logo (header, login, waiting page) — higher resolution for crisp display
LOGO_SIZE = 512

SIZES = {
    'icon-16.png': 16,
    'icon-32.png': 32,
    'icon-48.png': 48,
    'icon-180.png': 180,
    'icon-192.png': 192,
    'apple-touch-icon.png': 180,
    'icon-512.png': 512,
    'icon.png': 192,
    'favicon.png': 32,
    'proxywake.png': LOGO_SIZE,
}


def square_crop(image: Image.Image) -> Image.Image:
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def write_png(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format='PNG', optimize=True)


def write_ico(path: Path, image: Image.Image) -> None:
    frames = [image.resize((size, size), Image.Resampling.LANCZOS) for size in (16, 32, 48)]
    frames[0].save(path, format='ICO', sizes=[(frame.width, frame.height) for frame in frames])


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f'Source icon not found: {SOURCE}')

    source = Image.open(SOURCE).convert('RGBA')
    square = square_crop(source)

    for filename, size in SIZES.items():
        resized = square.resize((size, size), Image.Resampling.LANCZOS)
        write_png(OUTPUT_DIR / filename, resized)
        print(f'Wrote {filename} ({size}x{size})')

    write_ico(OUTPUT_DIR / 'favicon.ico', square)
    print('Wrote favicon.ico')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
