#!/usr/bin/env python3
"""Generate all animated SVG assets for the space-themed GitHub profile README."""
import math
import random
import os
import xml.dom.minidom

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

# ---------- shared palette ----------
SPACE_BLACK = "#030614"
PANEL = "#0A0F24"
INDIGO = "#1B2735"
PURPLE = "#6E48AA"
PURPLE_BRIGHT = "#A78BFA"
VIOLET = "#7C3AED"
CYAN = "#22D3EE"
CYAN_BRIGHT = "#7DF9FF"
PINK = "#F472B6"
GOLD = "#FBBF24"
STAR_WHITE = "#E0E7FF"
MUTED = "#8B949E"

SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'Courier New',ui-monospace,Menlo,Consolas,monospace"
CW = 0.6  # monospace advance ratio (em)


def stars(n, x0, y0, x1, y1, seed, rmin=0.7, rmax=1.6, colors=None, omin=0.15, omax=1.0):
    """Twinkling star circles scattered in a box."""
    rng = random.Random(seed)
    colors = colors or [STAR_WHITE, STAR_WHITE, CYAN_BRIGHT, PURPLE_BRIGHT]
    out = []
    for _ in range(n):
        x = round(rng.uniform(x0, x1), 1)
        y = round(rng.uniform(y0, y1), 1)
        r = round(rng.uniform(rmin, rmax), 2)
        c = rng.choice(colors)
        dur = round(rng.uniform(2.0, 5.5), 2)
        beg = round(-rng.uniform(0, dur), 2)
        out.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}">'
            f'<animate attributeName="opacity" values="{omin};{omax};{omin}" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    return "\n".join(out)


def sparkles(coords, seed=7, size=5.0, color=STAR_WHITE):
    """Plus-shaped sparkle stars that pulse-scale."""
    rng = random.Random(seed)
    out = []
    for (x, y) in coords:
        dur = round(rng.uniform(2.4, 4.6), 2)
        beg = round(-rng.uniform(0, dur), 2)
        s = size
        out.append(
            f'<g transform="translate({x} {y})" opacity="0.9">'
            f'<path d="M0 {-s} C 0.6 {-s*0.25}, {s*0.25} -0.6, {s} 0 C {s*0.25} 0.6, 0.6 {s*0.25}, 0 {s} '
            f'C -0.6 {s*0.25}, {-s*0.25} 0.6, {-s} 0 C {-s*0.25} -0.6, -0.6 {-s*0.25}, 0 {-s} Z" fill="{color}">'
            f'<animateTransform attributeName="transform" type="scale" values="0.45;1;0.45" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.25;1;0.25" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
            f"</path></g>"
        )
    return "\n".join(out)


def shooting_star(p0, p1, total=16.0, start=0.05, flight=1.4, tail=90):
    """A meteor streaking p0->p1 during a small slice of a long loop."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ang = math.degrees(math.atan2(dy, dx))
    s0 = start
    s1 = min(start + flight / total, 0.999)
    return f"""<g opacity="0">
  <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{s0:.4f};{s0+0.008:.4f};{s1-0.01:.4f};{s1:.4f};1" dur="{total}s" repeatCount="indefinite"/>
  <animateMotion path="M {p0[0]} {p0[1]} L {p1[0]} {p1[1]}" keyPoints="0;0;1;1" keyTimes="0;{s0:.4f};{s1:.4f};1" calcMode="linear" dur="{total}s" repeatCount="indefinite"/>
  <g transform="rotate({ang:.1f})">
    <line x1="0" y1="0" x2="-{tail}" y2="0" stroke="url(#meteorTail)" stroke-width="2.2" stroke-linecap="round"/>
    <circle r="2.6" fill="#FFFFFF"/>
    <circle r="5" fill="#FFFFFF" opacity="0.28"/>
  </g>
</g>"""


COMMON_DEFS = f"""
<linearGradient id="meteorTail" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="-90" y2="0">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/>
  <stop offset="0.35" stop-color="{CYAN_BRIGHT}" stop-opacity="0.5"/>
  <stop offset="1" stop-color="{CYAN_BRIGHT}" stop-opacity="0"/>
</linearGradient>
<filter id="softGlow" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="4" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="bigGlow" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="9" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
"""


# =====================================================================
# 1. HERO — solar system banner
# =====================================================================
def gen_hero():
    W, H = 900, 430
    defs = COMMON_DEFS + f"""
<radialGradient id="heroBg" cx="50%" cy="18%" r="95%">
  <stop offset="0" stop-color="#101736"/>
  <stop offset="0.5" stop-color="#081022"/>
  <stop offset="1" stop-color="{SPACE_BLACK}"/>
</radialGradient>
<radialGradient id="nebPurple" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.55"/>
  <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="nebPink" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="{PINK}" stop-opacity="0.4"/>
  <stop offset="1" stop-color="{PINK}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="nebCyan" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0.35"/>
  <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{STAR_WHITE}"/>
  <stop offset="0.45" stop-color="{PURPLE_BRIGHT}"/>
  <stop offset="1" stop-color="{CYAN_BRIGHT}"/>
</linearGradient>
<linearGradient id="shimmer" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
  <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.75"/>
  <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
</linearGradient>
<radialGradient id="sunCore" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FFF7D6"/>
  <stop offset="0.55" stop-color="{GOLD}"/>
  <stop offset="1" stop-color="#F59E0B"/>
</radialGradient>
<radialGradient id="sunHalo" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="{GOLD}" stop-opacity="0.5"/>
  <stop offset="0.6" stop-color="#F59E0B" stop-opacity="0.18"/>
  <stop offset="1" stop-color="#F59E0B" stop-opacity="0"/>
</radialGradient>
<radialGradient id="earthG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#7DD3FC"/>
  <stop offset="0.55" stop-color="#3B82F6"/>
  <stop offset="1" stop-color="#1E3A8A"/>
</radialGradient>
<radialGradient id="marsG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#FCA5A5"/><stop offset="1" stop-color="#B91C1C"/>
</radialGradient>
<radialGradient id="venusG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#FDE68A"/><stop offset="1" stop-color="#D97706"/>
</radialGradient>
<radialGradient id="mercuryG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#E5E7EB"/><stop offset="1" stop-color="#6B7280"/>
</radialGradient>
<radialGradient id="jupiterG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#F5D0A9"/><stop offset="1" stop-color="#B4713D"/>
</radialGradient>
<radialGradient id="saturnG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#F3E0B5"/><stop offset="1" stop-color="#C09B5B"/>
</radialGradient>
<radialGradient id="uranusG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#CFFAFE"/><stop offset="1" stop-color="#0891B2"/>
</radialGradient>
<radialGradient id="neptuneG" cx="35%" cy="35%" r="80%">
  <stop offset="0" stop-color="#A5B4FC"/><stop offset="1" stop-color="#4338CA"/>
