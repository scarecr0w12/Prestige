#!/usr/bin/env python3
"""Plot Prestige XP-to-next (PLAYER_NEXT_LEVEL_XP) vs current prestige level L.
Formulas match modules/Prestige/src/Prestige.cpp InitPrestigeExpTnl.
"""
from __future__ import annotations

import argparse
import math


def xp_type1(base: float, r: float, L: int) -> float:
    return base * (100.0 + (L + 1) * r) / 100.0


def xp_type2(base: float, r: float, k: float, L: int) -> float:
    if k == 0:
        return float("nan")
    return base * (1.0 + ((L + 1) * r) / 100.0) * (L * L / k)


def fmt_si(x: float) -> str:
    ax = abs(x)
    if ax >= 1e9:
        return f"{x/1e9:.1f}B"
    if ax >= 1e6:
        return f"{x/1e6:.1f}M"
    if ax >= 1e3:
        return f"{x/1e3:.0f}k"
    return f"{x:.0f}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base", type=float, default=100_000)
    p.add_argument("--r", type=float, default=5)
    p.add_argument("--k", type=float, default=5)
    p.add_argument("--max-L", type=int, default=40)
    p.add_argument(
        "--y-scale",
        choices=("log", "linear"),
        default="log",
        help="log: both curves visible; linear: best for type 2 only",
    )
    p.add_argument(
        "--show",
        choices=("both", "type2", "type1"),
        default="both",
        help="Which series to draw",
    )
    p.add_argument("-o", "--output", default="prestige_xp_per_level.svg")
    args = p.parse_args()

    Ls = list(range(0, args.max_L + 1))
    y1 = [xp_type1(args.base, args.r, L) for L in Ls]
    y2 = [xp_type2(args.base, args.r, args.k, L) for L in Ls]

    w, h = 1040, 700
    ml, mr, mt, mb = 118, 48, 100, 88
    iw, ih = w - ml - mr, h - mt - mb

    def x_px(L: int) -> float:
        if args.max_L <= 0:
            return ml
        return ml + (L / args.max_L) * iw

    use_log = args.y_scale == "log" and args.show == "both"

    positives: list[float] = []
    if args.show in ("both", "type1"):
        positives.extend(y for y in y1 if y > 0)
    if args.show in ("both", "type2"):
        positives.extend(y for y in y2 if y > 0)

    if use_log:
        ymin = min(positives) * 0.85
        ymax = max(positives) * 1.12
        ymin = max(ymin, 1.0)
        lo = math.log10(ymin)
        hi = math.log10(ymax)

        def y_px(y: float) -> float:
            if y <= 0:
                return mt + ih
            t = (math.log10(y) - lo) / (hi - lo) if hi > lo else 0.5
            return mt + ih - t * ih

        tick_vals: list[float] = []
        p10 = math.floor(lo)
        p10_hi = math.ceil(hi)
        for e in range(p10, p10_hi + 1):
            for m in (1, 2, 5):
                v = m * (10**e)
                if ymin <= v <= ymax:
                    tick_vals.append(v)
        tick_vals = sorted(set(tick_vals))
        if len(tick_vals) > 12:
            tick_vals = tick_vals[:: max(1, len(tick_vals) // 10) ]
    else:
        if args.show == "type2":
            ys_plot = [y for y in y2[1:] if not math.isnan(y)] if len(y2) > 1 else y2
            ymax = max(ys_plot) if ys_plot else 1.0
        elif args.show == "type1":
            ymax = max(y1) if y1 else 1.0
        else:
            ymax = max(max(y1), max(y2[1:]) if len(y2) > 1 else max(y2))
        ymin = 0.0
        ymax *= 1.06

        def y_px(y: float) -> float:
            if ymax <= ymin:
                return mt + ih
            return mt + ih - (y - ymin) / (ymax - ymin) * ih

        nticks = 7
        tick_vals = [ymin + (ymax - ymin) * i / (nticks - 1) for i in range(nticks)]

    def polyline_xys(xs: list[int], ys: list[float], *, skip_nonpositive: bool) -> str:
        pts = []
        for L, y in zip(xs, ys):
            if math.isnan(y) or math.isinf(y):
                continue
            if skip_nonpositive and y <= 0:
                continue
            pts.append(f"{x_px(L):.2f},{y_px(y):.2f}")
        return " ".join(pts)

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'font-family="system-ui,Segoe UI,Roboto,sans-serif">'
    )
    parts.append(f'<rect width="{w}" height="{h}" fill="#f4f6f8"/>')

    # Title block (two lines)
    parts.append(f'<text x="{w/2}" y="40" text-anchor="middle" font-size="20" font-weight="700" fill="#1a1a1a">Prestige XP required for next level</text>')
    parts.append(
        f'<text x="{w/2}" y="66" text-anchor="middle" font-size="15" fill="#444">'
        f"Base={args.base:g} · r={args.r:g} · k={args.k:g} · L = current prestige level (stored stat)"
        f"</text>"
    )
    scale_note = "Vertical axis: logarithmic — both formulas stay visible." if use_log else "Vertical axis: linear."
    parts.append(f'<text x="{w/2}" y="88" text-anchor="middle" font-size="13" fill="#555">{scale_note}</text>')

    # Plot background
    parts.append(f'<rect x="{ml}" y="{mt}" width="{iw}" height="{ih}" fill="#ffffff" stroke="#cfd8dc" stroke-width="1"/>')

    # Grid + y labels
    for tv in tick_vals:
        yy = y_px(tv)
        if not (mt <= yy <= mt + ih):
            continue
        parts.append(
            f'<line x1="{ml}" y1="{yy:.2f}" x2="{ml+iw}" y2="{yy:.2f}" stroke="#eceff1" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{ml-14}" y="{yy+5:.2f}" text-anchor="end" font-size="14" font-weight="500" fill="#37474f">{fmt_si(tv)}</text>'
        )

    # X ticks every 5 (and 0, max)
    x_step = 5 if args.max_L >= 20 else max(1, args.max_L // 8)
    x_labels = sorted(set(range(0, args.max_L + 1, x_step)) | {args.max_L})
    for L in x_labels:
        xx = x_px(L)
        parts.append(f'<line x1="{xx:.2f}" y1="{mt+ih}" x2="{xx:.2f}" y2="{mt+ih+8}" stroke="#455a64" stroke-width="1.2"/>')
        parts.append(
            f'<text x="{xx:.2f}" y="{mt+ih+30}" text-anchor="middle" font-size="14" font-weight="500" fill="#37474f">{L}</text>'
        )

    # Axes on top of grid
    parts.append(
        f'<line x1="{ml}" y1="{mt+ih}" x2="{ml+iw}" y2="{mt+ih}" stroke="#263238" stroke-width="2"/>'
    )
    parts.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ih}" stroke="#263238" stroke-width="2"/>')

    # Area fill under type 2 (linear scale only; skip for log to avoid distortion)
    if args.show in ("both", "type2") and not use_log:
        base_y = y_px(ymin)
        pts_fill = []
        for L, y in zip(Ls, y2):
            if y <= 0 or math.isnan(y):
                continue
            pts_fill.append(f"{x_px(L):.2f},{y_px(y):.2f}")
        if len(pts_fill) >= 2:
            first_L = next(L for L, y in zip(Ls, y2) if y > 0)
            last_L = Ls[-1]
            poly = (
                f"{x_px(first_L):.2f},{base_y:.2f} "
                + " ".join(pts_fill)
                + f" {x_px(last_L):.2f},{base_y:.2f}"
            )
            parts.append(f'<polygon points="{poly}" fill="#ffebee" stroke="none" opacity="0.9"/>')

    # Lines (type 2 first so type 1 draws on top when both linear — here order ok)
    skip_np = use_log or args.show == "both"
    if args.show in ("both", "type2"):
        parts.append(
            f'<polyline fill="none" stroke="#b71c1c" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round" '
            f'points="{polyline_xys(Ls, y2, skip_nonpositive=skip_np)}"/>'
        )
    if args.show in ("both", "type1"):
        parts.append(
            f'<polyline fill="none" stroke="#1565c0" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" '
            f'stroke-dasharray="10 6" points="{polyline_xys(Ls, y1, skip_nonpositive=False)}"/>'
        )

    # Axis captions
    parts.append(
        f'<text x="{ml+iw/2}" y="{h-42}" text-anchor="middle" font-size="16" font-weight="600" fill="#263238">Prestige level L (working toward L+1)</text>'
    )
    parts.append(
        f'<text transform="translate(36,{mt+ih/2}) rotate(-90)" text-anchor="middle" font-size="16" font-weight="600" fill="#263238">XP to next level</text>'
    )

    # Legend — large, high contrast
    lx, ly = ml + 16, mt + 16
    lw, lh = 420, 76 if args.show == "both" else 44
    parts.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="#ffffff" stroke="#90a4ae" stroke-width="1.5" rx="6" opacity="0.97"/>')
    if args.show in ("both", "type2"):
        parts.append(
            f'<line x1="{lx+18}" y1="{ly+26}" x2="{lx+52}" y2="{ly+26}" stroke="#b71c1c" stroke-width="3.5"/>'
        )
        parts.append(
            f'<text x="{lx+62}" y="{ly+32}" font-size="15" font-weight="600" fill="#1a1a1a">Type 2</text>'
        )
        parts.append(
            f'<text x="{lx+130}" y="{ly+32}" font-size="14" fill="#455a64">Base × (1 + (L+1)·r/100) × (L² ÷ k)</text>'
        )
    if args.show in ("both", "type1"):
        yoff = 44 if args.show == "both" else 26
        parts.append(
            f'<line x1="{lx+18}" y1="{ly+yoff}" x2="{lx+52}" y2="{ly+yoff}" stroke="#1565c0" stroke-width="3" stroke-dasharray="10 6"/>'
        )
        parts.append(
            f'<text x="{lx+62}" y="{ly+yoff+6}" font-size="15" font-weight="600" fill="#1a1a1a">Type 1</text>'
        )
        parts.append(
            f'<text x="{lx+130}" y="{ly+yoff+6}" font-size="14" fill="#455a64">Base × (100 + (L+1)·r) ÷ 100</text>'
        )

    if args.show in ("both", "type2"):
        parts.append(
            f'<text x="{ml}" y="{h-14}" font-size="13" fill="#546e7a">Note: type 2 is 0 XP at L=0 in module code (L²/k).</text>'
        )

    parts.append("</svg>")
    svg = "\n".join(parts)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg)
    print(args.output)


if __name__ == "__main__":
    main()
