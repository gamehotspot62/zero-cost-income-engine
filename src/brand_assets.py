"""Custom Quantum Neural Pulse AI brand logo, SVG vector assets, and pure-stdlib PNG/ICO favicons."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="StackPulse AI Logo">
  <defs>
    <linearGradient id="spHexGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#22c55e"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
    <radialGradient id="spCoreGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.38"/>
      <stop offset="65%" stop-color="#6366f1" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#070b14" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="spPulseGrad" x1="0%" y1="50%" x2="100%" y2="50%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#22c55e"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="60" height="60" rx="15" fill="#070b14" stroke="url(#spHexGrad)" stroke-width="2.5"/>
  <circle cx="32" cy="32" r="24" fill="url(#spCoreGlow)"/>
  <polygon points="32,9 51,20 51,44 32,55 13,44 13,20" fill="rgba(15,23,42,0.85)" stroke="url(#spHexGrad)" stroke-width="2.2" stroke-linejoin="round"/>
  <path d="M21 23 L32 17 L43 23" fill="none" stroke="#38bdf8" stroke-width="1.6" stroke-linecap="round" stroke-opacity="0.7"/>
  <path d="M21 41 L32 47 L43 41" fill="none" stroke="#22c55e" stroke-width="1.6" stroke-linecap="round" stroke-opacity="0.7"/>
  <polyline points="14,34 22,34 27,21 34,44 40,28 45,34 50,34" fill="none" stroke="url(#spPulseGrad)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="14" cy="34" r="2.6" fill="#38bdf8"/>
  <circle cx="27" cy="21" r="2.2" fill="#f8fafc"/>
  <circle cx="34" cy="44" r="2.2" fill="#22c55e"/>
  <circle cx="50" cy="34" r="2.6" fill="#22c55e"/>
</svg>
"""

BRAND_LOGO_SVG = """<svg class="sp-logo-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="36" height="36" aria-hidden="true">
  <defs>
    <linearGradient id="spNavGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#22c55e"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
    <linearGradient id="spNavPulse" x1="0%" y1="50%" x2="100%" y2="50%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#22c55e"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="60" height="60" rx="15" fill="#070b14" stroke="url(#spNavGrad)" stroke-width="2.5"/>
  <polygon points="32,9 51,20 51,44 32,55 13,44 13,20" fill="#0f172a" stroke="url(#spNavGrad)" stroke-width="2.2" stroke-linejoin="round"/>
  <polyline points="14,34 22,34 27,21 34,44 40,28 45,34 50,34" fill="none" stroke="url(#spNavPulse)" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="14" cy="34" r="2.6" fill="#38bdf8"/>
  <circle cx="50" cy="34" r="2.6" fill="#22c55e"/>
</svg>"""

HERO_EMBLEM_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="96" height="96" role="img" aria-label="StackPulse AI Quantum Neural Core">
  <defs>
    <linearGradient id="spHeroRing" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#22c55e"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
    <radialGradient id="spHeroGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.45"/>
      <stop offset="60%" stop-color="#22c55e" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#070b14" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <circle cx="60" cy="60" r="56" fill="url(#spHeroGlow)"/>
  <circle cx="60" cy="60" r="50" fill="none" stroke="url(#spHeroRing)" stroke-width="1.5" stroke-dasharray="6 6" opacity="0.65">
    <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="22s" repeatCount="indefinite"/>
  </circle>
  <polygon points="60,16 98,38 98,82 60,104 22,82 22,38" fill="#0b1222" stroke="url(#spHeroRing)" stroke-width="3" stroke-linejoin="round"/>
  <polygon points="60,26 89,43 89,77 60,94 31,77 31,43" fill="none" stroke="#38bdf8" stroke-width="1.2" opacity="0.45"/>
  <polyline points="24,62 38,62 47,39 58,83 69,48 78,62 96,62" fill="none" stroke="url(#spHeroRing)" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="24,62 38,62 47,39 58,83 69,48 78,62 96,62" fill="none" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>
  <circle cx="24" cy="62" r="4" fill="#38bdf8"/>
  <circle cx="47" cy="39" r="3.5" fill="#f8fafc"/>
  <circle cx="58" cy="83" r="3.5" fill="#22c55e"/>
  <circle cx="96" cy="62" r="4" fill="#22c55e"/>
