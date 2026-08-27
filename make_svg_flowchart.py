#!/usr/bin/env python3
"""
Generate the gen3 pipeline flowchart as pipeline.svg.
Replicates the original layout: group boxes, stacked cylinders, correct pfsFluxReference.
"""

FILL  = '#C5DCF0'
EDGE  = '#5B9BD5'
GRP_F = '#EEF5FB'
GRP_E = '#90B8D8'
DARK  = '#1A1A1A'

# Coordinate system: 1 unit = SCL pixels; y-axis flipped (mpl y-up → SVG y-down)
SCL   = 85.0
Y_MAX = 12.75   # top of mpl viewport
Y_MIN = 1.85    # bottom of mpl viewport

SVG_W = int(6.5 * SCL)              # 552
SVG_H = int((Y_MAX - Y_MIN) * SCL) + 6  # 932  (tiny bottom margin)

def px(x): return round(x * SCL, 1)
def py(y): return round((Y_MAX - y) * SCL, 1)
def pw(w): return round(w * SCL, 1)
def ph(h): return round(h * SCL, 1)

els = []
def e(s): els.append(s)

# ── drawing helpers ────────────────────────────────────────────────────────────

def grpbox(x0, y0, x1, y1):
    """Rounded group-box background; y0 < y1 in mpl coords."""
    e(f'<rect x="{px(x0)}" y="{py(y1)}" width="{pw(x1-x0)}" height="{ph(y1-y0)}" '
      f'rx="8" fill="{GRP_F}" stroke="{GRP_E}" stroke-width="1.5"/>')


def _text_block(cx_svg, cy_svg, lines, fs):
    """Render one or more text lines centered at (cx_svg, cy_svg) in SVG coords."""
    lh = fs * 1.3
    n  = len(lines)
    y0 = cy_svg - (n - 1) * lh / 2
    for i, line in enumerate(lines):
        e(f'<text x="{cx_svg}" y="{y0 + i*lh:.1f}" text-anchor="middle" '
          f'dominant-baseline="central" font-size="{fs}" fill="{DARK}">{line}</text>')


def box(cx, cy, w, h, txt, fs=9.0):
    """Rounded rectangle task/data box."""
    e(f'<rect x="{px(cx-w/2)}" y="{py(cy+h/2)}" width="{pw(w)}" height="{ph(h)}" '
      f'rx="5" fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')
    _text_block(px(cx), py(cy), txt.split('\n'), fs)


def _drum1(cx, cy, w, bh, eh):
    """Draw one cylinder at absolute mpl coords (cx, cy)."""
    ecx  = px(cx)
    erx  = pw(w) / 2
    ery  = ph(eh) / 2
    rx_  = px(cx - w / 2)
    rw   = pw(w)
    ry_  = py(cy + bh / 2)    # top of body in SVG (smaller y)
    rh   = ph(bh)
    lx   = px(cx - w / 2)
    rx2  = px(cx + w / 2)
    yt   = py(cy + bh / 2)    # body top (SVG)
    yb   = py(cy - bh / 2)    # body bottom (SVG, larger y)

    # 1. bottom ellipse (gives depth)
    e(f'<ellipse cx="{ecx}" cy="{yb}" rx="{erx}" ry="{ery}" '
      f'fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')
    # 2. body rectangle (no stroke so sides don't bleed)
    e(f'<rect x="{rx_}" y="{ry_}" width="{rw}" height="{rh}" '
      f'fill="{FILL}" stroke="none"/>')
    # 3. side lines
    e(f'<line x1="{lx}" y1="{yt}" x2="{lx}" y2="{yb}" stroke="{EDGE}" stroke-width="1.5"/>')
    e(f'<line x1="{rx2}" y1="{yt}" x2="{rx2}" y2="{yb}" stroke="{EDGE}" stroke-width="1.5"/>')
    # 4. top ellipse (on top – the visible cap)
    e(f'<ellipse cx="{ecx}" cy="{yt}" rx="{erx}" ry="{ery}" '
      f'fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')


def drum(cx, cy, w, h, txt, copies=1, fs=9.0):
    """Stacked cylinder symbol; copies > 1 draws shadow copies behind the front one."""
    eh = h * 0.28
    bh = h * 0.72
    for k in range(copies - 1, 0, -1):
        _drum1(cx + k * 0.10, cy + k * 0.08, w, bh, eh)
    _drum1(cx, cy, w, bh, eh)
    _text_block(px(cx), py(cy), [txt], fs)


def arrow(x1, y1, x2, y2):
    e(f'<line x1="{px(x1)}" y1="{py(y1)}" x2="{px(x2)}" y2="{py(y2)}" '
      f'stroke="{DARK}" stroke-width="1.5" marker-end="url(#arr)"/>')


def polyarrow(pts):
    d = ' '.join(f'{"M" if i==0 else "L"} {px(p[0])} {py(p[1])}'
                 for i, p in enumerate(pts))
    e(f'<path d="{d}" stroke="{DARK}" stroke-width="1.5" fill="none" '
      f'marker-end="url(#arr)"/>')


# ── elements (same coordinates as make_flowchart.py) ──────────────────────────

