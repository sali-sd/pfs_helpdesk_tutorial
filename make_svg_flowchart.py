#!/usr/bin/env python3
"""
Generate the gen3 pipeline flowchart as pipeline.svg.
Pixel-based layout — no group boxes, generous section spacing, clean arrow routing.
Corrects pfsReference → pfsFluxReference.
"""

FILL  = '#C5DCF0'
EDGE  = '#5B9BD5'
DARK  = '#1A1A1A'
W     = 500
H     = 895
DX, DY = 8, 7   # stacking shadow offset per copy (right, up in SVG)

els = []
def e(s): els.append(s)


# ── text helper ────────────────────────────────────────────────────────────────
def _txt(cx, cy, lines, fs):
    lh = fs * 1.3
    n  = len(lines)
    y0 = cy - (n - 1) * lh / 2
    for i, ln in enumerate(lines):
        e(f'<text x="{cx:.1f}" y="{y0 + i*lh:.1f}" text-anchor="middle" '
          f'dominant-baseline="central" font-size="{fs}" fill="{DARK}">{ln}</text>')


# ── rounded-rectangle task box ────────────────────────────────────────────────
def box(cx, cy, w, h, txt, fs=12):
    e(f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w}" height="{h}" '
      f'rx="5" fill="{FILL}" stroke="{EDGE}" stroke-width="1.5"/>')
    _txt(cx, cy, txt.split('\n'), fs)


# ── cylinder (database drum) ───────────────────────────────────────────────────
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

def drum(cx, cy, w, h, txt, copies=1, fs=12):
    """Stacked cylinder; copies>1 draws shadow copies offset up-right."""
    for k in range(copies - 1, 0, -1):
        _drum1(cx + k * DX, cy - k * DY, w, h)
    _drum1(cx, cy, w, h)
    _txt(cx, cy, [txt], fs)


# ── arrows ─────────────────────────────────────────────────────────────────────
def arrow(x1, y1, x2, y2):
    e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
      f'stroke="{DARK}" stroke-width="1.5" marker-end="url(#arr)"/>')

def polyarrow(pts):
    d = ' '.join(f'{"M" if i == 0 else "L"} {p[0]} {p[1]}'
                 for i, p in enumerate(pts))
    e(f'<path d="{d}" stroke="{DARK}" stroke-width="1.5" fill="none" '
      f'marker-end="url(#arr)"/>')


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1  –  reduceExposure                               no group box, y=80
# ══════════════════════════════════════════════════════════════════════════════
box (110, 80, 150, 70, 'raw, bias,\ndark, flat, …', fs=10)
box (283, 80, 158, 48, 'reduceExposure')
drum(433, 80, 107, 62, 'pfsArm')

# S1 arrows
arrow(185, 80, 204, 80)           # raw → reduceExposure
arrow(362, 80, 380, 80)           # reduceExposure → pfsArm

# pfsArm (s1) → pfsArm stacked (s2):
#   From drum bottom → down → right margin → across above s2 → down into stack
polyarrow([(433, 111), (433, 150), (488, 150), (488, 175), (83, 175), (83, 200)])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2  –  mergeArms                                       y ≈ 210–275
# ══════════════════════════════════════════════════════════════════════════════
drum(83,  242, 110, 60, 'pfsArm',   copies=4)
box (257, 242, 150, 48, 'mergeArms')
drum(415, 210, 110, 55, 'sky1d')
drum(415, 274, 110, 58, 'pfsMerged')

# S2 arrows
arrow(138, 242, 182, 242)          # pfsArm_s2 → mergeArms
arrow(332, 242, 360, 210)          # mergeArms → sky1d
arrow(332, 242, 360, 274)          # mergeArms → pfsMerged

# pfsMerged (s2) → calculateReferenceFlux (s3):
#   From drum bottom → down → left margin → calcRefFlux left edge
polyarrow([(415, 303), (415, 340), (25, 340), (25, 395), (110, 395)])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3  –  calculateReferenceFlux / fluxCalibrate       y ≈ 395–530
# ══════════════════════════════════════════════════════════════════════════════
box (213, 395, 207, 48, 'calculateReferenceFlux', fs=11)
drum(415, 395, 127, 62, 'pfsFluxReference', fs=11)   # ← CORRECTED

# S3a arrows
arrow(317, 395, 352, 395)          # calculateReferenceFlux → pfsFluxReference

# pfsFluxReference → fluxCalibrate:
#   From drum bottom → left across (above pfsCalib top) → down → fluxCalib left
polyarrow([(415, 426), (25, 426), (25, 498), (129, 498)])

box (208, 498, 158, 48, 'fluxCalibrate')
drum(415, 466, 122, 54, 'pfsCalibrated')
drum(415, 530, 110, 54, 'fluxCal')

# S3b arrows
arrow(287, 498, 354, 466)          # fluxCalibrate → pfsCalibrated
arrow(287, 498, 360, 530)          # fluxCalibrate → fluxCal


# ══════════════════════════════════════════════════════════════════════════════
# CROSS-SECTION FEEDS  →  SECTION 4
# ══════════════════════════════════════════════════════════════════════════════

# sky1d (s2) → sky1d stacked (s4):  right spine → horizontal at y=618
polyarrow([(470, 210), (488, 210), (488, 618), (170, 618)])

# fluxCal (s3) → fluxCal stacked (s4):  right spine → below pfsCoadd → up
polyarrow([(470, 530), (488, 530), (488, 780), (170, 780), (170, 743)])

# pfsArm (s2) → pfsArm stacked (s4):  far-left spine
polyarrow([(28, 242), (10, 242), (10, 833), (28, 833)])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4  –  coaddSpectra                                  y ≈ 650–833
# ══════════════════════════════════════════════════════════════════════════════
drum(83,  650, 110, 56, 'sky1d',    copies=5)
drum(83,  743, 110, 56, 'fluxCal',  copies=5)
drum(83,  833, 110, 56, 'pfsArm',   copies=5)
box (250, 743, 145, 48, 'coaddSpectra')
drum(393, 743, 110, 66, 'pfsCoadd', copies=5)

# S4 arrows
arrow(138, 650, 178, 719)          # sky1d_s4  → coaddSpectra (entering near top-left)
arrow(138, 743, 178, 743)          # fluxCal_s4 → coaddSpectra (straight)
arrow(138, 833, 178, 767)          # pfsArm_s4  → coaddSpectra (entering near bottom-left)
arrow(323, 743, 338, 743)          # coaddSpectra → pfsCoadd


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