</svg>"""


def head_favicon_links(root_prefix: str = "") -> str:
    """Return cross-browser favicon and Apple touch icon HTML link tags."""
    return (
        f'<link rel="icon" type="image/svg+xml" href="{root_prefix}assets/favicon.svg" />\n'
        f'  <link rel="icon" type="image/png" sizes="64x64" href="{root_prefix}assets/favicon.png" />\n'
        f'  <link rel="shortcut icon" href="{root_prefix}favicon.ico" />\n'
        f'  <link rel="apple-touch-icon" href="{root_prefix}assets/favicon.png" />'
    )


def _dist_to_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    dx, dy = x2 - x1, y2 - y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg_len_sq))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _blend(dst: tuple[int, int, int, int], src: tuple[int, int, int, int], alpha: float) -> tuple[int, int, int, int]:
    a = max(0.0, min(1.0, alpha)) * (src[3] / 255.0)
    if a <= 0.0:
        return dst
    inv = 1.0 - a
    r = int(round(src[0] * a + dst[0] * inv))
    g = int(round(src[1] * a + dst[1] * inv))
    b = int(round(src[2] * a + dst[2] * inv))
    out_a = int(round(min(255.0, dst[3] + a * (255.0 - dst[3]))))
    return (r, g, b, out_a)


def _render_favicon_png_bytes(size: int = 64) -> bytes:
    """Render an anti-aliased 64x64 RGBA PNG of the Quantum Neural Pulse logo using pure stdlib."""
    hex_pts = [
        (32.0, 9.0),
        (51.0, 20.0),
        (51.0, 44.0),
        (32.0, 55.0),
        (13.0, 44.0),
        (13.0, 20.0),
    ]
    pulse_pts = [
        (14.0, 34.0),
        (22.0, 34.0),
        (27.0, 21.0),
        (34.0, 44.0),
        (40.0, 28.0),
        (45.0, 34.0),
        (50.0, 34.0),
    ]
    nodes = [(14.0, 34.0), (27.0, 21.0), (34.0, 44.0), (50.0, 34.0)]

    rows: list[bytes] = []
    for y in range(size):
        row = bytearray([0])  # PNG filter type 0
        py = y + 0.5
        for x in range(size):
            px = x + 0.5
            # Rounded square signed distance
            cx, cy = abs(px - 32.0), abs(py - 32.0)
            qx, qy = max(cx - 15.0, 0.0), max(cy - 15.0, 0.0)
            sdf_box = math.hypot(qx, qy) - 15.0
            if sdf_box > 1.2:
                row.extend((0, 0, 0, 0))
                continue

            cov = max(0.0, min(1.0, 1.0 - sdf_box))
            # Obsidian background + central cyan-indigo glow
            d_center = math.hypot(px - 32.0, py - 32.0)
            glow = max(0.0, 1.0 - d_center / 28.0) ** 2
            pixel = (
                int(7 + 34 * glow),
                int(11 + 78 * glow),
                int(20 + 115 * glow),
                int(round(255 * cov)),
            )

            # Diagonal gradient color (cyan -> emerald -> indigo)
            grad_t = max(0.0, min(1.0, (px + py) / 128.0))
            if grad_t < 0.5:
                k = grad_t * 2.0
                grad_rgb = (
                    int(56 + (34 - 56) * k),
                    int(189 + (197 - 189) * k),
                    int(248 + (94 - 248) * k),
                )
            else:
                k = (grad_t - 0.5) * 2.0
                grad_rgb = (
                    int(34 + (129 - 34) * k),
                    int(197 + (140 - 197) * k),
                    int(94 + (248 - 94) * k),
                )

            # Outer rounded-square border
            if abs(sdf_box + 1.2) < 1.8:
                border_a = max(0.0, 1.0 - abs(sdf_box + 1.2) / 1.8) * 0.9
                pixel = _blend(pixel, (*grad_rgb, 255), border_a)

            # Hexagon frame
            min_hex_d = min(
                _dist_to_segment(px, py, hex_pts[i][0], hex_pts[i][1], hex_pts[(i + 1) % 6][0], hex_pts[(i + 1) % 6][1])
                for i in range(6)
            )
            if min_hex_d < 2.1:
                hex_a = max(0.0, 1.0 - max(0.0, min_hex_d - 0.6) / 1.5)
                pixel = _blend(pixel, (*grad_rgb, 255), hex_a)

            # Neural pulse waveform with crisp luminous core
            min_pulse_d = min(
                _dist_to_segment(px, py, pulse_pts[i][0], pulse_pts[i][1], pulse_pts[i + 1][0], pulse_pts[i + 1][1])
                for i in range(len(pulse_pts) - 1)
            )
            if min_pulse_d < 3.4:
                halo_a = max(0.0, 1.0 - min_pulse_d / 3.4) * 0.55
                pixel = _blend(pixel, (56, 189, 248, 255), halo_a)
            if min_pulse_d < 1.8:
                core_a = max(0.0, 1.0 - max(0.0, min_pulse_d - 0.6) / 1.2)
                pixel = _blend(pixel, (248, 250, 252, 255), core_a)

            # Synaptic endpoint & vertex dots
            for idx, (nx, ny) in enumerate(nodes):
                nd = math.hypot(px - nx, py - ny)
                if nd < 2.8:
                    dot_rgb = (56, 189, 248) if idx == 0 else (248, 250, 252) if idx == 1 else (34, 197, 94)
                    dot_a = max(0.0, 1.0 - max(0.0, nd - 1.4) / 1.4)
                    pixel = _blend(pixel, (*dot_rgb, 255), dot_a)

            row.extend(pixel)
        rows.append(bytes(row))

    raw_scanlines = b"".join(rows)

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw_scanlines, level=9)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def _wrap_png_as_ico(png_bytes: bytes, size: int = 64) -> bytes:
    """Wrap a PNG icon inside a standard single-image ICO container."""
    dim = size if size < 256 else 0
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png_bytes), 22)
    return header + entry + png_bytes


def build_brand_assets(dist_dir: Path) -> None:
    """Write SVG, PNG, and ICO brand logo and browser tab favicon files into dist/."""
    assets_dir = dist_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    (assets_dir / "logo.svg").write_text(FAVICON_SVG, encoding="utf-8")
    png_bytes = _render_favicon_png_bytes(64)
    (assets_dir / "favicon.png").write_bytes(png_bytes)
    (dist_dir / "favicon.ico").write_bytes(_wrap_png_as_ico(png_bytes, 64))
