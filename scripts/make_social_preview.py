"""Draw docs/social-preview.png (1280 x 640) with the standard library only.
The numbers on it come from results/trigger_bm25_heldout.json and results/overlap.json.
Run: .venv/bin/python scripts/make_social_preview.py   (add --check to compare without writing)"""

import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1280, 640

FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    "-": "00000 00000 00000 11111 00000 00000 00000", ".": "00000 00000 00000 00000 00000 01100 01100",
    ",": "00000 00000 00000 00000 01100 00100 01000", ":": "00000 01100 01100 00000 01100 01100 00000",
    "(": "00010 00100 01000 01000 01000 00100 00010", ")": "01000 00100 00010 00010 00010 00100 01000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}
FONT["/"] = "00001 00010 00010 00100 01000 01000 10000"

BG = (20, 26, 40)
FG = (238, 243, 236)
MUTED = (160, 170, 190)
ACCENT = (110, 196, 170)


class Canvas:
    def __init__(self, w: int, h: int, color):
        self.w, self.h = w, h
        self.rows = [bytearray(bytes(color) * w) for _ in range(h)]

    def rect(self, x0: int, y0: int, x1: int, y1: int, color) -> None:
        x0, x1 = max(0, x0), min(self.w, x1)
        if x1 <= x0:
            return
        for y in range(max(0, y0), min(self.h, y1)):
            self.rows[y][3 * x0:3 * x1] = bytes(color) * (x1 - x0)

    def text(self, s: str, x: int, y: int, scale: int, color) -> None:
        for ch in s.upper():
            for r, bits in enumerate(FONT[ch].split()):
                for c, b in enumerate(bits):
                    if b == "1":
                        self.rect(x + c * scale, y + r * scale, x + (c + 1) * scale, y + (r + 1) * scale, color)
            x += 6 * scale

    def centered(self, s: str, y: int, scale: int, color) -> None:
        if len(s) * 6 * scale - scale > self.w - 40:
            raise ValueError(f"line too wide for the image: {s}")
        self.text(s, (self.w - (len(s) * 6 * scale - scale)) // 2, y, scale, color)

    def png(self) -> bytes:
        raw = b"".join(b"\x00" + bytes(r) for r in self.rows)

        def chunk(kind: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def render() -> bytes:
    h = json.loads((ROOT / "results" / "trigger_bm25_heldout.json").read_text())
    rep = json.loads((ROOT / "results" / "overlap.json").read_text())
    planted = {tuple(sorted((p["a"], p["b"]))) for p in
               json.loads((ROOT / "examples" / "PLANTED_OVERLAPS.json").read_text())["pairs"]}
    found = len(planted & {tuple(p) for p in rep["flagged"]})
    f1 = h["metrics"]["f1"]
    img = Canvas(W, H, BG)
    img.rect(0, 0, W, 12, ACCENT)
    img.centered("SKILLTRIAL", 140, 14, FG)
    img.centered("TEST YOUR AGENT SKILLS", 290, 6, FG)
    img.centered("LINT, TOKEN BUDGET, TRIGGER PRECISION AND RECALL, OVERLAPS", 385, 3, MUTED)
    img.centered(f"HELD-OUT TRIGGER F1 {f1['value']:.3f} (CI {f1['ci95'][0]:.3f} TO {f1['ci95'][1]:.3f})", 460, 3,
                 ACCENT)
    img.centered(f"PLANTED OVERLAPS FOUND: {found} OF {len(planted)}", 510, 3, ACCENT)
    img.centered(f"OFFLINE BM25 BASELINE. {h['n_prompts']} SYNTHETIC PROMPTS. NO API KEY.", 590, 3, MUTED)
    return img.png()


def main(argv: list[str]) -> int:
    out = ROOT / "docs" / "social-preview.png"
    png = render()
    if "--check" in argv:
        ok = out.exists() and out.read_bytes() == png
        print("docs/social-preview.png matches the results files" if ok else
              "docs/social-preview.png is stale: run scripts/make_social_preview.py")
        return 0 if ok else 1
    out.write_bytes(png)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
