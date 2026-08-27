#!/usr/bin/env python3
"""
Generate the gen3 pipeline flowchart as pipeline.svg.
Clean pixel-based layout: no group boxes, minimal-bend routing, thinner s4 drums.
Corrects pfsReference → pfsFluxReference.
"""

FILL  = '#C5DCF0'
EDGE  = '#5B9BD5'
DARK  = '#1A1A1A'
W     = 500
H     = 855
DX, DY = 6, 5   # stacking shadow offset (right, up in SVG)

els = []
def e(s): els.append(s)


def _txt(cx, cy, lines, fs):
    lh = fs * 1.3
    n  = len(lines)
    y0 = cy - (n - 1) * lh / 2
    for i, ln in enumerate(lines):
        e(f'<text x="{cx:.1f}" y="{y0 + i*lh:.1f}" text-anchor="middle" '
          f'dominant-baseline="central" font-size="{fs}" fill="{DARK}">{ln}</text>')


def box(cx, cy, w, h, txt, fs=12):
    e(f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w}" height="{h}" '
      f'rx="5" fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')
    _txt(cx, cy, txt.split('\n'), fs)


def _drum1(cx, cy, w, h):
    bh = h * 0.72; eh = h * 0.28
    yt = cy - bh / 2; yb = cy + bh / 2
    rx = w / 2;  ry = eh / 2
    e(f'<ellipse cx="{cx:.1f}" cy="{yb:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
      f'fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')
    e(f'<rect x="{cx - w/2:.1f}" y="{yt:.1f}" width="{w}" height="{bh:.2f}" '
      f'fill="{FILL}" stroke="none"/>')
    e(f'<line x1="{cx - w/2:.1f}" y1="{yt:.1f}" x2="{cx - w/2:.1f}" y2="{yb:.1f}" '
      f'stroke="{EDGE}" stroke-width="1.5"/>')
    e(f'<line x1="{cx + w/2:.1f}" y1="{yt:.1f}" x2="{cx + w/2:.1f}" y2="{yb:.1f}" '
      f'stroke="{EDGE}" stroke-width="1.5"/>')
    e(f'<ellipse cx="{cx:.1f}" cy="{yt:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
      f'fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')

def drum(cx, cy, w, h, txt, copies=1, fs=12, dx=None, dy=None):
    _dx = dx if dx is not None else DX
    _dy = dy if dy is not None else DY
    for k in range(copies - 1, 0, -1):
        _drum1(cx + k * _dx, cy - k * _dy, w, h)
    _drum1(cx, cy, w, h)
    _txt(cx, cy, [txt], fs)


def arrow(x1, y1, x2, y2):
    e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
      f'stroke="{DARK}" stroke-width="1.5" marker-end="url(#arr)"/>')

def polyarrow(pts):
    d = ' '.join(f'{"M" if i == 0 else "L"} {p[0]} {p[1]}'
                 for i, p in enumerate(pts))
    e(f'<path d="{d}" stroke="{DARK}" stroke-width="1.5" fill="none" '
      f'marker-end="url(#arr)"/>')


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1  –  reduceExposure                                          y = 80
# ══════════════════════════════════════════════════════════════════════════════
box (110, 80, 150, 70, 'raw, bias,\ndark, flat, …', fs=10)
box (283, 80, 158, 48, 'reduceExposure')
drum(433, 80, 107, 62, 'pfsArm')

arrow(185, 80, 204, 80)            # raw → reduceExposure
arrow(362, 80, 380, 80)            # reduceExposure → pfsArm

# pfsArm s1 → pfsArm s2  (down to gap, left to s2 x, down into stack)
polyarrow([(433, 111), (433, 155), (83, 155), (83, 200)])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2  –  mergeArms                                        y ≈ 210–285
# ══════════════════════════════════════════════════════════════════════════════
drum(83,  242, 110, 60, 'pfsArm',   copies=4)
box (257, 242, 150, 48, 'mergeArms')
drum(415, 210, 110, 55, 'sky1d')
drum(415, 274, 110, 58, 'pfsMerged')

