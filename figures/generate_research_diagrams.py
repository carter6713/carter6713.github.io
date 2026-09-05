"""Generate the three concept diagrams used by the research blog drafts."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# Nature-figure requirement: keep SVG text editable and use a sans-serif stack.
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
# Validator-readable declarations: svg.fonttype='none'; pdf.fonttype=42
plt.rcParams["font.size"] = 8

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "blog" / "img" / "research-notes"
OUT.mkdir(parents=True, exist_ok=True)

SKILL_SCRIPTS = Path(
    os.environ.get(
        "NATURE_FIGURE_SCRIPTS",
        str(Path.home() / ".agents" / "skills" / "nature-figure" / "scripts"),
    )
)
sys.path.insert(0, str(SKILL_SCRIPTS))
from audit_panel_alignment import require_matplotlib_panel_alignment  # noqa: E402


COLORS = {
    "navy": "#0F4D92",
    "blue": "#3775BA",
    "pale_blue": "#E8F1FA",
    "teal": "#42949E",
    "pale_teal": "#E4F3F3",
    "gold": "#D29B31",
    "pale_gold": "#FBF2DD",
    "red": "#B64342",
    "pale_red": "#F8E7E5",
    "ink": "#272727",
    "gray": "#767676",
    "line": "#C8CDD2",
    "paper": "#FFFFFF",
}


def canvas():
    fig, ax = plt.subplots(figsize=(7.2, 3.85), facecolor="white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 58)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, label, *, face="white", edge=None, size=8, weight="normal"):
    edge = edge or COLORS["line"]
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.35,rounding_size=1.2",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.0,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        ha="center",
        va="center",
        fontsize=size,
        color=COLORS["ink"],
        fontweight=weight,
        linespacing=1.25,
    )
    return patch


def arrow(ax, start, end, *, color=None, style="-|>", width=1.1, dashed=False, curve=0):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=9,
        linewidth=width,
        color=color or COLORS["gray"],
        linestyle="--" if dashed else "-",
        connectionstyle=f"arc3,rad={curve}",
        shrinkA=2,
        shrinkB=2,
    )
    ax.add_patch(patch)
    return patch


def save(fig, stem):
    fig.canvas.draw()
    require_matplotlib_panel_alignment(
        fig,
        json_out=str(OUT / f"{stem}.alignment.json"),
        overlay_svg=str(OUT / f"{stem}.alignment.svg"),
        strict=True,
    )
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", dpi=600, bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)


def data_knowledge_loop():
    fig, ax = canvas()
    ax.text(2, 54.5, "Where knowledge enters a learning system", fontsize=12, fontweight="bold", color=COLORS["ink"])
    ax.text(2, 51.0, "A practical map from hybrid inputs to auditable feedback", fontsize=8, color=COLORS["gray"])

    box(ax, 2, 32, 14, 10, "Observed\ndata", face=COLORS["pale_blue"], edge=COLORS["blue"], weight="bold")
    box(ax, 2, 16, 14, 10, "Prior\nknowledge", face=COLORS["pale_gold"], edge=COLORS["gold"], weight="bold")

    stages = [
        (23, "Input &\nsampling"),
        (40, "Representation &\narchitecture"),
        (59, "Objective &\noptimization"),
        (78, "Inference &\nconstraints"),
    ]
    widths = [13, 15, 14, 14]
    for (x, label), w in zip(stages, widths):
        box(ax, x, 31, w, 11, label, face=COLORS["pale_teal"], edge=COLORS["teal"], size=7.4, weight="bold")
    for i in range(len(stages) - 1):
        x1 = stages[i][0] + widths[i]
        x2 = stages[i + 1][0]
        arrow(ax, (x1, 36.5), (x2, 36.5), color=COLORS["navy"])

    arrow(ax, (16, 37), (23, 37), color=COLORS["blue"])
    for x, _ in stages:
        arrow(ax, (16, 21), (x + 3, 31), color=COLORS["gold"], dashed=True)

    box(ax, 30, 7, 45, 9, "Evaluation: accuracy · robustness · consistency", face="#F4F5F6", edge=COLORS["line"], size=7.2, weight="bold")
    arrow(ax, (85, 31), (75, 9), color=COLORS["gray"], curve=-0.08)
    arrow(ax, (30, 11.5), (16, 19), color=COLORS["gold"], curve=-0.12)
    ax.text(17, 5.0, "evaluation updates or rejects knowledge", fontsize=7, color=COLORS["gray"])
    save(fig, "data-knowledge-loop")


def missing_class_pipeline():
    fig, ax = canvas()
    ax.text(2, 54.5, "Missing-class generation is an evaluation problem", fontsize=12, fontweight="bold", color=COLORS["ink"])
    ax.text(2, 51.0, "Separate image plausibility from recognition value and cross-domain robustness", fontsize=8, color=COLORS["gray"])

    box(ax, 2, 31, 15, 13, "Source crops\nobserved classes", face=COLORS["pale_blue"], edge=COLORS["blue"], size=7.3, weight="bold")
    box(ax, 2, 13, 15, 11, "Target crop\nmissing disease", face=COLORS["pale_red"], edge=COLORS["red"], weight="bold")
    box(ax, 24, 27, 17, 14, "Conditional\ngenerator", face=COLORS["pale_teal"], edge=COLORS["teal"], weight="bold")
    ax.text(32.5, 22.5, "class + crop + disease-region cue", fontsize=6.5, ha="center", color=COLORS["gray"])
    box(ax, 48, 27, 16, 14, "Synthetic\ncandidates", face=COLORS["pale_gold"], edge=COLORS["gold"], weight="bold")
    box(ax, 70, 31, 13, 10, "Quality &\nleakage gate", face="#F4F5F6", edge=COLORS["gray"], weight="bold")
    box(ax, 87, 31, 11, 10, "Classifier\ntraining", face=COLORS["pale_blue"], edge=COLORS["navy"], weight="bold")

    arrow(ax, (17, 37), (24, 36), color=COLORS["blue"])
    arrow(ax, (17, 18.5), (24, 31), color=COLORS["red"], dashed=True)
    arrow(ax, (41, 34), (48, 34), color=COLORS["teal"])
    arrow(ax, (64, 34), (70, 36), color=COLORS["gold"])
    arrow(ax, (83, 36), (87, 36), color=COLORS["navy"])

    checks = [
        (21, "1  Fidelity\nDoes it resemble the class?"),
        (46, "2  Utility\nDoes recognition improve?"),
        (71, "3  Generalization\nDoes it transfer domains?"),
    ]
    for x, label in checks:
        box(ax, x, 8, 22, 10, label, face="#FFFFFF", edge=COLORS["line"], size=6.7, weight="bold")
    arrow(ax, (92.5, 31), (84, 18), color=COLORS["gray"], curve=-0.08)
    arrow(ax, (76.5, 31), (59, 18), color=COLORS["gray"], curve=-0.08)
    arrow(ax, (56, 27), (34, 18), color=COLORS["gray"], curve=-0.08)
    ax.text(2, 5.0, "Guardrail: split real data first; fit generation on training data only; deduplicate before evaluation.", fontsize=7, color=COLORS["red"])
    save(fig, "missing-class-evaluation")


def semantic_3d_loop():
    fig, ax = canvas()
    ax.text(2, 54.5, "A structured semantic layer makes 3D generation maintainable", fontsize=12, fontweight="bold", color=COLORS["ink"])
    ax.text(2, 51.0, "Separate intent, assets, constraints and rendered scenes into versioned objects", fontsize=8, color=COLORS["gray"])

    box(ax, 2, 31, 13, 11, "Semantic\nrequest", face=COLORS["pale_gold"], edge=COLORS["gold"], weight="bold")
    box(ax, 2, 15, 13, 11, "GLB assets &\nmedia", face=COLORS["pale_blue"], edge=COLORS["blue"], weight="bold")

    box(ax, 21, 20, 25, 23, "Structured annotation layer\n\nEntity · relation · region\ncontent binding · provenance\nproject · version", face=COLORS["pale_teal"], edge=COLORS["teal"], size=6.8, weight="bold")
    box(ax, 51, 31, 15, 11, "Constraint\nvalidation", face="#F4F5F6", edge=COLORS["gray"], weight="bold")
    box(ax, 51, 15, 15, 11, "Scene\nassembly", face=COLORS["pale_blue"], edge=COLORS["navy"], weight="bold")
    box(ax, 73, 25, 13, 12, "Three.js\npreview", face=COLORS["pale_gold"], edge=COLORS["gold"], weight="bold")
    box(ax, 90, 25, 8, 12, "Review &\npublish", face=COLORS["pale_red"], edge=COLORS["red"], size=7.3, weight="bold")

    arrow(ax, (15, 36.5), (21, 35), color=COLORS["gold"])
    arrow(ax, (15, 20.5), (21, 27), color=COLORS["blue"])
    arrow(ax, (46, 36.5), (51, 36.5), color=COLORS["teal"])
    arrow(ax, (58.5, 31), (58.5, 26), color=COLORS["gray"])
    arrow(ax, (66, 20.5), (73, 30), color=COLORS["navy"])
    arrow(ax, (86, 31), (90, 31), color=COLORS["gold"])
    arrow(ax, (94, 25), (43, 17), color=COLORS["red"], dashed=True, curve=-0.18)

    ax.text(24, 13.5, "DRF API", fontsize=7, color=COLORS["teal"], fontweight="bold")
    ax.text(34, 13.5, "MySQL persistence", fontsize=7, color=COLORS["teal"], fontweight="bold")
    ax.text(70, 8.0, "feedback creates a new version, never an invisible overwrite", fontsize=7, ha="center", color=COLORS["red"])
    save(fig, "semantic-3d-architecture")


if __name__ == "__main__":
    data_knowledge_loop()
    missing_class_pipeline()
    semantic_3d_loop()
