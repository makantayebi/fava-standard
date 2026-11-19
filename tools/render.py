#!/usr/bin/env python3
"""Render a versions/<x>/layout.yaml into its platform/visual artifacts.

    python3 tools/render.py v0.0.2
        writes versions/v0.0.2/generated/avayi.xkb_symbols
           and versions/v0.0.2/generated/layout.svg

    python3 tools/render.py v0.0.2 --compare v0.0.1
        also writes versions/v0.0.2/generated/vs-v0.0.1.svg,
        both versions stacked in one diagram for an at-a-glance diff.

layout.yaml is the only input; nothing here is hand-edited.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
VERSIONS_DIR = ROOT / "versions"

# --- physical keyboard grid, label shown in the diagram's corner + the layout.yaml key name ---
ROWS = [
    [("`", "TLDE")] + [(d, f"AE{i+1:02d}") for i, d in enumerate(
        ["1","2","3","4","5","6","7","8","9","0","-","="])],
    [(d, f"AD{i+1:02d}") for i, d in enumerate(
        ["Q","W","E","R","T","Y","U","I","O","P","[","]"])] + [("\\", "BKSL")],
    [(d, f"AC{i+1:02d}") for i, d in enumerate(
        ["A","S","D","F","G","H","J","K","L",";","'"])],
    [(d, f"AB{i+1:02d}") for i, d in enumerate(
        ["Z","X","C","V","B","N","M",",",".","/"])],
]
ROW_OFFSETS = [0, 0.5, 0.75, 1.25]  # standard ANSI stagger, in key-widths
KEY_W, KEY_H, GAP = 56, 56, 6
PAD = 40

ARABIC_FONTS = "'Noto Sans Arabic','Noto Naskh Arabic','DejaVu Sans',Tahoma,Arial,sans-serif"
LATIN_FONTS = "'DejaVu Sans',Tahoma,Arial,sans-serif"
PLACEHOLDER = {"‌": "نیم‌فآسِلِ", "‍": "ZWJ", " ": "_"}

# codepoint -> preferred XKB keysym name, for the handful this project actually uses.
# anything not listed here falls back to the portable "U<hex>" keysym syntax.
CODEPOINT_KEYSYM = {
    0x00F7: "division", 0x00D7: "multiply", 0x00B0: "degree", 0x20AC: "EuroSign",
    0x00A7: "section", 0x003A: "colon", 0x007C: "bar", 0x005C: "backslash",
    0x002E: "period", 0x002F: "slash", 0x002D: "minus", 0x005F: "underscore",
    0x003D: "equal", 0x002B: "plus", 0x0021: "exclam", 0x0040: "at",
    0x0023: "numbersign", 0x0025: "percent", 0x005E: "asciicircum",
    0x002A: "asterisk", 0x0028: "parenleft", 0x0029: "parenright",
    0x007B: "braceleft", 0x007D: "braceright", 0x005B: "bracketleft",
    0x005D: "bracketright", 0x0020: "space",
    0x06F0: "Farsi_0", 0x06F1: "Farsi_1", 0x06F2: "Farsi_2", 0x06F3: "Farsi_3",
    0x06F4: "Farsi_4", 0x06F5: "Farsi_5", 0x06F6: "Farsi_6", 0x06F7: "Farsi_7",
    0x06F8: "Farsi_8", 0x06F9: "Farsi_9",
    0x064E: "Arabic_fatha", 0x064F: "Arabic_damma", 0x0650: "Arabic_kasra",
    0x0652: "Arabic_sukun", 0x0651: "Arabic_shadda", 0x0642: "Arabic_qaf",
    0x0641: "Arabic_feh", 0x060C: "Arabic_comma", 0x06CC: "Farsi_yeh",
    0x062C: "Arabic_jeem", 0x0647: "Arabic_heh", 0x062E: "Arabic_khah",
    0x0686: "Arabic_tcheh", 0x0634: "Arabic_sheen", 0x0633: "Arabic_seen",
    0x0628: "Arabic_beh", 0x0644: "Arabic_lam", 0x0622: "Arabic_maddaonalef",
    0x062A: "Arabic_teh", 0x0640: "Arabic_tatweel", 0x0646: "Arabic_noon",
    0x0645: "Arabic_meem", 0x06A9: "Arabic_keheh", 0x06AF: "Arabic_gaf",
    0x061B: "Arabic_semicolon", 0x0698: "Arabic_jeh", 0x0632: "Arabic_zain",
    0x0631: "Arabic_ra", 0x062F: "Arabic_dal", 0x067E: "Arabic_peh",
    0x0648: "Arabic_waw", 0x061F: "Arabic_question_mark",
}

# (key, "base"|"shift") -> a Private Use Area codepoint used purely as a
# Compose trigger (never meant to be seen on its own) for keys whose value
# is more than one codepoint. See schema/layout.schema.md, "Multi-character
# keys". Pick any unused PUA codepoint (U+E000-U+F8FF) when adding more;
# just don't reuse one already listed here.
COMPOSE_TRIGGER = {
    ("AD01", "shift"): 0xF103,  # Q shift -> اُ
    ("AD02", "shift"): 0xF102,  # W shift -> اِ
    ("AD03", "shift"): 0xF101,  # E shift -> اَ
    ("AB05", "base"): 0xF104,   # B base  -> وْ (v0.0.5)
    ("AB05", "shift"): 0xF104,  # shift omitted = same as base; same trigger, not a separate rule
}


def load_layout(version):
    path = VERSIONS_DIR / version / "layout.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cp_list(value):
    """A key's base/shift value is either one 'U+XXXX' string or a list of them."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [int(v[2:], 16) for v in value]