# Group boxes drawn first (backgrounds)
grpbox(0.22, 10.40, 6.28, 11.65)   # Section 2
grpbox(0.22,  7.50, 6.28, 10.00)   # Section 3
grpbox(0.22,  2.10, 6.28,  7.05)   # Section 4

# ── SECTION 1  –  reduceExposure ──────────────────────────────────────────────
box (1.00, 12.10, 1.55, 0.72, 'raw, bias,\ndark, flat, …', fs=7.8)
box (2.95, 12.10, 1.85, 0.56, 'reduceExposure')
drum(4.90, 12.10, 1.40, 0.78, 'pfsArm')

arrow(1.78, 12.10, 2.03, 12.10)
arrow(3.88, 12.10, 4.20, 12.10)

# pfsArm (s1) → pfsArm stacked (s2) — route along right edge above s2 box
polyarrow([
    (4.90, 11.72), (4.90, 11.82), (6.35, 11.82),
    (6.35, 11.78), (1.10, 11.78), (1.10, 11.58),
])

# ── SECTION 2  –  mergeArms ───────────────────────────────────────────────────
drum(1.10, 11.00, 1.40, 0.68, 'pfsArm',   copies=4)
box (3.05, 11.00, 1.85, 0.54, 'mergeArms')
drum(5.10, 11.28, 1.40, 0.62, 'sky1d')
drum(5.10, 10.72, 1.40, 0.68, 'pfsMerged')

arrow(1.80, 11.00, 2.13, 11.00)
arrow(3.98, 11.00, 4.40, 11.28)
arrow(3.98, 11.00, 4.40, 10.72)

# pfsMerged → calculateReferenceFlux — left spine
polyarrow([
    (4.40, 10.38), (4.40, 10.22), (0.42, 10.22),
    (0.42,  9.68), (1.45,  9.68),
])

# ── SECTION 3  –  calculateReferenceFlux / fluxCalibrate ──────────────────────
box (2.70,  9.68, 2.50, 0.54, 'calculateReferenceFlux', fs=8.3)
drum(5.20,  9.68, 1.65, 0.72, 'pfsFluxReference')   # ← CORRECTED

arrow(3.95, 9.68, 4.38, 9.68)

# pfsFluxReference → fluxCalibrate — left spine
polyarrow([
    (4.38, 9.32), (4.38, 8.92), (0.27, 8.92),
    (0.27, 8.32), (1.70, 8.32),
])

box (2.60,  8.32, 1.80, 0.54, 'fluxCalibrate')
drum(5.10,  9.00, 1.55, 0.62, 'pfsCalibrated')
drum(5.10,  8.20, 1.40, 0.62, 'fluxCal')

arrow(3.50, 8.32, 4.33, 9.00)
arrow(3.50, 8.32, 4.40, 8.20)

# ── CROSS-SECTION FEEDS  →  SECTION 4 ─────────────────────────────────────────
# sky1d (s2) → sky1d stacked (s4)  — right spine
polyarrow([(5.80, 11.28), (6.38, 11.28), (6.38, 6.20), (2.20, 6.20)])

# fluxCal (s3) → fluxCal stacked (s4)  — right spine
polyarrow([(5.80,  8.20), (6.38,  8.20), (6.38, 3.80), (2.20, 3.80), (2.20, 4.72)])

# pfsArm (s2) → pfsArm stacked (s4)  — far-left spine
polyarrow([(0.40, 11.00), (0.10, 11.00), (0.10, 3.20), (0.40, 3.20)])

# ── SECTION 4  –  coaddSpectra ────────────────────────────────────────────────
drum(1.10, 6.20, 1.40, 0.62, 'sky1d',    copies=5)
drum(1.10, 4.70, 1.40, 0.62, 'fluxCal',  copies=5)
drum(1.10, 3.20, 1.40, 0.62, 'pfsArm',   copies=5)
box (3.15, 4.70, 1.90, 0.54, 'coaddSpectra')
drum(5.20, 4.70, 1.50, 0.78, 'pfsCoadd', copies=5)

arrow(1.80, 6.20, 2.20, 4.83)
arrow(1.80, 4.70, 2.20, 4.70)
arrow(1.80, 3.20, 2.20, 4.57)
arrow(4.10, 4.70, 4.45, 4.70)


# ── assemble SVG ──────────────────────────────────────────────────────────────
body = '\n'.join(f'  {el}' for el in els)

svg = f'''\
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {SVG_W} {SVG_H}"
     style="max-width:{SVG_W}px;width:100%;height:auto;background:white;display:block;font-family:Arial,Helvetica,sans-serif;">
  <defs>
    <!-- arrowhead: tip placed exactly at line endpoint via refX=10 -->
    <marker id="arr" viewBox="0 0 10 10" refX="10" refY="5"
            markerWidth="5" markerHeight="5"
            markerUnits="strokeWidth" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{DARK}"/>
    </marker>
  </defs>
{body}
</svg>
'''

out = 'docs/img/pipeline.svg'
with open(out, 'w') as f:
    f.write(svg)
print(f"Saved {SVG_W}×{SVG_H}  →  {out}")
