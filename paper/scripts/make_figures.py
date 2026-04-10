#!/usr/bin/env python3
"""
Generate the figures for the ECD paper from the canonical condition_*.jsonl files.

Outputs (PNG, 300 DPI, monochrome):
  paper/figures/fig1_d_distribution.png   — D histogram per condition (stacked)
  paper/figures/fig2_d_box.png             — D box plot per condition
  paper/figures/fig3_d_ecdf.png            — Empirical CDF of D per condition
  paper/figures/fig4_verification_rates.png — Verification result distribution per condition

The figures are sealed: they only read the canonical files and the analysis result JSON,
they do not re-run the analysis or alter any field. Re-running this script always
produces byte-identical PNGs from the same input.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent.parent
C0 = REPO / "data" / "condition_0.jsonl"
C1 = REPO / "data" / "condition_1.jsonl"
RESULT = REPO / "results" / "canonical_result.json"
FIG_DIR = REPO / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Style: monochrome, journal-friendly
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "axes.grid": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "figure.dpi": 100,
})

C0_COLOR = "#888888"   # control: medium gray
C1_COLOR = "#222222"   # treatment: near-black


def load(path: Path) -> list[dict]:
    out = []
    with path.open() as f:
        for line in f:
            out.append(json.loads(line))
    return out


def D(trace: dict) -> int:
    return sum(1 for c in trace.get("claims", []) if c.get("status") == "UNRESOLVED")


def main() -> int:
    c0_traces = [t for t in load(C0) if not t.get("excluded")]
    c1_traces = [t for t in load(C1) if not t.get("excluded")]
    print(f"loaded c0: {len(c0_traces)} included")
    print(f"loaded c1: {len(c1_traces)} included")

    D0 = [D(t) for t in c0_traces]
    D1 = [D(t) for t in c1_traces]

    # ── Figure 1: histogram, side-by-side bars ──────────────────────────────
    max_d = max(max(D0), max(D1))
    bins = list(range(max_d + 2))
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    ax.hist(
        [D0, D1],
        bins=bins,
        align="left",
        rwidth=0.85,
        color=[C0_COLOR, C1_COLOR],
        label=[f"Condition 0 (no SRS, n={len(D0)})", f"Condition 1 (behavioral SRS, n={len(D1)})"],
    )
    ax.set_xlabel("D = count of UNRESOLVED claims per trace")
    ax.set_ylabel("number of traces")
    ax.set_xticks(bins[:-1])
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    ax.set_title("Distribution of ECD scores per condition")
    fig.savefig(FIG_DIR / "fig1_d_distribution.png")
    plt.close(fig)
    print(f"wrote {FIG_DIR / 'fig1_d_distribution.png'}")

    # ── Figure 2: box plot ──────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    bp = ax.boxplot(
        [D0, D1],
        labels=["c0\nno SRS", "c1\nbehavioral SRS"],
        widths=0.5,
        patch_artist=True,
        showfliers=True,
        flierprops={"marker": ".", "markersize": 3, "alpha": 0.4, "markeredgecolor": "none", "markerfacecolor": "black"},
    )
    for patch, color in zip(bp["boxes"], [C0_COLOR, C1_COLOR]):
        patch.set_facecolor(color)
        patch.set_edgecolor("black")
    for median in bp["medians"]:
        median.set_color("white")
        median.set_linewidth(1.5)
    ax.set_ylabel("D")
    ax.set_title("ECD by condition (with outliers)")
    fig.savefig(FIG_DIR / "fig2_d_box.png")
    plt.close(fig)
    print(f"wrote {FIG_DIR / 'fig2_d_box.png'}")

    # ── Figure 3: empirical CDF ─────────────────────────────────────────────
    def ecdf(values):
        s = sorted(values)
        n = len(s)
        xs = []
        ys = []
        prev = None
        for i, v in enumerate(s, 1):
            if v != prev:
                xs.append(v)
                ys.append(i / n)
                prev = v
        return xs, ys

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    x0, y0 = ecdf(D0)
    x1, y1 = ecdf(D1)
    ax.step(x0, y0, where="post", color=C0_COLOR, linewidth=1.5, label=f"c0 (n={len(D0)})")
    ax.step(x1, y1, where="post", color=C1_COLOR, linewidth=1.5, label=f"c1 (n={len(D1)})")
    ax.set_xlabel("D")
    ax.set_ylabel("F(D)  =  fraction of traces with D ≤ x")
    ax.set_title("Empirical CDF of D per condition")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", framealpha=1.0, edgecolor="black")
    fig.savefig(FIG_DIR / "fig3_d_ecdf.png")
    plt.close(fig)
    print(f"wrote {FIG_DIR / 'fig3_d_ecdf.png'}")

    # ── Figure 4: verification result distribution ─────────────────────────
    def verif_counts(traces):
        return Counter(t.get("verification_result") for t in traces)
    v0 = verif_counts(c0_traces)
    v1 = verif_counts(c1_traces)
    categories = ["PASS", "FAIL", "RUNTIME_ERROR", "TIMEOUT"]
    vals0 = [v0.get(c, 0) for c in categories]
    vals1 = [v1.get(c, 0) for c in categories]

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    x = list(range(len(categories)))
    w = 0.38
    ax.bar([i - w/2 for i in x], vals0, width=w, color=C0_COLOR, edgecolor="black", linewidth=0.6, label=f"c0 (n={len(c0_traces)})")
    ax.bar([i + w/2 for i in x], vals1, width=w, color=C1_COLOR, edgecolor="black", linewidth=0.6, label=f"c1 (n={len(c1_traces)})")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("number of traces")
    ax.set_title("Deterministic verification result by condition")
    ax.legend(loc="upper right", framealpha=1.0, edgecolor="black")
    fig.savefig(FIG_DIR / "fig4_verification_rates.png")
    plt.close(fig)
    print(f"wrote {FIG_DIR / 'fig4_verification_rates.png'}")

    # Quick summary
    print()
    print(f"c0 mean D:   {sum(D0)/len(D0):.4f}")
    print(f"c1 mean D:   {sum(D1)/len(D1):.4f}")
    print(f"c0 max D:    {max(D0)}")
    print(f"c1 max D:    {max(D1)}")
    print(f"c0 nonzero:  {sum(1 for d in D0 if d > 0)} of {len(D0)}")
    print(f"c1 nonzero:  {sum(1 for d in D1 if d > 0)} of {len(D1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