def chars_for(cps):
    return "".join(chr(c) for c in cps)


def keysym_for(cp):
    if cp in CODEPOINT_KEYSYM:
        return CODEPOINT_KEYSYM[cp]
    return f"U{cp:04X}"


# --- xkb_symbols generation ---
def render_xkb(layout):
    lines = [
        f'// Generated from fava-standard versions/{layout["version"]}/layout.yaml',
        "// Do not hand-edit — change layout.yaml and re-run tools/render.py instead.",
        "partial alphanumeric_keys",
        'xkb_symbols "avayi" {',
        f'    name[Group1]= "{layout["name"]}";',
        "",
        '    key.type[Group1]="ALPHABETIC";',
        "",
    ]
    row_keys = [key for row in ROWS for _label, key in row]
    # e.g. LSGT, KPDL, SPCE: not drawn in the ANSI-shaped diagram, but still
    # real keys that belong in the generated output.
    extra_keys = [k for k in layout["keys"] if k not in row_keys]
    for key in row_keys + extra_keys:
        spec = layout["keys"].get(key)
        if not spec:
            continue
        base_cps = cp_list(spec.get("base"))
        shift_cps = cp_list(spec.get("shift")) or base_cps

        def level_sym(cps, level_name, fallback):
            if len(cps) > 1:
                trigger = COMPOSE_TRIGGER.get((key, level_name))
                if trigger:
                    return f"U{trigger:04X}"  # PUA trigger; see avayi.XCompose for what it composes to
                lines.append(f"    // {key} {level_name}: multi-codepoint, no compose trigger registered — skipped")
                return fallback
            if cps:
                return keysym_for(cps[0])
            return fallback

        base_sym = level_sym(base_cps, "base", "NoSymbol")
        shift_sym = level_sym(shift_cps, "shift", base_sym)
        lines.append(f"    key <{key}> {{ [ {base_sym}, {shift_sym} ] }};")
    lines.append("};")
    return "\n".join(lines) + "\n"


# --- Compose-file generation, for the multi-character keys avayi.xkb_symbols can't express directly ---
def render_compose(layout):
    lines = [
        f'# Generated from fava-standard versions/{layout["version"]}/layout.yaml',
        "# Do not hand-edit — change layout.yaml and re-run tools/render.py instead.",
        "#",
        '# Install: append to ~/.XCompose (keep an existing `include "%L"` line',
        "# first, if you have one). ubuntu-keyboard/install.sh does this for you.",
        "",
    ]
    wrote_any = False
    for key, spec in layout["keys"].items():
        if not spec:
            continue
        for level_name in ("base", "shift"):
            cps = cp_list(spec.get(level_name))
            if level_name == "shift" and not cps:
                continue  # omitted shift = same as base, not a distinct rule to compose
            if len(cps) <= 1:
                continue
            trigger = COMPOSE_TRIGGER.get((key, level_name))
            if not trigger:
                continue
            lines.append(f'<U{trigger:04X}> : "{chars_for(cps)}"  # {key} {level_name}')
            wrote_any = True
    if not wrote_any:
        lines.append("# (no multi-character keys in this version)")
    return "\n".join(lines) + "\n"


