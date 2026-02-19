#!/usr/bin/env python3
"""Analyze EXCLURAD outputs and produce quick plots."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

PROTON_MASS = 0.9382720813
PI0_MASS = 0.1349768
PIP_MASS = 0.13957039
NEUTRON_MASS = 0.9395654133


def load_cols(path: Path, ncols: int) -> list[list[float]]:
    rows: list[list[float]] = []
    if not path.exists():
        raise FileNotFoundError(path)
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s:
            continue
        parts = s.split()
        if len(parts) < ncols:
            continue
        try:
            vals = [float(parts[i]) for i in range(ncols)]
        except ValueError:
            continue
        rows.append(vals)
    if not rows:
        raise RuntimeError(f"No numeric rows parsed from {path}")
    return rows


def lambda_kallen(a: float, b: float, c: float) -> float:
    return a * a + b * b + c * c - 2 * (a * b + a * c + b * c)


def t_from_w_q2_costh(w: float, q2: float, costh: float, ivec: int) -> float:
    mN = PROTON_MASS
    if ivec in (1, 3):
        m_pi = PI0_MASS if ivec == 1 else 1.019461
        m_rec = PROTON_MASS
    else:
        m_pi = PIP_MASS if ivec == 2 else 1.019461
        m_rec = NEUTRON_MASS if ivec == 2 else PROTON_MASS

    eg = (w * w - mN * mN - q2) / (2.0 * w)
    qmag = math.sqrt(max(eg * eg + q2, 0.0))

    e_pi = (w * w + m_pi * m_pi - m_rec * m_rec) / (2.0 * w)
    k2 = lambda_kallen(w * w, m_pi * m_pi, m_rec * m_rec) / (4.0 * w * w)
    kmag = math.sqrt(max(k2, 0.0))

    return m_pi * m_pi - 2.0 * (eg * e_pi - qmag * kmag * costh)


def scatter(plt, out: Path, x, yv, xlabel: str, ylabel: str, title: str, name: str) -> None:
    plt.figure(figsize=(6, 4))
    plt.scatter(x, yv, s=25)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / name, dpi=150)
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="directory containing radcor.dat etc")
    ap.add_argument("--ebeam", type=float, required=True, help="beam energy [GeV]")
    ap.add_argument("--ivec", type=int, default=1, choices=[1, 2, 3, 4], help="1: p, 2: pi+, 3: p(phi recoil), 4: phi(p recoil)")
    ap.add_argument("--out", default="plots", help="output plots directory")
    args = ap.parse_args()

    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise SystemExit(f"matplotlib is required for plotting: {exc}")

    base = Path(args.dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    radcor = load_cols(base / "radcor.dat", 8)
    W = [r[0] for r in radcor]
    Q2 = [r[1] for r in radcor]
    csth = [r[3] for r in radcor]
    phi = [r[4] for r in radcor]
    rc_full = [r[5] for r in radcor]
    born_check = [r[6] for r in radcor]
    rc_ll = [r[7] for r in radcor]

    y = [(w * w + q2 - PROTON_MASS * PROTON_MASS) / (2.0 * PROTON_MASS * args.ebeam) for w, q2 in zip(W, Q2)]
    tvals = [t_from_w_q2_costh(w, q2, c, args.ivec) for w, q2, c in zip(W, Q2, csth)]

    sig_ratio = None
    plus = base / "radsigpl.dat"
    minus = base / "radsigmi.dat"
    if plus.exists() and minus.exists():
        p = load_cols(plus, 7)
        m = load_cols(minus, 7)
        n = min(len(p), len(m), len(radcor))
        sig_ratio = []
        q2n = []
        for i in range(n):
            born_u = 0.5 * (p[i][5] + m[i][5])
            rad_u = 0.5 * (p[i][6] + m[i][6])
            if born_u != 0:
                sig_ratio.append(rad_u / born_u)
                q2n.append(radcor[i][1])
    else:
        q2n = []

    scatter(plt, out, Q2, rc_full, r"$Q^2$ [GeV$^2$]", "RC factor (sig/sib)", "Radiative correction vs Q2", "rc_vs_q2.png")
    scatter(plt, out, W, rc_full, "W [GeV]", "RC factor (sig/sib)", "Radiative correction vs W", "rc_vs_w.png")
    scatter(plt, out, phi, rc_full, r"$\phi_{cm}$ [deg]", "RC factor (sig/sib)", "Radiative correction vs phi", "rc_vs_phi.png")
    scatter(plt, out, csth, rc_full, r"cos($\theta_{cm}$)", "RC factor (sig/sib)", "Radiative correction vs cos(theta)", "rc_vs_costh.png")
    scatter(plt, out, y, rc_full, "y", "RC factor (sig/sib)", "Radiative correction vs y", "rc_vs_y.png")
    scatter(plt, out, tvals, rc_full, r"t [GeV$^2$]", "RC factor (sig/sib)", "Radiative correction vs t (approx)", "rc_vs_t.png")
    scatter(plt, out, Q2, born_check, r"$Q^2$ [GeV$^2$]", "sib/sibt", "Born consistency check", "born_check_vs_q2.png")
    scatter(plt, out, Q2, rc_ll, r"$Q^2$ [GeV$^2$]", "sigll/sib", "LL approximation correction", "rc_ll_vs_q2.png")

    if sig_ratio:
        scatter(plt, out, q2n, sig_ratio, r"$Q^2$ [GeV$^2$]", "rad/nonrad (unpolarized)", "Cross section ratio vs Q2", "sigma_ratio_vs_q2.png")

    print(f"Wrote plots to: {out}")


if __name__ == "__main__":
    main()
