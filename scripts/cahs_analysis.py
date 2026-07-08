"""
cahs_analysis.py
-----------------
Computational analysis of CAHS (Cytosolic Abundant Heat Soluble) proteins
in Hypsibius exemplaris.

Pipeline:
1. Parse CAHS protein sequences from FASTA
2. Predict intrinsic disorder using metapredict
3. Compute charge properties (NCPR, FCR, kappa) using localCIDER
4. Generate and save publication-style visualizations

Input:  data/raw/cahs_sequences.fasta
Output: results/figures/*.png
"""

from Bio import SeqIO
import metapredict as meta
from localcider.sequenceParameters import SequenceParameters
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------
# 1. Load sequences
# -------------------------------------------------
print("Loading CAHS sequences...")
sequences = {}
for record in SeqIO.parse("data/raw/cahs_sequences.fasta", "fasta"):
    sequences[record.id] = str(record.seq)
    print(f"{record.id}: {len(record.seq)} residues")

# -------------------------------------------------
# 2. Predict intrinsic disorder
# -------------------------------------------------
print("\nPredicting intrinsic disorder with metapredict...")
disorder_scores = {}
for seq_id, seq in sequences.items():
    scores = meta.predict_disorder(seq)
    avg_disorder = np.mean(scores)
    disorder_scores[seq_id] = avg_disorder
    print(f"{seq_id}: average disorder = {avg_disorder:.3f}")

# -------------------------------------------------
# 3. Compute charge properties (NCPR, FCR, kappa)
# -------------------------------------------------
print("\nComputing charge properties with localCIDER...")
charge_data = {}
for seq_id, seq in sequences.items():
    SeqOb = SequenceParameters(seq)
    net_charge = SeqOb.get_NCPR()
    FCR = SeqOb.get_FCR()
    kappa = SeqOb.get_kappa()
    charge_data[seq_id] = {"NCPR": net_charge, "FCR": FCR, "kappa": kappa}
    print(f"{seq_id}: NCPR={net_charge:.3f}, FCR={FCR:.3f}, kappa={kappa:.3f}")

# -------------------------------------------------
# 4. Visualization — Disorder barchart
# -------------------------------------------------
print("\nGenerating disorder barchart...")
proteins = list(disorder_scores.keys())
disorder = list(disorder_scores.values())

plt.figure(figsize=(8, 5))
colors = plt.cm.viridis(np.linspace(0, 1, len(proteins)))
bars = plt.bar(proteins, disorder, color=colors)
plt.axhline(y=0.5, color="red", linestyle="--", label="Disorder threshold (0.5)")
for bar, val in zip(bars, disorder):
    plt.text(bar.get_x() + bar.get_width()/2, val + 0.01, f"{val:.3f}",
              ha="center", va="bottom")
plt.title("Structural Disorder Across CAHS Paralogs")
plt.ylabel("Average Predicted Disorder")
plt.legend()
plt.tight_layout()
plt.savefig("results/figures/disorder_barchart_final.png", dpi=300)
plt.close()

# -------------------------------------------------
# 5. Visualization — Disorder vs FCR scatter
# -------------------------------------------------
print("Generating disorder vs FCR scatter plot...")
fcr = [charge_data[p]["FCR"] for p in proteins]

plt.figure(figsize=(7, 6))
plt.scatter(disorder, fcr, s=80, c=colors)
for i, p in enumerate(proteins):
    plt.annotate(p, (disorder[i], fcr[i]),
                 textcoords="offset points", xytext=(5, 5))
plt.title("Disorder vs. Charge Content in CAHS Paralogs")
plt.xlabel("Average Disorder")
plt.ylabel("FCR (Fraction of Charged Residues)")
plt.tight_layout()
plt.savefig("results/figures/disorder_fcr_scatter_fixed.png", dpi=300)
plt.close()

# -------------------------------------------------
# 6. Visualization — FCR vs kappa scatter
# -------------------------------------------------
print("Generating FCR vs kappa scatter plot...")
kappa = [charge_data[p]["kappa"] for p in proteins]

plt.figure(figsize=(7, 6))
plt.scatter(fcr, kappa, s=80, c=colors)
for i, p in enumerate(proteins):
    plt.annotate(p, (fcr[i], kappa[i]),
                 textcoords="offset points", xytext=(5, 5))
plt.title("FCR vs Kappa Across CAHS Paralogs")
plt.xlabel("FCR (Fraction of Charged Residues)")
plt.ylabel("Kappa (Charge Patterning)")
plt.tight_layout()
plt.savefig("results/figures/fcr_kappa_scatter_fixed.png", dpi=300)
plt.close()

print("\nAll figures saved in results/figures/")