# --- diagram generation (reuses the same per-character font-fallback trick from diagram/generate.py) ---
def svg_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


ARABIC_BLOCKS = [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)]


def font_for(ch):
    cp = ord(ch)
    if any(lo <= cp <= hi for lo, hi in ARABIC_BLOCKS):
        return ARABIC_FONTS
    return LATIN_FONTS  # includes DejaVu Sans, which also covers e.g. em dash, digits, punctuation


def tspans(s):
    if not s:
        return ""
    runs, cur_font, cur_chars = [], font_for(s[0]), [s[0]]
    for ch in s[1:]:
        f = font_for(ch)
        if f == cur_font:
            cur_chars.append(ch)
        else:
            runs.append((cur_font, "".join(cur_chars)))
            cur_font, cur_chars = f, [ch]
    runs.append((cur_font, "".join(cur_chars)))
    return "".join(f'<tspan font-family="{f}">{svg_escape(t)}</tspan>' for f, t in runs)


def display_text(s):
    return PLACEHOLDER.get(s, s)


def visual_width(text):
    """Count only glyphs that actually take horizontal space — combining
    marks and zero-width joiners ride on the previous glyph for free."""
    return sum(1 for c in text if unicodedata.combining(c) == 0 and c not in ("‌", "‍"))


def fit_font_size(text, max_px, cap_size, min_size=6):
    width = visual_width(text)
    if width <= 1:
        return cap_size
    size = max_px / (width * 1.05)
    return max(min_size, min(cap_size, round(size)))


def wrap_label(text):
    """A placeholder label (e.g. the Persian name for ZWNJ) that's too long
    for one line breaks at its own embedded ZWNJ/ZWJ, if it has one —
    that's already the natural word boundary in the label itself."""
    for i, c in enumerate(text):
        if c in ("‌", "‍") and 0 < i < len(text) - 1:
            return [text[:i], text[i + 1:]]
    return [text]


def render_keyboard_svg(x0, y0, layout):
    title = f'{layout["version"]} — {layout["name"]}'
    parts = [f'<text x="{x0}" y="{y0 - 18}" font-size="16" font-weight="600" '
             f'fill="#e6e6e6">{tspans(title)}</text>']
    for row_i, row in enumerate(ROWS):
        y = y0 + row_i * (KEY_H + GAP)
        x_start = x0 + ROW_OFFSETS[row_i] * (KEY_W + GAP)
        for col_i, (label, key) in enumerate(row):
            x = x_start + col_i * (KEY_W + GAP)
            spec = layout["keys"].get(key, {})
            lo = chars_for(cp_list(spec.get("base")))
            hi = chars_for(cp_list(spec.get("shift"))) or (lo if spec.get("shift") is None else "")
            if spec.get("shift") is None:
                hi = ""  # "omitted = same as base" is a *data* convention, not a display one
            lo_disp, hi_disp = display_text(lo), display_text(hi)
            hi_size = fit_font_size(hi_disp, KEY_W - 14, 9) if hi_disp != hi else 18

            if lo_disp != lo:
                lo_lines = wrap_label(lo_disp)
                lo_size = fit_font_size(max(lo_lines, key=visual_width), KEY_W - 14, 10)
            else:
                lo_lines, lo_size = [lo_disp], 20

            if len(lo_lines) == 2:
                lo_text_svg = (
                    f'<text x="{x+KEY_W-10}" y="{y+KEY_H-24}" font-size="{lo_size}" fill="#f0f0f0" '
                    f'text-anchor="end">{tspans(lo_lines[0])}</text>'
                    f'<text x="{x+KEY_W-10}" y="{y+KEY_H-10}" font-size="{lo_size}" fill="#f0f0f0" '
                    f'text-anchor="end">{tspans(lo_lines[1])}</text>'
                )
            else:
                lo_text_svg = (
                    f'<text x="{x+KEY_W-10}" y="{y+KEY_H-12}" font-size="{lo_size}" fill="#f0f0f0" '
                    f'text-anchor="end">{tspans(lo_lines[0])}</text>'
                )

            parts.append(
                f'<g><rect x="{x}" y="{y}" width="{KEY_W}" height="{KEY_H}" rx="8" '
                f'fill="#2b2b2b" stroke="#555" stroke-width="1.5"/>'
                f'<text x="{x+8}" y="{y+16}" font-size="10" fill="#888" '
                f'font-family="sans-serif">{svg_escape(label)}</text>'
                f'<text x="{x+KEY_W-10}" y="{y+22}" font-size="{hi_size}" fill="#7fd1ff" '
                f'text-anchor="end">{tspans(hi_disp)}</text>'
                f'{lo_text_svg}</g>'
            )
    bottom = y0 + len(ROWS) * (KEY_H + GAP)
    return "\n".join(parts), bottom


