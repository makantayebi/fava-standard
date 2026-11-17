# TODO: targets with no implementation yet

Each of these is a real platform + physical-keyboard combination that
isn't built yet. See `targets.yaml` for the two that *are* implemented
(`ubuntu-us-ansi`, `android`) and `README.md`'s "Script version vs.
target version" section for what "target" means here.

- **windows-us-ansi** — `windows-keyboard` currently ships `v0.0.1`
  only (the original design) and has never been updated to track later
  script versions. Needs: regenerate `Farsi-Avayi.klc` from the latest
  `layout.yaml` (no generator for this yet — `tools/render.py` only
  emits XKB/Compose/Android output so far, not `.klc`).
- **windows-eu-iso** — same as above, but needs a second `.klc` using
  ISO scancodes (the `OEM_102` / scancode `0x56` key) instead of ANSI's
  layout — Windows `.klc` files are scancode-based and genuinely
  distinguish the two, unlike XKB.
- **ubuntu-eu-iso** — possibly not a real target at all. XKB's keyboard
  geometry already maps the same `symbols/avayi` section onto either
  physical shape; investigate whether `ubuntu-us-ansi`'s existing
  implementation already covers ISO keyboards correctly before building
  anything separate here.
- **apple-us-ansi** — macOS keyboard layouts use an entirely different
  format (`.keylayout` XML, via Apple's own tooling), not XKB or `.klc`.
  No generator exists for this yet.
- **apple-eu-iso** — same format question as apple-us-ansi, plus
  whatever the ISO-equivalent distinction turns out to be on macOS
  (needs research — Apple's physical/logical key handling doesn't
  necessarily split along the same lines Windows does).
- **ios** — `ios-keyboard` repo exists as a placeholder only. iOS custom
  keyboard extensions have their own constraints (e.g. no system-wide
  Compose-equivalent) that haven't been investigated yet.

Possible additional targets not in the original list, worth considering
before ruling out:
- **web** — a browser-extension or PWA-based virtual keyboard, for
  typing Fava anywhere without installing a native app per platform.
- **chromeos** — Chrome OS has its own input-method-extension system,
  related to but distinct from both Android and a browser extension;
  worth checking whether `android`'s work covers it via ARC or needs
  its own target.