</radialGradient>
<clipPath id="heroClip"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>
"""
    # nebulas
    nebulas = f"""
<g clip-path="url(#heroClip)">
<ellipse cx="150" cy="90" rx="290" ry="150" fill="url(#nebPurple)">
  <animateTransform attributeName="transform" type="translate" values="0 0; 42 16; 0 0" dur="19s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
  <animate attributeName="opacity" values="0.7;1;0.7" dur="13s" repeatCount="indefinite"/>
</ellipse>
<ellipse cx="760" cy="140" rx="260" ry="140" fill="url(#nebPink)">
  <animateTransform attributeName="transform" type="translate" values="0 0; -36 20; 0 0" dur="23s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
  <animate attributeName="opacity" values="0.65;1;0.65" dur="16s" repeatCount="indefinite"/>
</ellipse>
<ellipse cx="480" cy="380" rx="330" ry="130" fill="url(#nebCyan)" opacity="0.5">
  <animate attributeName="opacity" values="0.35;0.6;0.35" dur="15s" repeatCount="indefinite"/>
</ellipse>
"""
    star_field = stars(64, 8, 8, W - 8, H - 8, seed=42) + "\n" + sparkles(
        [(84, 52), (818, 66), (700, 250), (120, 300), (452, 40), (860, 330)], seed=9
    )

    meteors = "\n".join([
        shooting_star((-80, 60), (980, 210), total=17, start=0.04),
        shooting_star((-60, 20), (940, 150), total=17, start=0.42, tail=70),
        shooting_star((180, -30), (1010, 260), total=17, start=0.74, tail=110),
    ])

    # --- solar band ---
    sun = f"""
<g>
  <circle cx="86" cy="336" r="86" fill="url(#sunHalo)">
    <animate attributeName="opacity" values="0.65;1;0.65" dur="4.2s" repeatCount="indefinite"/>
  </circle>
  <g>
    <animateTransform attributeName="transform" type="rotate" from="0 86 336" to="360 86 336" dur="70s" repeatCount="indefinite"/>
    {''.join(f'<line x1="{86 + 44*math.cos(math.radians(a)):.1f}" y1="{336 + 44*math.sin(math.radians(a)):.1f}" x2="{86 + 58*math.cos(math.radians(a)):.1f}" y2="{336 + 58*math.sin(math.radians(a)):.1f}" stroke="{GOLD}" stroke-width="2.4" stroke-linecap="round" opacity="0.75"/>' for a in range(0, 360, 30))}
  </g>
  <circle cx="86" cy="336" r="34" fill="url(#sunCore)" filter="url(#softGlow)">
    <animate attributeName="r" values="34;36;34" dur="4.2s" repeatCount="indefinite"/>
  </circle>
</g>
"""
    # orbit arcs around the sun
    orbit_radii = [88, 143, 208, 268, 358, 478, 588, 678]
    orbits = "\n".join(
        f'<circle cx="86" cy="336" r="{r}" fill="none" stroke="{CYAN_BRIGHT}" stroke-opacity="0.10" stroke-width="1" stroke-dasharray="2 7">'
        f'<animate attributeName="stroke-dashoffset" from="0" to="90" dur="{40+i*8}s" repeatCount="indefinite"/></circle>'
        for i, r in enumerate(orbit_radii)
    )

    def planet(x, r, fill, dur, extra="", beg=0.0):
        return f"""<g transform="translate({x} 336)">
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0; 0 -7; 0 0" dur="{dur}s" begin="{beg}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
    <circle r="{r+4}" fill="{fill.replace('url(#','url(#') if fill.startswith('url') else fill}" opacity="0.18"/>
    <circle r="{r}" fill="{fill}"/>
    {extra}
  </g>
</g>"""

    jup_bands = f'<path d="M -13 -5 Q 0 -8 13 -5" stroke="#8a5a2b" stroke-width="2" fill="none" opacity="0.55"/><path d="M -15 2 Q 0 -1 15 2" stroke="#8a5a2b" stroke-width="2.4" fill="none" opacity="0.5"/><path d="M -12 8 Q 0 6 12 8" stroke="#e8c496" stroke-width="1.8" fill="none" opacity="0.6"/>'
    saturn_ring = f'<ellipse rx="27" ry="8" fill="none" stroke="#D9C08C" stroke-width="2.6" transform="rotate(-18)" opacity="0.9"/><ellipse rx="21" ry="5.6" fill="none" stroke="#efe0bd" stroke-width="1" transform="rotate(-18)" opacity="0.55"/>'
    earth_moon = f'<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="7s" repeatCount="indefinite"/><circle cx="16" cy="0" r="2.6" fill="#CBD5E1"/></g>'
    uranus_ring = '<ellipse rx="15" ry="4.6" fill="none" stroke="#a5f3fc" stroke-width="1.2" transform="rotate(70)" opacity="0.6"/>'

    planets = "\n".join([
        planet(174, 5, "url(#mercuryG)", 5.2, beg=-1),
        planet(229, 7.5, "url(#venusG)", 6.1, beg=-2.5),
        planet(294, 9, "url(#earthG)", 5.6, extra=earth_moon + f'<path d="M -4 -5 Q -1 -7 2 -4 Q 5 -2 3 1 Q -2 3 -5 0 Q -6 -3 -4 -5 Z" fill="#4ADE80" opacity="0.85"/><path d="M 2 4 q 3 -1 4 1 q -2 2 -4 1 z" fill="#4ADE80" opacity="0.8"/>', beg=0),
        planet(354, 6.5, "url(#marsG)", 6.6, beg=-3.4),
        planet(444, 17, "url(#jupiterG)", 7.6, extra=jup_bands, beg=-1.8),
        planet(564, 14, "url(#saturnG)", 8.2, extra=saturn_ring, beg=-4.2),
        planet(674, 9.5, "url(#uranusG)", 7.1, extra=uranus_ring, beg=-2.2),
        planet(764, 9, "url(#neptuneG)", 6.4, beg=-5),
    ])

    pluto = f"""<g transform="translate(842 336)">
  <circle r="2.6" fill="#C4B5FD"><animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/></circle>
  <text x="0" y="16" text-anchor="middle" font-family="{MONO}" font-size="7.5" fill="{MUTED}" opacity="0.85">pluto</text>
  <text x="0" y="25" text-anchor="middle" font-family="{MONO}" font-size="6.5" fill="{MUTED}" opacity="0.6">(still counts)</text>
</g>"""

    you_are_here = f"""<g font-family="{MONO}">
  <text x="294" y="288" text-anchor="middle" font-size="12.5" fill="{CYAN_BRIGHT}" letter-spacing="1">you are here</text>
  <path d="M 294 296 l -5 -8 h 10 z" fill="{CYAN_BRIGHT}" transform="rotate(180 294 292)">
    <animate attributeName="opacity" values="1;0.15;1" dur="1.3s" repeatCount="indefinite"/>
  </path>
