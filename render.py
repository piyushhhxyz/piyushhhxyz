"""Render the neofetch-style profile card to dark_mode.svg / light_mode.svg.

The card is a fixed monospace grid: a 44-column ASCII portrait on the left and a
60-column info panel on the right. Every panel row is padded to exactly
PANEL_COLS with a run of dot leaders, which is what keeps the values aligned in
a single column the way neofetch does.
"""
import json
import pathlib
from xml.sax.saxutils import escape

MIN_PANEL_COLS = 60  # the panel grows past this only if a value needs it
ART_COLS = 44        # character cells reserved for the portrait
LINE_H = 20          # px between baselines
TOP = 30             # px baseline of the first row
ART_X = 15
GUTTER = 12          # px between the portrait and the panel
MARGIN = 15          # px of card padding on the right
# Consolas advances 0.55em; the size-adjust in the stylesheet stretches it to
# match the 0.602em monospace fallbacks (Menlo, DejaVu Sans Mono) so that one
# character is this many pixels wide no matter which font actually loads.
CHAR_W = 16 * 0.602

FILL = object()      # placeholder segment: absorbs the leftover dot leaders


def seg(text, cls=None):
    return (text, cls)


PANEL_COLS = MIN_PANEL_COLS      # rebound per-render by render()


def rule(label):
    """`- Contact -————————-—-` style divider, padded to PANEL_COLS."""
    dashes = PANEL_COLS - len(label) - 5
    return f"{label} -" + "—" * max(dashes, 0) + "-—-"


def kv(key_parts, value):
    """One `. Key: ..... value` row. key_parts renders '.'-joined in key colour."""
    key_len = sum(len(p) for p in key_parts) + (len(key_parts) - 1)
    segs = [seg(". ", "cc")]
    for i, p in enumerate(key_parts):
        if i:
            segs.append(seg("."))
        segs.append(seg(p, "key"))
    segs += [seg(":"), FILL, seg(escape(value), "value")]
    # ". " + key + ":" + " …dots… " + value  == PANEL_COLS
    dots = PANEL_COLS - 2 - key_len - 1 - len(value) - 2
    return segs, {FILL: " " + "." * max(dots, 1) + " "}


def line_to_svg(segs, fills, x, y):
    """Emit one <tspan …> row; the first segment carries the x/y anchor."""
    out = []
    first = True
    for s in segs:
        if s is FILL:
            out.append(f'<tspan class="cc">{fills[FILL]}</tspan>')
            continue
        text, cls = s
        attrs = ""
        if first:
            attrs = f' x="{x}" y="{y}"'
            first = False
        if cls:
            attrs += f' class="{cls}"'
        out.append(f"<tspan{attrs}>{text}</tspan>")
    return "".join(out)


def plain(text, x, y, cls=None):
    c = f' class="{cls}"' if cls else ""
    return f'<tspan x="{x}" y="{y}"{c}>{escape(text)}</tspan>'


def build_panel(cfg, s):
    """Return a list of rows; each row is (segments, fills) or a raw string."""
    rows = []
    rows.append(("raw", [seg(cfg["header"], "key"),
                         seg(rule("")[len(""):].replace(" -", " -", 1))]))
    # header: name in key colour followed by the divider tail
    rows[-1] = ("raw", [seg(cfg["header"], "key"),
                        seg(" -" + "—" * (PANEL_COLS - len(cfg["header"]) - 5)
                            + "-—-")])

    for row in cfg["about"]:
        if not row:
            rows.append(("raw", [seg(". ", "cc")]))
            continue
        key, val = row
        rows.append(("kv", (key.split("."), val.format(**s))))

    rows.append(("raw", [seg(". ", "cc")]))
    rows.append(("raw", [seg(rule("- Contact"))]))
    for key, val in cfg["contact"]:
        rows.append(("kv", (key.split("."), val)))

    rows.append(("raw", [seg(". ", "cc")]))
    rows.append(("raw", [seg(rule("- GitHub Stats"))]))
    rows.extend(stat_rows(s))
    return rows