def wrap_svg(fragments, width, content_height, caption):
    max_chars = max(20, int((width - 2 * PAD) / 6.2))
    words, lines, cur = caption.split(" "), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) > max_chars and cur:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    caption_top = content_height + 20
    caption_svg = "\n".join(
        f'<text x="{PAD}" y="{caption_top + i * 14}" font-size="11" fill="#777" '
        f'font-family="sans-serif">{svg_escape(line)}</text>'
        for i, line in enumerate(lines)
    )
    height = caption_top + (len(lines) - 1) * 14 + 10
    body = "\n".join(fragments)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">\n'
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="#1a1a1a"/>\n'
            f'{body}\n{caption_svg}\n</svg>')


CAPTION = ('top-right glyph = shift level, bottom-right = base level, "_" = literal space, '
           "نیم‌فآسِلِ/ZWJ = zero-width joiner marks (no visible glyph of their own)")
BOARD_W = int(13 * (KEY_W + GAP) + 60)
SINGLE_WIDTH = PAD * 2 + BOARD_W


# --- Android keyboard-XML generation (android.inputmethodservice.Keyboard format) ---
ANDROID_KEY_LABEL = {"‌": "نیم‌فاصله", "‍": "ZWJ"}  # نیم‌فاصله is the real, established Persian term for ZWNJ; no
# equivalent common Persian term for ZWJ is established, and it's not
# currently reachable from any key anyway, so it's left in Latin rather
# than inventing one.