</g>"""

    ufo = f"""<g>
  <animateMotion path="M -70 66 C 220 34, 430 96, 640 58 C 780 38, 900 70, 980 52" dur="27s" repeatCount="indefinite"/>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="2.3s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
    <ellipse rx="17" ry="6" fill="#94A3B8"/>
    <ellipse rx="17" ry="6" fill="url(#nebCyan)" opacity="0.6"/>
    <path d="M -8 -4 a 8 6 0 0 1 16 0 z" fill="#67E8F9" opacity="0.85"/>
    <circle cx="-9" cy="1.5" r="1.4" fill="{PINK}"><animate attributeName="opacity" values="1;0.1;1" dur="0.8s" repeatCount="indefinite"/></circle>
    <circle cx="0" cy="2.6" r="1.4" fill="{GOLD}"><animate attributeName="opacity" values="0.1;1;0.1" dur="0.8s" repeatCount="indefinite"/></circle>
    <circle cx="9" cy="1.5" r="1.4" fill="#4ADE80"><animate attributeName="opacity" values="1;0.1;1" dur="1.1s" repeatCount="indefinite"/></circle>
  </g>
</g>"""

    title = f"""
<g>
  <text x="450" y="152" text-anchor="middle" font-family="{SANS}" font-size="63" font-weight="800" letter-spacing="7" fill="url(#nameGrad)" filter="url(#softGlow)">ROHIT RAWAT</text>
  <clipPath id="nameClip"><text x="450" y="152" text-anchor="middle" font-family="{SANS}" font-size="63" font-weight="800" letter-spacing="7">ROHIT RAWAT</text></clipPath>
  <g clip-path="url(#nameClip)">
    <rect x="-260" y="80" width="150" height="100" fill="url(#shimmer)" transform="skewX(-18)">
      <animateTransform attributeName="transform" type="translate" from="-200 0" to="1250 0" dur="5.5s" repeatCount="indefinite" additive="sum"/>
    </rect>
  </g>
  <text x="450" y="196" text-anchor="middle" font-family="{MONO}" font-size="15.5" letter-spacing="6" fill="{CYAN_BRIGHT}">NAVIGATING THE CODE UNIVERSE
    <animate attributeName="opacity" values="0.65;1;0.65" dur="3.6s" repeatCount="indefinite"/>
  </text>
  <g opacity="0.9">
    <line x1="290" y1="218" x2="430" y2="218" stroke="{PURPLE_BRIGHT}" stroke-width="1" opacity="0.5"/>
    <line x1="470" y1="218" x2="610" y2="218" stroke="{CYAN}" stroke-width="1" opacity="0.5"/>
    <path d="M 450 212 l 4.5 6 l -4.5 6 l -4.5 -6 z" fill="none" stroke="{PURPLE_BRIGHT}" stroke-width="1.2">
      <animateTransform attributeName="transform" type="rotate" from="0 450 218" to="360 450 218" dur="9s" repeatCount="indefinite"/>
    </path>
  </g>
</g>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}" role="img" aria-label="Rohit Rawat, navigating the code universe">
<defs>{defs}</defs>
<rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="url(#heroBg)"/>
{nebulas}
{star_field}
{meteors}
{orbits}
{sun}
{planets}
{pluto}
{you_are_here}
{ufo}
{title}
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#26315c" stroke-opacity="0.55"/>
</svg>"""
    return svg


# =====================================================================
# 2. TYPING — terminal typing animation
# =====================================================================
def gen_typing():
    W, H = 720, 70
    FS = 16.5
    cw = FS * CW
    prompt = "rohit@universe:~$ "
    phrases = [
        "Full-Stack Developer",
        "Laravel | Java | React | Golang",
        "Building scalable galaxies of code",
        "sudo deploy --target=production",
    ]
    pad_x = 22
    text_y = 44
    prompt_w = len(prompt) * cw
    start_x = pad_x + 58 + prompt_w  # 58 = traffic lights zone

    TYPE_S, HOLD_S, DEL_S, GAP_S = 0.072, 1.75, 0.03, 0.28
    spans = []
    t = 0.35  # initial idle
    for p in phrases:
        n = len(p)
        t0 = t
        type_end = t0 + n * TYPE_S
        hold_end = type_end + HOLD_S
        del_end = hold_end + n * DEL_S
        t = del_end + GAP_S
        spans.append((p, t0, type_end, hold_end, del_end))
    T = t + 0.2

    def kt(x):
        return f"{max(0.0, min(1.0, x / T)):.5f}"

    groups = []
    for i, (p, t0, te, he, de) in enumerate(spans):
        n = len(p)
        # gate opacity
        if t0 <= 0.001:
            gate_v, gate_k = "1;0", f"0;{kt(de)}"
        else:
            gate_v, gate_k = "0;1;0", f"0;{kt(t0)};{kt(de)}"
        # clip width + cursor x keyframes
        times, widths = [0.0], [0.0]
        for k in range(n + 1):
            times.append(t0 + k * TYPE_S)
            widths.append(k * cw)
        times.append(he)
        widths.append(n * cw)
        for k in range(1, n + 1):
            times.append(he + k * DEL_S)
            widths.append((n - k) * cw)
        times.append(T)
        widths.append(0.0)
        ktimes = ";".join(kt(x) for x in times)
        wvals = ";".join(f"{w:.1f}" for w in widths)
        xvals = ";".join(f"{start_x + w:.1f}" for w in widths)
        groups.append(f"""<g opacity="0">
  <animate attributeName="opacity" values="{gate_v}" keyTimes="{gate_k}" calcMode="discrete" dur="{T:.3f}s" repeatCount="indefinite"/>
  <clipPath id="tclip{i}"><rect x="{start_x}" y="{text_y-20}" y2="0" width="0" height="30">
    <animate attributeName="width" values="{wvals}" keyTimes="{ktimes}" calcMode="discrete" dur="{T:.3f}s" repeatCount="indefinite"/>
  </rect></clipPath>
  <text x="{start_x}" y="{text_y}" font-family="{MONO}" font-size="{FS}" fill="{STAR_WHITE}" clip-path="url(#tclip{i})" xml:space="preserve">{p.replace('&','&amp;').replace('<','&lt;')}</text>
  <rect x="{start_x}" y="{text_y-15}" width="9" height="19" fill="{CYAN_BRIGHT}">
    <animate attributeName="x" values="{xvals}" keyTimes="{ktimes}" calcMode="discrete" dur="{T:.3f}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0.15;0.15;1" dur="0.95s" repeatCount="indefinite"/>
  </rect>
