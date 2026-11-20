#!/usr/bin/env python3
"""Render a layout.yaml into its platform/visual artifacts.

    python3 tools/render.py v0.0.2
        writes versions/v0.0.2/generated/avayi.xkb_symbols
           and versions/v0.0.2/generated/layout.svg
        — the shared BASE script, used as-is by any target that hasn't
        forked its own layout (e.g. ubuntu-us-ansi today).

    python3 tools/render.py v0.0.2 --compare v0.0.1
        also writes versions/v0.0.2/generated/vs-v0.0.1.svg,
        both versions stacked in one diagram for an at-a-glance diff.

    python3 tools/render.py v0.0.6 --target android
        writes layouts/android/v0.0.6/generated/avayi_keys.xml,
           avayi_keys_shifted.xml, and android_layout.svg
        — a target-specific FORK (its own layout.yaml, diverging from
        the base script for reasons specific to that platform), with its
        own independent version numbering. Only produces the artifacts
        that target actually uses (no XKB/Compose for android).

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
LAYOUTS_DIR = ROOT / "layouts"

# Which targets have their own tracked layout under layouts/<name>/, and
# what they're currently forked from. A target can track the base script
# exactly (no actual divergence yet, like ubuntu-us-ansi) and still live
# here — "has its own version number" and "has actually diverged" are
# different questions. Add an entry here for a new target (see
# layouts/README.md).
TARGET_ARTIFACTS = {
    "android": "android",      # android_keys.xml/_shifted.xml + android_layout.svg
    "ubuntu-us-ansi": "xkb",   # avayi.xkb_symbols + avayi.XCompose + layout.svg, same as the base script
}

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


def load_layout(version, target=None):
    base = (LAYOUTS_DIR / target) if target else VERSIONS_DIR
    path = base / version / "layout.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


ACTION_BACKSPACE = "BACKSPACE"  # a key that performs an action instead of
# typing a character. Checked for explicitly at each render site rather
# than taught to cp_list, since "what codepoints does this type" stops
# being the right question once a key isn't typing anything.
ACTION_SHIFT = "SHIFT"  # the physical shift control, relocatable into the
# main key grid (layouts/android/v0.0.7 moves it to AB01) instead of only
# ever living in the Android function row.


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
        if spec.get("base") == ACTION_BACKSPACE:
            lines.append(f"    key <{key}> {{ [ BackSpace, BackSpace ] }};")
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
            if spec.get(level_name) == ACTION_BACKSPACE:
                continue
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


def key_svg(x, y, w, h, corner_label, lo, hi):
    """One key box: corner_label is the small physical-key-name hint
    (top-left), hi is the shift-level glyph (top-right, blue), lo is the
    base-level glyph (bottom-right, wraps to two lines if it has an
    embedded ZWNJ/ZWJ). Shared by the physical-layout diagram and the
    Android on-screen-layout diagram so they stay visually consistent."""
    lo_disp, hi_disp = display_text(lo), display_text(hi)
    hi_size = fit_font_size(hi_disp, w - 14, 9) if hi_disp != hi else 18

    if lo_disp != lo:
        lo_lines = wrap_label(lo_disp)
        lo_size = fit_font_size(max(lo_lines, key=visual_width), w - 14, 10)
    else:
        lo_lines, lo_size = [lo_disp], 20

    if len(lo_lines) == 2:
        lo_text_svg = (
            f'<text x="{x+w-10}" y="{y+h-24}" font-size="{lo_size}" fill="#f0f0f0" '
            f'text-anchor="end">{tspans(lo_lines[0])}</text>'
            f'<text x="{x+w-10}" y="{y+h-10}" font-size="{lo_size}" fill="#f0f0f0" '
            f'text-anchor="end">{tspans(lo_lines[1])}</text>'
        )
    else:
        lo_text_svg = (
            f'<text x="{x+w-10}" y="{y+h-12}" font-size="{lo_size}" fill="#f0f0f0" '
            f'text-anchor="end">{tspans(lo_lines[0])}</text>'
        )

    return (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
        f'fill="#2b2b2b" stroke="#555" stroke-width="1.5"/>'
        f'<text x="{x+8}" y="{y+16}" font-size="10" fill="#888" '
        f'font-family="sans-serif">{svg_escape(corner_label)}</text>'
        f'<text x="{x+w-10}" y="{y+22}" font-size="{hi_size}" fill="#7fd1ff" '
        f'text-anchor="end">{tspans(hi_disp)}</text>'
        f'{lo_text_svg}</g>'
    )


def key_lo_hi(spec, page="shift"):
    """A key's corner-display text, honoring the "omitted level = same as
    base" data convention and the action-key sentinels (backspace,
    shift). page="shift" (default) returns (base-display, shift-display)
    for the usual two-corner diagram; page="symbols" returns
    (symbols-display, "") — the symbols page has no second level of its
    own to show in the other corner."""
    base_val = spec.get("base")
    if base_val == ACTION_BACKSPACE:
        return "⌫", ""
    if base_val == ACTION_SHIFT:
        return "⇧", ""
    if page == "symbols":
        sym_val = spec.get("symbols", base_val)  # omitted = same as base
        return chars_for(cp_list(sym_val)), ""
    lo = chars_for(cp_list(base_val))
    hi = chars_for(cp_list(spec.get("shift"))) or (lo if spec.get("shift") is None else "")
    if spec.get("shift") is None:
        hi = ""  # "omitted = same as base" is a *data* convention, not a display one
    return lo, hi


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
            lo, hi = key_lo_hi(spec)
            parts.append(key_svg(x, y, KEY_W, KEY_H, label, lo, hi))
    bottom = y0 + len(ROWS) * (KEY_H + GAP)
    return "\n".join(parts), bottom


def render_android_svg(x0, y0, layout, page="shift"):
    """What the Android on-screen keyboard actually shows, for a given
    page ("shift" = the normal base/shift two-corner view, "symbols" =
    the ۱۲۳ page): the {}\\ cluster (and others — see ANDROID_HIDE_KEYS)
    hidden, the ZWNJ key labeled with its Android symbol, and a 5th row
    for the function keys that only exist on this target. Mirrors
    avayi_keys*.xml, not the physical ANSI diagram above."""
    page_label = " — ۱۲۳ page" if page == "symbols" else ""
    title = f'{layout["version"]} — {layout["name"]} (Android on-screen layout{page_label})'
    parts = [f'<text x="{x0}" y="{y0 - 18}" font-size="16" font-weight="600" '
             f'fill="#e6e6e6">{tspans(title)}</text>']
    android_rows = [[(lbl, key) for lbl, key in row if key not in ANDROID_HIDE_KEYS] for row in ROWS]
    for row_i, row in enumerate(android_rows):
        y = y0 + row_i * (KEY_H + GAP)
        n = len(row)
        w = (BOARD_W - (n - 1) * GAP) / n
        for col_i, (label, key) in enumerate(row):
            x = x0 + col_i * (w + GAP)
            spec = layout["keys"].get(key, {})
            lo, hi = key_lo_hi(spec, page=page)
            lo_disp = ANDROID_KEY_LABEL.get(lo, lo).replace("\\n", "\n")
            parts.append(key_svg(x, y, w, KEY_H, label, lo_disp, hi))

    func_y = y0 + len(android_rows) * (KEY_H + GAP)
    zwnj_text = chars_for(cp_list(layout["keys"]["FUNCROW_ZWNJ"]["base"]))
    zwnj_disp = ANDROID_KEY_LABEL.get(zwnj_text, zwnj_text).replace("\\n", "\n")
    toggle_label = "ABC" if page == "symbols" else "۱۲۳"
    func_row = [("toggle", toggle_label, ""), ("globe", "🌐", ""), ("space", "␣", ""),
                ("zwnj", zwnj_disp, ""), ("enter", "⏎", "")]
    func_widths = [0.12, 0.12, 0.50, 0.13, 0.13]
    fx = x0
    for (corner, lo, hi), frac in zip(func_row, func_widths):
        w = BOARD_W * frac
        parts.append(key_svg(fx, func_y, w, KEY_H, corner, lo, hi))
        fx += w + GAP
    bottom = func_y + KEY_H + GAP
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
ANDROID_KEY_LABEL = {"‌": "◂┆▸", "‍": "ZWJ"}  # نیم‌فاصله (the real Persian term
# for ZWNJ) was too wide for a ~10%-width key at the Android keyboard's label
# text size and overflowed past the key — and the screen's left edge, since
# it's the leftmost key in its row. This glyph-based symbol (narrowing arrows
# around a thin break) fits a single line and reads as "half-space" visually.
# equivalent common Persian term for ZWJ is established, and it's not
# currently reachable from any key anyway, so it's left in Latin rather
# than inventing one.

# Keys this particular target chooses not to surface — a phone touchscreen
# doesn't need the rarely-used {}\ cluster taking up row-2 space the way a
# physical keyboard's dedicated keys do. The underlying script/layout.yaml
# still defines them; this is an Android-rendering choice only.
# AB09 (v0.0.7): the dot it typed is already reachable via shift+AB06
# (د) as of v0.0.6 — removed to save space next to the AB10 backspace key.
ANDROID_HIDE_KEYS = {"AD11", "AD12", "BKSL", "AB09"}


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


SYMBOLS_CODE = 12  # the ۱۲۳/ABC page-toggle key — FavaInputMethodService
# handles this directly, same spirit as GLOBE_CODE.


def render_android_keyboard(layout, page, with_function_row=True):
    """One android.inputmethodservice.Keyboard XML resource for one page:
    "base", "shift", or "symbols". Every character key uses
    android:keyOutputText, so the IME only needs an onText() handler for
    them — no per-key Kotlin logic, same spirit as letting layout.yaml be
    the only hand-edited input everywhere else. A key with no explicit
    value for the requested page falls back to "base" (same "omitted =
    same as base" convention already used for shift, extended to a
    third level)."""
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        f'<!-- Generated from fava-standard layouts/android/{layout["version"]}/layout.yaml ({page}) -->',
        "<!-- Do not hand-edit — change layout.yaml and re-run tools/render.py instead. -->",
        '<Keyboard xmlns:android="http://schemas.android.com/apk/res/android"',
        '    android:keyWidth="10%p" android:keyHeight="54dp"',
        '    android:horizontalGap="0px" android:verticalGap="0px">',
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
            level = spec.get(page) if page != "base" else spec.get("base")
            if level is None:
                level = spec.get("base")  # omitted level = same as base
            if level == ACTION_BACKSPACE:
                lines.append(
                    '        <Key android:codes="-5" '
                    'android:keyIcon="@android:drawable/ic_input_delete" '
                    'android:isRepeatable="true" />'
                )
                continue
            if level == ACTION_SHIFT:
                # momentary shift (one character, then reverts) is handled
                # in Kotlin; isSticky is deliberately omitted — that's a
                # lock-style flag we don't want
                lines.append(
                    '        <Key android:codes="-1" android:keyLabel="⇧" '
                    'android:isModifier="true" />'
                )
                continue
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
        if page == "symbols":
            # same control, code 12 either way — FavaInputMethodService
            # toggles the page and doesn't care which label was showing
            lines.append('        <Key android:codes="12" android:keyLabel="ABC" android:keyWidth="12%p" />')
        else:
            lines.append('        <Key android:codes="12" android:keyLabel="۱۲۳" android:keyWidth="12%p" />')
        # globe/language-switch key, code 11 — same role as Gboard's own globe
        # key: hand off to the system's "switch to next IME" (FavaInputMethodService
        # handles GLOBE_CODE directly, no XML-level special casing beyond the code)
        lines.append('        <Key android:codes="11" android:keyLabel="🌐" android:keyWidth="12%p" />')
        lines.append(f'        <Key android:codes="{code+1}" android:keyLabel="{xml_escape(chars_for(cp_list(layout["keys"]["SPCE"]["base"])) or " ")}" android:keyOutputText=" " android:keyWidth="50%p" android:isRepeatable="true" />')
        zwnj_text = chars_for(cp_list(layout["keys"]["FUNCROW_ZWNJ"]["base"]))
        zwnj_label = ANDROID_KEY_LABEL.get(zwnj_text, zwnj_text)
        lines.append(f'        <Key android:codes="{code+2}" android:keyLabel="{xml_escape(zwnj_label)}" android:keyOutputText="{xml_escape(zwnj_text)}" android:keyWidth="13%p" />')
        lines.append('        <Key android:codes="10" android:keyLabel="⏎" android:keyWidth="13%p" />')
        lines.append("    </Row>")

    lines.append("</Keyboard>")
    return "\n".join(lines) + "\n"


def render_base(args):
    """The shared script: XKB symbols, Compose file, and the physical-
    layout diagram. Used as-is by any target that hasn't forked its own
    layout (see load_layout / --target for targets that have)."""
    out_dir = VERSIONS_DIR / args.version / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    layout = load_layout(args.version)

    xkb_text = render_xkb(layout)
    (out_dir / "avayi.xkb_symbols").write_text(xkb_text, encoding="utf-8")
    print(f"wrote {out_dir / 'avayi.xkb_symbols'}")

    compose_text = render_compose(layout)
    (out_dir / "avayi.XCompose").write_text(compose_text, encoding="utf-8")
    print(f"wrote {out_dir / 'avayi.XCompose'}")

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


def render_target(args):
    """A target-specific fork: its own layout.yaml under layouts/<target>/
    <version>/, producing only the artifacts that target actually uses."""
    target = args.target
    if target not in TARGET_ARTIFACTS:
        sys.exit(f"error: unknown --target '{target}' (known: {', '.join(TARGET_ARTIFACTS)})")

    out_dir = LAYOUTS_DIR / target / args.version / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    layout = load_layout(args.version, target=target)
    kind = TARGET_ARTIFACTS[target]

    if kind == "android":
        has_symbols_page = any(spec and "symbols" in spec for spec in layout["keys"].values())

        (out_dir / "avayi_keys.xml").write_text(render_android_keyboard(layout, page="base"), encoding="utf-8")
        print(f"wrote {out_dir / 'avayi_keys.xml'}")
        (out_dir / "avayi_keys_shifted.xml").write_text(render_android_keyboard(layout, page="shift"), encoding="utf-8")
        print(f"wrote {out_dir / 'avayi_keys_shifted.xml'}")
        if has_symbols_page:
            (out_dir / "avayi_keys_symbols.xml").write_text(render_android_keyboard(layout, page="symbols"), encoding="utf-8")
            print(f"wrote {out_dir / 'avayi_keys_symbols.xml'}")

        android_svg, android_bottom = render_android_svg(PAD, 60, layout)
        android_wrapped = wrap_svg([android_svg], SINGLE_WIDTH, android_bottom + 10, CAPTION)
        (out_dir / "android_layout.svg").write_text(android_wrapped, encoding="utf-8")
        print(f"wrote {out_dir / 'android_layout.svg'}")

        if has_symbols_page:
            symbols_svg, symbols_bottom = render_android_svg(PAD, 60, layout, page="symbols")
            symbols_wrapped = wrap_svg([symbols_svg], SINGLE_WIDTH, symbols_bottom + 10, CAPTION)
            (out_dir / "android_layout_symbols.svg").write_text(symbols_wrapped, encoding="utf-8")
            print(f"wrote {out_dir / 'android_layout_symbols.svg'}")

    elif kind == "xkb":
        (out_dir / "avayi.xkb_symbols").write_text(render_xkb(layout), encoding="utf-8")
        print(f"wrote {out_dir / 'avayi.xkb_symbols'}")
        (out_dir / "avayi.XCompose").write_text(render_compose(layout), encoding="utf-8")
        print(f"wrote {out_dir / 'avayi.XCompose'}")
        board_svg, bottom = render_keyboard_svg(PAD, 60, layout)
        svg = wrap_svg([board_svg], SINGLE_WIDTH, bottom + 10, CAPTION)
        (out_dir / "layout.svg").write_text(svg, encoding="utf-8")
        print(f"wrote {out_dir / 'layout.svg'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version", help="e.g. v0.0.2 — a versions/<name>/ folder, or layouts/<target>/<name>/ with --target")
    ap.add_argument("--compare", metavar="OTHER_VERSION", help="also render OTHER_VERSION stacked below, for a diff view (base script only)")
    ap.add_argument("--target", metavar="NAME", help="render a target-specific fork (layouts/<NAME>/<version>/layout.yaml) instead of the shared base script")
    args = ap.parse_args()

    if args.target:
        render_target(args)
    else:
        render_base(args)


if __name__ == "__main__":
    main()
