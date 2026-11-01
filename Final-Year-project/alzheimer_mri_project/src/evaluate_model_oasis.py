"""
Evaluate the OASIS model on its held-out test PATIENTS.
Reports accuracy per slice AND per patient (average the predictions of all of a patient's slices),
plus sanity checks. Run after train_model_oasis.py:
    python src/evaluate_model_oasis.py
Writes: results/oasis/confusion_matrix.png, results/oasis/evaluation_full.json
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow import keras

out_dir = Path("results") / "oasis"
model_path = Path("models") / "alzheimer_oasis.keras"
for p in (out_dir / "split.npz", out_dir / "class_mapping.json", model_path):
    if not p.exists():
        raise FileNotFoundError(f"{p} not found - run train_model_oasis.py first.")

with open(out_dir / "class_mapping.json") as f:
    c2i = json.load(f)
classes = [k for k, _ in sorted(c2i.items(), key=lambda kv: kv[1])]
K = len(classes)

s = np.load(out_dir / "split.npz")
test_idx = s["test"]
c = np.load(str(s["cache"]))
X, y, pat = c["X"], c["y"], c["pat"]
print(f"Test set: {len(test_idx)} slices from {len(set(pat[test_idx]))} patients (none seen in training)")

model = keras.models.load_model(model_path)


def predict(imgs):
    return model.predict(imgs[..., None].astype(np.float32) / 255.0, batch_size=64, verbose=0)


probs = predict(X[test_idx])
pred = probs.argmax(1)
true = y[test_idx]
conf = probs.max(1)
flags = []

# ---------------- slice level ----------------
acc_s = accuracy_score(true, pred)
cm_s = confusion_matrix(true, pred, labels=range(K))
print("\n" + "=" * 55 + f"\nSLICE-LEVEL test accuracy: {acc_s:.4f}\n" + "=" * 55)
print(classification_report(true, pred, target_names=classes, digits=3, zero_division=0))
print("Confusion matrix (rows = true, cols = predicted):\n", cm_s)

# ---------------- patient level ----------------
tp = pat[test_idx]
pats = sorted(set(tp))
p_true, p_pred = [], []
for p in pats:
    m = tp == p
    p_true.append(Counter(true[m]).most_common(1)[0][0])
    p_pred.append(int(probs[m].mean(0).argmax()))
p_true, p_pred = np.array(p_true), np.array(p_pred)
acc_p = accuracy_score(p_true, p_pred)
cm_p = confusion_matrix(p_true, p_pred, labels=range(K))
print("\n" + "=" * 55 + f"\nPATIENT-LEVEL test accuracy: {acc_p:.4f}  ({len(pats)} patients)\n" + "=" * 55)
print(classification_report(p_true, p_pred, labels=range(K), target_names=classes, digits=3, zero_division=0))
print("Patient confusion matrix:\n", cm_p)

# ---------------- sanity checks ----------------
print("\n--- SANITY CHECKS ---")
for k in range(K):
    n_pat = int(cm_p[k].sum())
    rec = cm_s[k, k] / max(cm_s[k].sum(), 1)
    print(f"{classes[k]:20s} test patients: {n_pat:3d} | slice recall: {rec:.3f}")
    if n_pat < 5:
        flags.append(f"'{classes[k]}' has only {n_pat} test patients - result unreliable.")
    if rec < 0.30:
        flags.append(f"'{classes[k]}' is almost never recognised (slice recall {rec:.2f}).")
print(f"\nMean confidence when correct: {conf[pred == true].mean():.3f}")
if (pred != true).any():
    print(f"Mean confidence when WRONG:   {conf[pred != true].mean():.3f}")
    if conf[pred != true].mean() > 0.9:
        flags.append("Very confident even when wrong (overconfident).")
if (conf > 0.99).mean() > 0.7:
    flags.append(">70% of predictions are >99% confident - suspicious.")
if acc_s > 0.97:
    flags.append("Slice accuracy >97% - still suspiciously high; check for leakage or an easy shortcut.")

rng = np.random.default_rng(0)
junk = {"all-black": np.zeros((1,) + X.shape[1:], np.uint8),
        "mid-gray": np.full((1,) + X.shape[1:], 128, np.uint8),
        "random noise": rng.integers(0, 256, (1,) + X.shape[1:], dtype=np.uint8)}
print("\nJunk inputs (lower confidence is better):")
for name, img in junk.items():
    pj = predict(img)[0]
    print(f"  {name:13s} -> {classes[pj.argmax()]:20s} {pj.max():.1%}")
    if pj.max() > 0.95:
        flags.append(f"Model is >95% sure about '{name}' - may use non-anatomical cues.")

print("\n" + ("RESULT: no red flags raised." if not flags else "RED FLAGS:"))
for f_ in flags:
    print("  -", f_)

# ---------------- plots + json ----------------
fig, axs = plt.subplots(1, 2, figsize=(14, 6))
for ax, cm, title in [(axs[0], cm_s, f"Slice level (acc {acc_s:.1%})"),
                      (axs[1], cm_p, f"Patient level (acc {acc_p:.1%})")]:
    cmn = cm / np.maximum(cm.sum(1, keepdims=True), 1)
    ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(K), classes, rotation=30, ha="right")
    ax.set_yticks(range(K), classes)
    for i in range(K):
        for j in range(K):
            ax.text(j, i, f"{cm[i, j]}\n({cmn[i, j]:.0%})", ha="center", va="center",
                    color="white" if cmn[i, j] > 0.5 else "black", fontsize=9)
    ax.set_title(title)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
fig.tight_layout()
fig.savefig(out_dir / "confusion_matrix.png", dpi=200)
with open(out_dir / "evaluation_full.json", "w") as f:
    json.dump({"slice_accuracy": float(acc_s), "patient_accuracy": float(acc_p),
               "n_test_slices": int(len(test_idx)), "n_test_patients": len(pats), "classes": classes,
               "slice_confusion": cm_s.tolist(), "patient_confusion": cm_p.tolist(),
               "red_flags": flags}, f, indent=2)
print("\nSaved: results/oasis/confusion_matrix.png, results/oasis/evaluation_full.json")