# Keys this particular target chooses not to surface — a phone touchscreen
# doesn't need the rarely-used {}\ cluster taking up row-2 space the way a
# physical keyboard's dedicated keys do. The underlying script/layout.yaml
# still defines them; this is an Android-rendering choice only.
ANDROID_HIDE_KEYS = {"AD11", "AD12", "BKSL"}


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def render_android_keyboard(layout, shifted, with_function_row=True):
    """One android.inputmethodservice.Keyboard XML resource: either the
    unshifted or the shifted page. Every character key uses
    android:keyOutputText, so the IME only needs an onText() handler for
    them — no per-key Kotlin logic, same spirit as letting layout.yaml be
    the only hand-edited input everywhere else."""
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<!-- Generated from fava-standard versions/{layout["version"]}/layout.yaml ({"shifted" if shifted else "base"}) -->',
        "<!-- Do not hand-edit — change layout.yaml and re-run tools/render.py instead. -->",
        '<Keyboard xmlns:android="http://schemas.android.com/apk/res/android"',
        '    android:keyWidth="10%p" android:keyHeight="54dp"',
        '    android:horizontalGap="4dp" android:verticalGap="6dp">',
    ]
    code = 1000
    for row in ROWS:
        visible = [(lbl, key) for lbl, key in row if key not in ANDROID_HIDE_KEYS]
        if not visible:
            continue
        n = len(visible)
        width = round(100 / n, 3)
        lines.append(f'    <Row android:keyWidth="{width}%p">')
        for _label, key in visible:
            spec = layout["keys"].get(key) or {}
            level = spec.get("shift") if shifted else spec.get("base")
            if level is None:
                level = spec.get("base")  # shift omitted = same as base
            cps = cp_list(level)
            text = chars_for(cps) if cps else ""
            # a phone keycap is too small for the diagram's full placeholder
            # label (e.g. the Persian name for ZWNJ) — a short one here instead,
            # distinct from android:keyOutputText, which still types the real character
            label = ANDROID_KEY_LABEL.get(text, text)
            code += 1
            lines.append(
                f'        <Key android:codes="{code}" '
                f'android:keyLabel="{xml_escape(label)}" '
                f'android:keyOutputText="{xml_escape(text)}" />'
            )
        lines.append("    </Row>")

    if with_function_row:
        lines.append('    <Row android:keyWidth="12%p" android:rowEdgeFlags="bottom">')
        # momentary shift (one character, then reverts) is handled in Kotlin;
        # isSticky is deliberately omitted — that's a lock-style flag we don't want
        lines.append('        <Key android:codes="-1" android:keyLabel="⇧" android:isModifier="true" android:keyWidth="12%p" />')
        # globe/language-switch key, code 11 — same role as Gboard's own globe
        # key: hand off to the system's "switch to next IME" (FavaInputMethodService
        # handles GLOBE_CODE directly, no XML-level special casing beyond the code)
        lines.append('        <Key android:codes="11" android:keyLabel="🌐" android:keyWidth="12%p" />')
        lines.append(f'        <Key android:codes="{code+1}" android:keyLabel="{xml_escape(chars_for(cp_list(layout["keys"]["SPCE"]["base"])) or " ")}" android:keyOutputText=" " android:keyWidth="50%p" android:isRepeatable="true" />')
        lines.append('        <Key android:codes="-5" android:keyIcon="@android:drawable/ic_input_delete" android:keyWidth="13%p" android:isRepeatable="true" />')
        lines.append('        <Key android:codes="10" android:keyLabel="⏎" android:keyWidth="13%p" />')
        lines.append("    </Row>")

    lines.append("</Keyboard>")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", help="e.g. v0.0.2 (must match a versions/<name>/ folder)")
    ap.add_argument("--compare", metavar="OTHER_VERSION", help="also render OTHER_VERSION stacked below, for a diff view")
    args = ap.parse_args()

    out_dir = VERSIONS_DIR / args.version / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    layout = load_layout(args.version)

    xkb_text = render_xkb(layout)
    (out_dir / "avayi.xkb_symbols").write_text(xkb_text, encoding="utf-8")
    print(f"wrote {out_dir / 'avayi.xkb_symbols'}")

    compose_text = render_compose(layout)
    (out_dir / "avayi.XCompose").write_text(compose_text, encoding="utf-8")
    print(f"wrote {out_dir / 'avayi.XCompose'}")

    (out_dir / "avayi_keys.xml").write_text(render_android_keyboard(layout, shifted=False), encoding="utf-8")
    print(f"wrote {out_dir / 'avayi_keys.xml'}")
    (out_dir / "avayi_keys_shifted.xml").write_text(render_android_keyboard(layout, shifted=True), encoding="utf-8")
    print(f"wrote {out_dir / 'avayi_keys_shifted.xml'}")

    board_svg, bottom = render_keyboard_svg(PAD, 60, layout)
    svg = wrap_svg([board_svg], SINGLE_WIDTH, bottom + 10, CAPTION)
    (out_dir / "layout.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {out_dir / 'layout.svg'}")

    if args.compare:
        other = load_layout(args.compare)
        other_svg, other_bottom = render_keyboard_svg(PAD, 60, other)
        gap = 60
        this_y0 = other_bottom + gap
        this_svg, this_bottom = render_keyboard_svg(PAD, this_y0, layout)
        combined = wrap_svg([other_svg, this_svg], SINGLE_WIDTH, this_bottom + 10, CAPTION)
        cmp_path = out_dir / f"vs-{args.compare}.svg"
        cmp_path.write_text(combined, encoding="utf-8")
        print(f"wrote {cmp_path}")


if __name__ == "__main__":
    main()
