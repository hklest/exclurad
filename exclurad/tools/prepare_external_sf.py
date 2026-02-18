#!/usr/bin/env python3
"""Prepare EXCLURAD external structure-function tables.

Input rows can be either:
  5 columns: Q2 W cos(theta_cm) sigma_T sigma_L
  8 columns: Q2 W cos(theta_cm) sigma_T sigma_L sigma_TT sigma_LT sigma_LTp

For 5-column input, sigma_TT/sigma_LT/sigma_LTp are filled from command-line defaults
(default 0.0 for each).
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_line(line: str):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split()
    if len(parts) not in (5, 8):
        raise ValueError(f"Expected 5 or 8 columns, got {len(parts)}: {line}")
    vals = [float(x) for x in parts]
    return vals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", required=True, help="Input table path")
    ap.add_argument("--outfile", required=True, help="Output table path")
    ap.add_argument("--default-tt", type=float, default=0.0, help="Default sigma_TT for 5-column rows")
    ap.add_argument("--default-lt", type=float, default=0.0, help="Default sigma_LT for 5-column rows")
    ap.add_argument("--default-ltp", type=float, default=0.0, help="Default sigma_LTp for 5-column rows")
    args = ap.parse_args()

    inp = Path(args.infile)
    out = Path(args.outfile)

    rows = []
    for ln, line in enumerate(inp.read_text().splitlines(), start=1):
        parsed = parse_line(line)
        if parsed is None:
            continue
        if len(parsed) == 5:
            q2, w, cth, st, sl = parsed
            parsed = [q2, w, cth, st, sl, args.default_tt, args.default_lt, args.default_ltp]
        rows.append(parsed)

    if not rows:
        raise SystemExit("No numeric rows were parsed.")

    header = "# Q2 W cos(theta_cm) sigma_T sigma_L sigma_TT sigma_LT sigma_LTp"
    lines = [header]
    for r in rows:
        lines.append(" ".join(f"{v:.8g}" for v in r))
    out.write_text("\n".join(lines) + "\n")

    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
