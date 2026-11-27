"""One-off: rebuild the embedded font subsets and the width table the card generator measures with.

Needs fontTools + brotli (pip install fonttools brotli). Not run in CI; its outputs are committed.
Sources (SIL OFL 1.1, see OFL-*.txt):
  https://github.com/google/fonts/raw/main/ofl/figtree/Figtree%5Bwght%5D.ttf
  https://github.com/google/fonts/raw/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf
Usage: python3 tools/fonts/build_fonts.py Figtree[wght].ttf JetBrainsMono[wght].ttf
"""
import json
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = Path(__file__).resolve().parent
CHARS = [*range(0x20, 0x7F), 0xB7, 0xD7, 0x2014, 0x2026, 0x2190, 0x2192, 0x2197, 0x21C4, 0x258C]
WEIGHTS = [300, 400, 500, 600, 700]


def make_subset(src, dst):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern"]
    opts.name_IDs = ["*"]  # keep copyright / licence names
    f = TTFont(src)
    s = subset.Subsetter(opts)
    s.populate(unicodes=CHARS)
    s.subset(f)
    f.flavor = "woff2"
    f.save(dst)


def widths(src):
    out = {}
    for w in WEIGHTS:
        f = instancer.instantiateVariableFont(TTFont(src), {"wght": w})
        upm, cmap, hmtx = f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"]
        out[str(w)] = {chr(c): round(hmtx[cmap[c]][0] / upm, 4) for c in CHARS if c in cmap}
    return out


if __name__ == "__main__":
    sans, mono = sys.argv[1:3]
    make_subset(sans, HERE / "figtree-subset.woff2")
    make_subset(mono, HERE / "jetbrains-mono-subset.woff2")
    (HERE / "metrics.json").write_text(json.dumps({"sans": widths(sans), "mono": widths(mono)}, ensure_ascii=False))
    print("ok")