</g>""")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Full-stack developer: Laravel, Java, React, Golang">
<defs>
<linearGradient id="termEdge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{PURPLE}"/><stop offset="1" stop-color="{CYAN}"/>
</linearGradient>
</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{PANEL}" stroke="url(#termEdge)" stroke-opacity="0.65"/>
<rect x="1" y="1" width="{W-2}" height="24" rx="12" fill="#0D1430"/>
<rect x="1" y="14" width="{W-2}" height="11" fill="#0D1430"/>
<circle cx="{pad_x}" cy="13" r="4.5" fill="#FF5F57"/>
<circle cx="{pad_x+16}" cy="13" r="4.5" fill="#FEBC2E"/>
<circle cx="{pad_x+32}" cy="13" r="4.5" fill="#28C840"><animate attributeName="opacity" values="1;0.4;1" dur="2.2s" repeatCount="indefinite"/></circle>
<text x="{W/2}" y="17" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{MUTED}" letter-spacing="1">mission-terminal — zsh</text>
<text x="{pad_x+58}" y="{text_y}" font-family="{MONO}" font-size="{FS}" fill="#4ADE80" xml:space="preserve">{prompt}</text>
{''.join(groups)}
</svg>"""
    return svg


# =====================================================================
# 3. DIVIDER — comet crossing a beam
# =====================================================================
def gen_divider():
    W, H = 900, 34
    y = 20
    tw = 4.4  # travel dur
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="">
<defs>
<linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="14" y1="{y}" x2="{W-14}" y2="{y}">
  <stop offset="0" stop-color="{PURPLE}" stop-opacity="0"/>
  <stop offset="0.2" stop-color="{PURPLE}" stop-opacity="0.75"/>
  <stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.9"/>
  <stop offset="0.8" stop-color="{PURPLE}" stop-opacity="0.75"/>
  <stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="cometTail" x1="1" y1="0" x2="0" y2="0">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/>
  <stop offset="0.3" stop-color="{CYAN_BRIGHT}" stop-opacity="0.55"/>
  <stop offset="1" stop-color="{PURPLE_BRIGHT}" stop-opacity="0"/>
</linearGradient>
<filter id="dGlow" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="2.5" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>
<line x1="14" y1="{y}" x2="{W-14}" y2="{y}" stroke="url(#beam)" stroke-width="5" opacity="0.28"/>
<line x1="14" y1="{y}" x2="{W-14}" y2="{y}" stroke="url(#beam)" stroke-width="2.2"/>
<g>
  <circle cx="150" cy="{y}" r="1.6" fill="{CYAN_BRIGHT}"><animate attributeName="opacity" values="0.1;1;0.1" dur="2.6s" repeatCount="indefinite"/></circle>
  <circle cx="450" cy="{y}" r="1.6" fill="{STAR_WHITE}"><animate attributeName="opacity" values="1;0.1;1" dur="3.1s" repeatCount="indefinite"/></circle>
  <circle cx="750" cy="{y}" r="1.6" fill="{PURPLE_BRIGHT}"><animate attributeName="opacity" values="0.1;1;0.1" dur="2.2s" repeatCount="indefinite"/></circle>
</g>
<g opacity="0">
  <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.03;0.8;0.86;1" dur="{tw}s" repeatCount="indefinite"/>
  <animateMotion path="M -60 {y} L {W+60} {y}" keyPoints="0;1;1" keyTimes="0;0.86;1" calcMode="linear" dur="{tw}s" repeatCount="indefinite"/>
  <polygon points="0,0 -74,-2.6 -74,2.6" fill="url(#cometTail)"/>
  <circle r="3" fill="#FFFFFF" filter="url(#dGlow)"/>
</g>
</svg>"""
    return svg


# =====================================================================
# 4. TECH ORBIT — rotating stack rings
# =====================================================================
def gen_orbit():
    W, H = 860, 620
    cx, cy = W / 2, 316
    rings = [
        # (radius, duration, direction 1=cw, items [(label, color, start_angle)])
        (104, 26, 1, [("PHP", "#9FA8DA"), ("Java", "#F89820"), ("JavaScript", "#F7DF1E"), ("Golang", "#00ADD8")]),
        (182, 40, -1, [("Laravel", "#FF2D20"), ("React", "#61DAFB"), ("Node.js", "#4ADE80"), ("Bootstrap", "#B197FC")]),
        (262, 58, 1, [("MySQL", "#5FA8E8"), ("PostgreSQL", "#699ECA"), ("Redis", "#FF6B6B"), ("Git", "#F05032"), ("GitHub", "#E0E7FF")]),
    ]

    ring_svgs = []
    for ri, (r, dur, dirn, items) in enumerate(rings):
        frm, to = (0, 360 * dirn)
        c_frm, c_to = (0, -360 * dirn)
        parts = [
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{CYAN_BRIGHT}" stroke-opacity="0.13" stroke-width="1.1" stroke-dasharray="3 7">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="{100*dirn}" dur="{dur+18}s" repeatCount="indefinite"/></circle>'
        ]
        n = len(items)
        inner = []
        rng = random.Random(100 + ri)
        for ii, (label, color) in enumerate(items):
            a = math.radians(-90 + ii * 360 / n)
            px = cx + r * math.cos(a)
            py = cy + r * math.sin(a)
            wpx = 26 + len(label) * 8.6
            inner.append(f"""<g transform="translate({px:.1f} {py:.1f})">
  <g>
    <animateTransform attributeName="transform" type="rotate" from="{c_frm}" to="{c_to}" dur="{dur}s" repeatCount="indefinite"/>
    <rect x="{-wpx/2:.1f}" y="-15" width="{wpx:.1f}" height="30" rx="15" fill="#0D1117" fill-opacity="0.94" stroke="{color}" stroke-width="1.5"/>
    <circle cx="{-wpx/2+13:.1f}" cy="0" r="3.4" fill="{color}">
      <animate attributeName="opacity" values="1;0.35;1" dur="{round(rng.uniform(1.6,3.2),2)}s" repeatCount="indefinite"/>
    </circle>
    <text x="{-wpx/2+23:.1f}" y="4.6" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{color}">{label}</text>
  </g>
</g>""")
            # debris dot between items
            da = math.radians(-90 + (ii + 0.5) * 360 / n)
            inner.append(
                f'<circle cx="{cx + r*math.cos(da):.1f}" cy="{cy + r*math.sin(da):.1f}" r="2" fill="{CYAN_BRIGHT}" opacity="0.5">'
                f'<animate attributeName="opacity" values="0.15;0.7;0.15" dur="{round(rng.uniform(2,4),2)}s" repeatCount="indefinite"/></circle>'
            )
        parts.append(f"""<g>
  <animateTransform attributeName="transform" type="rotate" from="{frm} {cx} {cy}" to="{to} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/>
  {''.join(inner)}
</g>""")
        ring_svgs.append("".join(parts))

    core = f"""