arrow(138, 242, 182, 242)          # pfsArm_s2 → mergeArms
arrow(332, 242, 360, 210)          # mergeArms → sky1d
arrow(332, 242, 360, 274)          # mergeArms → pfsMerged

# pfsMerged → calculateReferenceFlux  (left from pfsMerged bottom, down, right)
polyarrow([(415, 303), (25, 303), (25, 395), (110, 395)])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3  –  calculateReferenceFlux / fluxCalibrate          y ≈ 395–543
# ══════════════════════════════════════════════════════════════════════════════
box (213, 395, 207, 48, 'calculateReferenceFlux', fs=11)
drum(415, 395, 127, 62, 'pfsFluxReference', fs=11)   # ← CORRECTED

arrow(317, 395, 352, 395)          # calculateReferenceFlux → pfsFluxReference

# pfsFluxReference → fluxCalibrate  (right margin, down, left)
polyarrow([(415, 426), (488, 426), (488, 498), (129, 498)])

box (208, 498, 158, 48, 'fluxCalibrate')
drum(415, 466, 122, 54, 'pfsCalibrated')
drum(415, 530, 110, 54, 'fluxCal')

arrow(287, 498, 354, 466)          # fluxCalibrate → pfsCalibrated
arrow(287, 498, 360, 530)          # fluxCalibrate → fluxCal


# ══════════════════════════════════════════════════════════════════════════════
# CROSS-SECTION FEEDS  →  SECTION 4
# ══════════════════════════════════════════════════════════════════════════════

# sky1d (s2) → sky1d s4:  right margin down to s4 level, left into stack
polyarrow([(470, 210), (488, 210), (488, 607), (162, 607)])

# fluxCal (s3) → fluxCal s4:  right margin down past pfsCoadd, up into stack
polyarrow([(470, 530), (488, 530), (488, 752), (162, 752), (162, 715)])

# pfsArm (s2) → pfsArm s4:  far-left spine
polyarrow([(28, 242), (10, 242), (10, 797), (28, 797)])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4  –  coaddSpectra         (thinner drums: h=45, dx=6, dy=5)
# ══════════════════════════════════════════════════════════════════════════════
drum(83,  630, 110, 45, 'sky1d',    copies=5, dx=6, dy=5)
drum(83,  715, 110, 45, 'fluxCal',  copies=5, dx=6, dy=5)
drum(83,  797, 110, 45, 'pfsArm',   copies=5, dx=6, dy=5)
box (255, 715, 150, 48, 'coaddSpectra')
drum(393, 715, 110, 62, 'pfsCoadd', copies=5, dx=6, dy=5)

# s4 input drums → coaddSpectra  (fan into box at different entry heights)
arrow(138, 630, 180, 703)          # sky1d_s4  → coaddSpectra near top-left
arrow(138, 715, 180, 715)          # fluxCal_s4 → coaddSpectra centre
arrow(138, 797, 180, 727)          # pfsArm_s4  → coaddSpectra near bottom-left
arrow(330, 715, 338, 715)          # coaddSpectra → pfsCoadd


# ══════════════════════════════════════════════════════════════════════════════
# ASSEMBLE SVG
# ══════════════════════════════════════════════════════════════════════════════
body = '\n'.join(f'  {el}' for el in els)

svg = f'''\
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {H}"
     style="max-width:{W}px;width:100%;height:auto;background:white;display:block;font-family:Arial,Helvetica,sans-serif;">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="10" refY="5"
            markerWidth="5" markerHeight="5" markerUnits="strokeWidth" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="{DARK}"/>
    </marker>
  </defs>
{body}
</svg>
'''

out = 'docs/img/pipeline.svg'
with open(out, 'w') as f:
    f.write(svg)
print(f"Saved {W}×{H}  →  {out}")