def pad_pair(fixed_len, slots):
    """Split the leftover columns across `slots` dot runs, left run widest."""
    total = PANEL_COLS - fixed_len
    base = max(total // slots, 1)
    return [total - base * (slots - 1)] + [base] * (slots - 1)


def stat_rows(s):
    repos, contrib = f"{s['repos']:,}", f"{s['contributed']:,}"
    stars, commits = f"{s['stars']:,}", f"{s['commits']:,}"
    followers = f"{s['followers']:,}"
    net, add, dele = f"{s['loc_net']:,}", f"{s['loc_add']:,}", f"{s['loc_del']:,}"

    rows = []

    # . Repos: .. N {Contributed: N} | Stars: .. N
    fixed = len(". ") + len("Repos:") + len(repos) + len(" {Contributed: ") \
        + len(contrib) + len("} | ") + len("Stars:") + len(stars) + 4
    d1, d2 = pad_pair(fixed, 2)
    rows.append(("raw", [
        seg(". ", "cc"), seg("Repos", "key"), seg(":"),
        seg(" " + "." * d1 + " ", "cc"), seg(repos, "value"),
        seg(" {"), seg("Contributed", "key"), seg(": "), seg(contrib, "value"),
        seg("} | "), seg("Stars", "key"), seg(":"),
        seg(" " + "." * d2 + " ", "cc"), seg(stars, "value")]))

    # . Commits: .. N | Followers: .. N
    fixed = len(". ") + len("Commits:") + len(commits) + len(" | ") \
        + len("Followers:") + len(followers) + 4
    d1, d2 = pad_pair(fixed, 2)
    rows.append(("raw", [
        seg(". ", "cc"), seg("Commits", "key"), seg(":"),
        seg(" " + "." * d1 + " ", "cc"), seg(commits, "value"),
        seg(" | "), seg("Followers", "key"), seg(":"),
        seg(" " + "." * d2 + " ", "cc"), seg(followers, "value")]))

    # . Lines of Code on GitHub: . N ( N++, N-- )
    label = "Lines of Code on GitHub"
    fixed = len(". ") + len(label) + 1 + len(net) + len(" ( ") + len(add) \
        + len("++, ") + len(dele) + len("-- )") + 2
    d1 = max(PANEL_COLS - fixed, 1)
    rows.append(("raw", [
        seg(". ", "cc"), seg(label, "key"), seg(":"),
        seg(" " + "." * d1 + " ", "cc"), seg(net, "value"),
        seg(" ( "), seg(add, "add"), seg("++", "add"), seg(", "),
        seg(dele, "del"), seg("--", "del"), seg(" )")]))
    return rows


def center_art(lines, cols=ART_COLS):
    """Centre the portrait in its column so the card is not lopsided."""
    body = [l.rstrip() for l in lines]
    left = min((len(l) - len(l.lstrip()) for l in body if l.strip()), default=0)
    right = max((len(l) for l in body), default=0)
    pad = max((cols - (right - left)) // 2, 0)
    return [" " * pad + l[left:] if l.strip() else "" for l in body]


def panel_width(cfg, stats):
    """Widest row the panel must hold, so nothing gets clipped off the card."""
    widest = len(cfg["header"]) + 5
    for row in cfg["about"]:
        if row:
            widest = max(widest, 6 + len(row[0]) + len(row[1].format(**stats)))
    for key, val in cfg["contact"]:
        widest = max(widest, 6 + len(key) + len(val))
    fixed = (len(". Lines of Code on GitHub:") + 3
             + len(f"{stats['loc_net']:,}") + len(" ( ")
             + len(f"{stats['loc_add']:,}") + len("++, ")
             + len(f"{stats['loc_del']:,}") + len("-- )"))
    return max(MIN_PANEL_COLS, widest, fixed)


def render(cfg, stats, art_lines, theme_name):
    global PANEL_COLS
    PANEL_COLS = panel_width(cfg, stats)
    panel_x = int(ART_X + ART_COLS * CHAR_W + GUTTER)
    width = int(panel_x + PANEL_COLS * CHAR_W + MARGIN)

    t = cfg["themes"][theme_name]
    rows = build_panel(cfg, stats)
    height = TOP + max(len(art_lines), len(rows)) * LINE_H

    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'font-family="ConsolasFallback,Consolas,Menlo,monospace" '
        f'width="{width}px" height="{height}px" font-size="16px">',
        "<style>",
        "@font-face {src: local('Consolas'), local('Consolas Bold');",
        "font-family: 'ConsolasFallback'; font-display: swap;",
        "-webkit-size-adjust: 109%; size-adjust: 109%;}",
        f".key {{fill: {t['key']};}}",
        f".value {{fill: {t['value']};}}",
        f".add {{fill: {t['add']};}}",
        f".del {{fill: {t['del']};}}",
        f".cc {{fill: {t['cc']};}}",
        "text, tspan {white-space: pre;}",
        "</style>",
        f'<rect width="{width}px" height="{height}px" fill="{t["bg"]}" rx="15"/>',
        f'<text x="{ART_X}" y="{TOP}" fill="{t["fg"]}" xml:space="preserve">',
    ]
    for i, line in enumerate(art_lines):
        out.append(plain(line.ljust(ART_COLS), ART_X, TOP + i * LINE_H))
    out.append("</text>")

    out.append(f'<text x="{panel_x}" y="{TOP}" fill="{t["fg"]}" xml:space="preserve">')
    for i, (kind, body) in enumerate(rows):
        y = TOP + i * LINE_H
        if kind == "kv":
            segs, fills = kv(*body)
            out.append(line_to_svg(segs, fills, panel_x, y))
        else:
            out.append(line_to_svg(body, {}, panel_x, y))
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out)


def main():
    cfg = json.loads(pathlib.Path("config.json").read_text())
    stats = json.loads(pathlib.Path("cache/stats.json").read_text())
    art = pathlib.Path("assets/ascii_art.txt").read_text().rstrip("\n").split("\n")
    art = [escape(l) for l in center_art(art)]
    for theme, path in (("dark", "dark_mode.svg"), ("light", "light_mode.svg")):
        pathlib.Path(path).write_text(render(cfg, stats, art, theme))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