<g>
  <circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{PURPLE_BRIGHT}" stroke-width="1.4" opacity="0">
    <animate attributeName="r" values="30;58" dur="3.2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0" dur="3.2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="30" fill="none" stroke="{CYAN}" stroke-width="1.4" opacity="0">
    <animate attributeName="r" values="30;58" dur="3.2s" begin="1.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0" dur="3.2s" begin="1.6s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="30" fill="url(#coreG)" filter="url(#bigGlow)">
    <animate attributeName="r" values="30;32;30" dur="3.4s" repeatCount="indefinite"/>
  </circle>
  <path d="M {cx} {cy-13} C {cx+1.6} {cy-4}, {cx+4} {cy-1.6}, {cx+13} {cy} C {cx+4} {cy+1.6}, {cx+1.6} {cy+4}, {cx} {cy+13} C {cx-1.6} {cy+4}, {cx-4} {cy+1.6}, {cx-13} {cy} C {cx-4} {cy-1.6}, {cx-1.6} {cy-4}, {cx} {cy-13} Z" fill="#FFFFFF">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="14s" repeatCount="indefinite"/>
  </path>
  <text x="{cx}" y="{cy+56}" text-anchor="middle" font-family="{MONO}" font-size="11.5" letter-spacing="3" fill="{PURPLE_BRIGHT}" opacity="0.9">CORE SYSTEMS</text>
</g>"""

    legend = f"""
<g font-family="{MONO}" font-size="11">
  <circle cx="34" cy="{H-52}" r="3" fill="{GOLD}"/><text x="44" y="{H-48}" fill="{MUTED}">INNER ORBIT :: LANGUAGES</text>
  <circle cx="34" cy="{H-32}" r="3" fill="{CYAN}"/><text x="44" y="{H-28}" fill="{MUTED}">MID ORBIT :: FRAMEWORKS &amp; RUNTIME</text>
  <circle cx="34" cy="{H-12}" r="3" fill="{PURPLE_BRIGHT}"/><text x="44" y="{H-8}" fill="{MUTED}">OUTER ORBIT :: DATA &amp; TOOLS</text>
</g>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack: PHP, Java, JavaScript, Golang, Laravel, React, Node.js, Bootstrap, MySQL, PostgreSQL, Redis, Git, GitHub">
<defs>{COMMON_DEFS}
<radialGradient id="orbitBg" cx="50%" cy="45%" r="80%">
  <stop offset="0" stop-color="#0D1430"/>
  <stop offset="1" stop-color="{SPACE_BLACK}"/>
</radialGradient>
<radialGradient id="coreG" cx="40%" cy="35%" r="80%">
  <stop offset="0" stop-color="{PURPLE_BRIGHT}"/>
  <stop offset="1" stop-color="{VIOLET}"/>
</radialGradient>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="url(#orbitBg)"/>
{stars(46, 10, 10, W-10, H-10, seed=77, omin=0.1, omax=0.85)}
{"".join(ring_svgs)}
{core}
{legend}
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#26315c" stroke-opacity="0.55"/>
</svg>"""
    return svg


# =====================================================================
# 5. MISSION CONTROL — HUD stats dashboard (template + filled)
# =====================================================================
def gen_mission_control_template():
    W, H = 900, 352
    rx, ry = 152, 178  # radar center
    rr = 86  # radar radius
    C = 2 * math.pi * 27  # gauge circumference

    grid_lines = []
    for gx in range(60, W, 60):
        grid_lines.append(f'<line x1="{gx}" y1="34" x2="{gx}" y2="{H-10}" stroke="{CYAN}" stroke-opacity="0.035" stroke-width="1"/>')
    for gy in range(60, H, 55):
        grid_lines.append(f'<line x1="10" y1="{gy}" x2="{W-10}" y2="{gy}" stroke="{CYAN}" stroke-opacity="0.035" stroke-width="1"/>')

    radar_blips = ""
    rngb = random.Random(5)
    for (bx, by, beg) in [(rx+38, ry-30, 0.6), (rx-44, ry+22, 2.1), (rx+14, ry+52, 3.3)]:
        radar_blips += (
            f'<circle cx="{bx}" cy="{by}" r="3" fill="{CYAN_BRIGHT}" opacity="0">'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;0.15;1" dur="4s" begin="{beg}s" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="2;5" dur="4s" begin="{beg}s" repeatCount="indefinite"/></circle>'
        )

    def gauge(x, label, value_ph, off_ph, color):
        return f"""<g>
  <circle cx="{x}" cy="150" r="27" fill="none" stroke="{color}" stroke-opacity="0.16" stroke-width="5"/>
  <circle cx="{x}" cy="150" r="27" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"
    stroke-dasharray="{C:.2f}" stroke-dashoffset="{C:.2f}" transform="rotate(-90 {x} 150)">
    <animate attributeName="stroke-dashoffset" from="{C:.2f}" to="{off_ph}" begin="0.5s" dur="1.6s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.25 1"/>
  </circle>
  <text x="{x}" y="158" text-anchor="middle" font-family="{SANS}" font-size="24" font-weight="800" fill="{STAR_WHITE}">{value_ph}</text>
  <text x="{x}" y="205" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1.6" fill="{MUTED}">{label}</text>
  <circle cx="{x}" cy="112" r="2.4" fill="{color}">
    <animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
</g>"""

    gauges = (
        gauge(392, "REPOSITORIES", "{REPOS}", "{REPOS_OFF}", CYAN)
        + gauge(542, "FOLLOWERS", "{FOLLOWERS}", "{FOLLOWERS_OFF}", PURPLE_BRIGHT)
        + gauge(692, "STARS EARNED", "{STARS}", "{STARS_OFF}", GOLD)
        + gauge(832, "YEARS IN ORBIT", "{YEARS}", "{YEARS_OFF}", PINK)
    )

    ticker_txt = "MISSION: BUILD SCALABLE GALAXIES OF CODE  ///  NAV: BACKEND ARCHITECTURE + DISTRIBUTED SYSTEMS  ///  FUEL: COFFEE RESERVES AT 87%  ///  STATUS: ALL SYSTEMS NOMINAL  ///  "
    tick_w = len(ticker_txt) * 12 * CW  # font 12 mono
    corners = []
    for (cxx, cyy, sx, sy) in [(12, 12, 1, 1), (W-12, 12, -1, 1), (12, H-12, 1, -1), (W-12, H-12, -1, -1)]:
        corners.append(f'<path d="M {cxx} {cyy+sy*16} L {cxx} {cyy} L {cxx+sx*16} {cyy}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-opacity="0.8"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub statistics dashboard">
<defs>{COMMON_DEFS}
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{CYAN}" stop-opacity="0.06"/>
  <stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN_BRIGHT}" stop-opacity="0.5"/>
  <stop offset="1" stop-color="{CYAN_BRIGHT}" stop-opacity="0"/>
</linearGradient>
<clipPath id="mcClip"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>
<clipPath id="tickClip"><rect x="20" y="{H-40}" width="{W-40}" height="30"/></clipPath>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="{PANEL}"/>
<g clip-path="url(#mcClip)">
{''.join(grid_lines)}
<rect x="0" y="-90" width="{W}" height="80" fill="url(#scan)">
  <animateTransform attributeName="transform" type="translate" from="0 0" to="0 {H+180}" dur="7s" repeatCount="indefinite"/>
</rect>
</g>
{''.join(corners)}
<text x="30" y="34" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{CYAN_BRIGHT}">&#9650; MISSION CONTROL — LIVE TELEMETRY</text>
<g font-family="{MONO}" font-size="10.5">
  <circle cx="{W-348}" cy="29" r="3.4" fill="#4ADE80"><animate attributeName="opacity" values="1;0.25;1" dur="1.4s" repeatCount="indefinite"/></circle>
  <text x="{W-338}" y="33" fill="#4ADE80" letter-spacing="1">LINK ESTABLISHED</text>
  <text x="{W-30}" y="33" text-anchor="end" fill="{MUTED}">SYNC {{SYNC_DATE}}</text>
</g>
<line x1="20" y1="46" x2="{W-20}" y2="46" stroke="{CYAN}" stroke-opacity="0.25" stroke-width="1"/>

<!-- radar -->
<g>
  <circle cx="{rx}" cy="{ry}" r="{rr}" fill="#0D1430" stroke="{CYAN}" stroke-opacity="0.35"/>
  <circle cx="{rx}" cy="{ry}" r="{int(rr*0.66)}" fill="none" stroke="{CYAN}" stroke-opacity="0.18"/>
  <circle cx="{rx}" cy="{ry}" r="{int(rr*0.36)}" fill="none" stroke="{CYAN}" stroke-opacity="0.18"/>
  <line x1="{rx-rr}" y1="{ry}" x2="{rx+rr}" y2="{ry}" stroke="{CYAN}" stroke-opacity="0.14"/>
  <line x1="{rx}" y1="{ry-rr}" x2="{rx}" y2="{ry+rr}" stroke="{CYAN}" stroke-opacity="0.14"/>
  <g>
    <animateTransform attributeName="transform" type="rotate" from="0 {rx} {ry}" to="360 {rx} {ry}" dur="4.4s" repeatCount="indefinite"/>
    <path d="M {rx} {ry} L {rx+rr} {ry} A {rr} {rr} 0 0 0 {rx + rr*math.cos(math.radians(-38)):.1f} {ry + rr*math.sin(math.radians(-38)):.1f} Z" fill="url(#sweep)"/>
    <line x1="{rx}" y1="{ry}" x2="{rx+rr}" y2="{ry}" stroke="{CYAN_BRIGHT}" stroke-width="1.6" stroke-opacity="0.9"/>
  </g>
  {radar_blips}
  <text x="{rx}" y="286" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{MUTED}">SCANNING SECTOR: PRODUCTION</text>
  <text x="{rx}" y="301" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="#4ADE80">0 CRITICAL BUGS DETECTED
    <animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/>
  </text>
</g>

<line x1="292" y1="70" x2="292" y2="{H-56}" stroke="{CYAN}" stroke-opacity="0.15"/>
<text x="392" y="86" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{MUTED}">ONBOARD TELEMETRY</text>
<g font-family="{MONO}" font-size="10">
  <circle cx="700" cy="82" r="3" fill="#4ADE80"><animate attributeName="opacity" values="1;0.2;1" dur="1.1s" repeatCount="indefinite"/></circle><text x="708" y="85.5" fill="{MUTED}">PWR</text>
  <circle cx="748" cy="82" r="3" fill="{GOLD}"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.7s" repeatCount="indefinite"/></circle><text x="756" y="85.5" fill="{MUTED}">NET</text>
  <circle cx="796" cy="82" r="3" fill="{CYAN_BRIGHT}"><animate attributeName="opacity" values="1;0.2;1" dur="2.3s" repeatCount="indefinite"/></circle><text x="804" y="85.5" fill="{MUTED}">DB</text>
</g>
{gauges}

<line x1="20" y1="{H-46}" x2="{W-20}" y2="{H-46}" stroke="{CYAN}" stroke-opacity="0.25"/>
<g clip-path="url(#tickClip)">
  <g>
    <animateTransform attributeName="transform" type="translate" from="0 0" to="-{tick_w:.0f} 0" dur="26s" repeatCount="indefinite"/>
    <text x="24" y="{H-20}" font-family="{MONO}" font-size="12" fill="{CYAN_BRIGHT}" opacity="0.75" xml:space="preserve">{ticker_txt}{ticker_txt}</text>
  </g>
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#26315c" stroke-opacity="0.55"/>
</svg>"""
    return svg


# =====================================================================
# 6. ASTRONAUT — floating, waving
# =====================================================================
def gen_astronaut():
    W, H = 240, 300
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Floating astronaut waving hello">
<defs>
<radialGradient id="visorG" cx="35%" cy="30%" r="90%">
  <stop offset="0" stop-color="#38BDF8"/>
  <stop offset="0.5" stop-color="#0E7490"/>
  <stop offset="1" stop-color="#0B1030"/>
</radialGradient>
<linearGradient id="suitG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#F8FAFC"/><stop offset="1" stop-color="#CBD5E1"/>
</linearGradient>
</defs>
<g stroke-linecap="round">
  <path d="M 214 8 C 200 70, 186 96, 166 122" fill="none" stroke="{CYAN_BRIGHT}" stroke-width="2" stroke-dasharray="5 6" opacity="0.75">
    <animate attributeName="stroke-dashoffset" from="0" to="-44" dur="3.2s" repeatCount="indefinite"/>
  </path>
  <circle cx="30" cy="52" r="1.8" fill="{STAR_WHITE}"><animate attributeName="opacity" values="0.15;1;0.15" dur="2.8s" repeatCount="indefinite"/></circle>
  <circle cx="204" cy="196" r="1.8" fill="{CYAN_BRIGHT}"><animate attributeName="opacity" values="1;0.15;1" dur="3.4s" repeatCount="indefinite"/></circle>
  <circle cx="26" cy="236" r="1.8" fill="{PURPLE_BRIGHT}"><animate attributeName="opacity" values="0.15;1;0.15" dur="2.2s" repeatCount="indefinite"/></circle>
  <circle cx="120" cy="18" r="1.5" fill="{STAR_WHITE}"><animate attributeName="opacity" values="1;0.2;1" dur="4s" repeatCount="indefinite"/></circle>
  <circle cx="60" cy="130" r="1.5" fill="{STAR_WHITE}"><animate attributeName="opacity" values="0.2;1;0.2" dur="3.1s" repeatCount="indefinite"/></circle>

  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0; 0 -12; 0 0" dur="5.2s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
    <g transform="rotate(-4 120 170)">
      <animateTransform attributeName="transform" type="rotate" values="-4 120 170; 4 120 170; -4 120 170" dur="7s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>

      <!-- speech bubble -->
      <g opacity="0">
        <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.55;0.6;0.85;0.9;1" calcMode="discrete" dur="7.5s" repeatCount="indefinite"/>
        <rect x="24" y="52" width="92" height="30" rx="15" fill="#0D1117" stroke="{CYAN}" stroke-opacity="0.7"/>
        <path d="M 88 82 l 8 12 l 2 -12 z" fill="#0D1117" stroke="{CYAN}" stroke-opacity="0.7"/>
        <text x="70" y="72" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{CYAN_BRIGHT}">hello() &#128075;</text>
      </g>

      <!-- backpack -->
      <rect x="76" y="128" width="88" height="74" rx="16" fill="#94A3B8" stroke="#475569" stroke-width="2.5"/>
      <!-- waving arm (behind body, raised) -->
      <g>
        <animateTransform attributeName="transform" type="rotate" values="-14 158 150; 16 158 150; -14 158 150" dur="1.9s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/>
        <path d="M 156 150 C 176 138, 188 122, 192 100" fill="none" stroke="url(#suitG)" stroke-width="17"/>
        <path d="M 156 150 C 176 138, 188 122, 192 100" fill="none" stroke="#475569" stroke-width="17" opacity="0"/>
        <path d="M 156 150 C 176 138, 188 122, 192 100" fill="none" stroke="#64748B" stroke-width="19" stroke-opacity="0.35"/>
        <circle cx="193" cy="96" r="11" fill="url(#suitG)" stroke="#475569" stroke-width="2.5"/>
      </g>
      <!-- left arm -->
      <path d="M 92 152 C 74 162, 64 176, 62 194" fill="none" stroke="#64748B" stroke-opacity="0.35" stroke-width="19"/>
      <path d="M 92 152 C 74 162, 64 176, 62 194" fill="none" stroke="url(#suitG)" stroke-width="17"/>
      <circle cx="61" cy="198" r="11" fill="url(#suitG)" stroke="#475569" stroke-width="2.5"/>
      <!-- legs -->
      <path d="M 104 214 C 100 234, 98 246, 96 258" fill="none" stroke="url(#suitG)" stroke-width="19"/>
      <path d="M 136 214 C 140 234, 142 246, 146 258" fill="none" stroke="url(#suitG)" stroke-width="19"/>
      <rect x="84" y="252" width="26" height="16" rx="8" fill="#94A3B8" stroke="#475569" stroke-width="2.5"/>
      <rect x="132" y="252" width="26" height="16" rx="8" fill="#94A3B8" stroke="#475569" stroke-width="2.5"/>
      <!-- torso -->
      <rect x="88" y="128" width="64" height="94" rx="26" fill="url(#suitG)" stroke="#475569" stroke-width="2.8"/>
      <rect x="102" y="158" width="36" height="26" rx="6" fill="#0D1430" stroke="#475569" stroke-width="2"/>
      <circle cx="111" cy="166" r="3" fill="#F87171"><animate attributeName="opacity" values="1;0.2;1" dur="1.3s" repeatCount="indefinite"/></circle>
      <circle cx="121" cy="166" r="3" fill="#4ADE80"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.7s" repeatCount="indefinite"/></circle>
      <rect x="105" y="174" width="30" height="4" rx="2" fill="{CYAN}" opacity="0.8">
        <animate attributeName="width" values="10;30;10" dur="3.4s" repeatCount="indefinite"/>
      </rect>
      <!-- helmet -->
      <circle cx="120" cy="96" r="37" fill="url(#suitG)" stroke="#475569" stroke-width="2.8"/>
      <circle cx="120" cy="98" r="27" fill="url(#visorG)" stroke="#334155" stroke-width="2.4"/>
      <ellipse cx="110" cy="88" rx="8" ry="5" fill="#E0F2FE" opacity="0.65" transform="rotate(-24 110 88)"/>
      <clipPath id="visorClip"><circle cx="120" cy="98" r="27"/></clipPath>
      <g clip-path="url(#visorClip)">
        <rect x="86" y="70" width="10" height="70" fill="#E0F2FE" opacity="0.3" transform="skewX(-20)">
          <animateTransform attributeName="transform" type="translate" from="-40 0" to="110 0" dur="4.2s" repeatCount="indefinite" additive="sum"/>
        </rect>
      </g>
      <!-- antenna -->
      <line x1="120" y1="59" x2="120" y2="46" stroke="#475569" stroke-width="2.5"/>
      <circle cx="120" cy="43" r="4" fill="{PINK}"><animate attributeName="opacity" values="1;0.25;1" dur="1.1s" repeatCount="indefinite"/></circle>
    </g>
  </g>
</g>
</svg>"""
    return svg


# =====================================================================
# 7. FOOTER — rocket launch from a purple planet
# =====================================================================
def gen_footer():
    W, H = 900, 300
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="See you in orbit — rocket launching">
<defs>{COMMON_DEFS}
<radialGradient id="ftBg" cx="50%" cy="0%" r="110%">
  <stop offset="0" stop-color="#0E1533"/>
  <stop offset="1" stop-color="{SPACE_BLACK}"/>
</radialGradient>
<linearGradient id="planetG2" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#4C1D95"/>
  <stop offset="0.45" stop-color="#37136E"/>
  <stop offset="1" stop-color="#160A38"/>
</linearGradient>
<linearGradient id="byeGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CYAN_BRIGHT}"/>
  <stop offset="0.5" stop-color="{STAR_WHITE}"/>
  <stop offset="1" stop-color="{PURPLE_BRIGHT}"/>
</linearGradient>
<linearGradient id="flameG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFFFFF"/>
  <stop offset="0.35" stop-color="{GOLD}"/>
  <stop offset="1" stop-color="#F97316" stop-opacity="0.1"/>
</linearGradient>
<clipPath id="ftClip"><rect x="0" y="0" width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" rx="16" fill="url(#ftBg)"/>
<g clip-path="url(#ftClip)">
{stars(44, 8, 8, W-8, 200, seed=1234)}
{shooting_star((-70, 40), (960, 170), total=13, start=0.55, tail=80)}

<!-- satellite -->
<g>
  <animateMotion path="M 830 60 C 700 40, 500 60, 330 44" dur="34s" repeatCount="indefinite" keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear"/>
  <g transform="rotate(-14)">
    <rect x="-22" y="-3" width="14" height="8" rx="1.5" fill="{CYAN}" opacity="0.85"/>
    <rect x="8" y="-3" width="14" height="8" rx="1.5" fill="{CYAN}" opacity="0.85"/>
    <line x1="-8" y1="1" x2="8" y2="1" stroke="#94A3B8" stroke-width="2"/>
    <rect x="-5" y="-5" width="10" height="12" rx="2" fill="#CBD5E1"/>
    <circle cx="0" cy="-9" r="2" fill="{PINK}"><animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
  </g>
</g>

<!-- planet -->
<ellipse cx="450" cy="478" rx="580" ry="238" fill="url(#planetG2)"/>
<ellipse cx="450" cy="478" rx="580" ry="238" fill="none" stroke="{CYAN_BRIGHT}" stroke-opacity="0.35" stroke-width="1.4" filter="url(#softGlow)"/>
<ellipse cx="260" cy="292" rx="26" ry="9" fill="#120728" opacity="0.55"/>
<ellipse cx="640" cy="300" rx="34" ry="11" fill="#120728" opacity="0.5"/>
<ellipse cx="480" cy="330" rx="20" ry="7" fill="#120728" opacity="0.55"/>
<ellipse cx="150" cy="330" rx="30" ry="10" fill="#120728" opacity="0.45"/>

<!-- rocket : idle shake then launch, 9s loop -->
<g>
  <animateTransform attributeName="transform" type="translate"
    values="0 0; 0 0; 0 -34; 0 -420; 0 -420; 0 0"
    keyTimes="0;0.30;0.42;0.62;0.99;1"
    calcMode="spline" keySplines="0.4 0 0.6 1;0.55 0 0.9 0.4;0.3 0.6 0.4 1;0 0 1 1;0 0 1 1"
    dur="9s" repeatCount="indefinite"/>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0.9 0;-0.9 0;0.6 0;0 0" dur="0.16s" repeatCount="indefinite"/>
    <g transform="translate(450 252)">
      <!-- exhaust flame -->
      <g>
        <animateTransform attributeName="transform" type="scale" values="1 1;1 1.45;1 0.85;1 1.3;1 1" dur="0.34s" repeatCount="indefinite"/>
        <path d="M -7 0 C -5 16, -2 24, 0 34 C 2 24, 5 16, 7 0 Z" fill="url(#flameG)"/>
        <path d="M -3.4 0 C -2.4 9, -1 14, 0 19 C 1 14, 2.4 9, 3.4 0 Z" fill="#FFFFFF" opacity="0.9"/>
      </g>
      <!-- body -->
      <path d="M 0 -58 C 10 -44, 13 -30, 13 -12 L 13 0 L -13 0 L -13 -12 C -13 -30, -10 -44, 0 -58 Z" fill="#F1F5F9" stroke="#64748B" stroke-width="2"/>
      <path d="M 0 -58 C 4 -52, 7 -46, 9 -38 L -9 -38 C -7 -46, -4 -52, 0 -58 Z" fill="{PINK}" stroke="#64748B" stroke-width="1.6"/>
      <circle cx="0" cy="-24" r="6.5" fill="url(#visorG2)" stroke="#64748B" stroke-width="2"/>
      <circle cx="0" cy="-24" r="2.4" fill="{CYAN_BRIGHT}"><animate attributeName="opacity" values="1;0.3;1" dur="1.2s" repeatCount="indefinite"/></circle>
      <path d="M -13 -14 C -20 -8, -22 -2, -22 4 L -13 0 Z" fill="{PINK}" stroke="#64748B" stroke-width="1.6"/>
      <path d="M 13 -14 C 20 -8, 22 -2, 22 4 L 13 0 Z" fill="{PINK}" stroke="#64748B" stroke-width="1.6"/>
    </g>
  </g>
</g>
<radialGradient id="visorG2" cx="35%" cy="30%" r="90%">
  <stop offset="0" stop-color="#67E8F9"/><stop offset="1" stop-color="#0B1030"/>
</radialGradient>

<!-- launch smoke -->
<g opacity="0">
  <animate attributeName="opacity" values="0;0;0.8;0.35;0;0" keyTimes="0;0.30;0.40;0.55;0.72;1" dur="9s" repeatCount="indefinite"/>
  <circle cx="432" cy="252" r="10" fill="#CBD5E1" opacity="0.5"><animate attributeName="r" values="6;16" keyTimes="0;1" dur="9s" repeatCount="indefinite"/></circle>
  <circle cx="468" cy="252" r="12" fill="#94A3B8" opacity="0.45"><animate attributeName="r" values="7;20" keyTimes="0;1" dur="9s" repeatCount="indefinite"/></circle>
  <circle cx="450" cy="258" r="14" fill="#E2E8F0" opacity="0.4"><animate attributeName="r" values="8;24" keyTimes="0;1" dur="9s" repeatCount="indefinite"/></circle>
</g>

<text x="450" y="96" text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" letter-spacing="6" fill="url(#byeGrad)" filter="url(#softGlow)">SEE YOU IN ORBIT</text>
<text x="450" y="128" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{MUTED}">thanks for stopping by my corner of the cosmos
  <animate attributeName="opacity" values="0.6;1;0.6" dur="3.8s" repeatCount="indefinite"/>
</text>
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#26315c" stroke-opacity="0.55"/>
</svg>"""
    return svg


# =====================================================================
# fill mission-control template with live values
# =====================================================================
def fill_dashboard(template, repos, followers, stars_n, years, sync_date):
    C = 2 * math.pi * 27

    def off(frac):
        frac = max(0.06, min(1.0, frac))
        return f"{C * (1 - frac):.2f}"

    return (template
            .replace("{REPOS_OFF}", off(repos / 20))
            .replace("{FOLLOWERS_OFF}", off(followers / 20))
            .replace("{STARS_OFF}", off(stars_n / 10))
            .replace("{YEARS_OFF}", off(years / 8))
            .replace("{REPOS}", str(repos))
            .replace("{FOLLOWERS}", str(followers))
            .replace("{STARS}", str(stars_n))
            .replace("{YEARS}", str(years))
            .replace("{SYNC_DATE}", sync_date))


def validate(name, content):
    try:
        xml.dom.minidom.parseString(content)
        print(f"  OK   {name}  ({len(content)//1024}KB)")
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        raise SystemExit(1)


assets = {
    "hero.svg": gen_hero(),
    "typing.svg": gen_typing(),
    "divider.svg": gen_divider(),
    "tech-orbit.svg": gen_orbit(),
    "astronaut.svg": gen_astronaut(),
    "footer.svg": gen_footer(),
}
tmpl = gen_mission_control_template()
assets["mission-control.template.svg"] = tmpl
assets["mission-control.svg"] = fill_dashboard(tmpl, 11, 5, 2, 4, "2026-08-13")

for name, content in assets.items():
    validate(name, content)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)
print("done ->", OUT)
