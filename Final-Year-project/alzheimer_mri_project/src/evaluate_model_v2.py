"""
Evaluate the v2 model on the exact held-out test split saved by train_model_v2.py,
plus a few sanity checks. Does NOT overwrite your old results.

Run from the project root (after train_model_v2.py has finished):
    python src/evaluate_model_v2.py

Writes: results/confusion_matrix_v2.png, results/evaluation_full_v2.json
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tensorflow import keras

from preprocess import IMG_SIZE, cache_file

results_dir = Path("results")
model_path = Path("models") / "alzheimer_cnn_v2.keras"
cache_path = results_dir / cache_file()
mapping_path = results_dir / "class_mapping.json"
split_path = results_dir / "split_v2.npz"

for p_ in (cache_path, model_path, mapping_path, split_path):
    if not p_.exists():
        raise FileNotFoundError(f"{p_} not found - run train_model_v2.py first.")

with open(mapping_path) as f:
    class_to_idx = json.load(f)
classes = [k for k, _ in sorted(class_to_idx.items(), key=lambda kv: kv[1])]

c = np.load(cache_path, allow_pickle=True)
X, y = c["X"], c["y"]
s = np.load(split_path)
train_idx, val_idx, test_idx = s["train"], s["val"], s["test"]   # exact split used in training
print(f"Split -> train {len(train_idx)}, val {len(val_idx)}, test {len(test_idx)}")

# ---------------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------------
model = keras.models.load_model(model_path)


def predict(imgs_u8):
    return model.predict(imgs_u8[..., None].astype(np.float32) / 255.0, batch_size=64, verbose=0)


probs = predict(X[test_idx])
pred = probs.argmax(axis=1)
true = y[test_idx]
conf = probs.max(axis=1)
acc = accuracy_score(true, pred)

print("\n" + "=" * 55)
print(f"TEST ACCURACY (held-out, group-separated): {acc:.4f}")
print("=" * 55)
print(classification_report(true, pred, target_names=classes, digits=3, zero_division=0))
cm = confusion_matrix(true, pred, labels=range(len(classes)))
print("Confusion matrix (rows = true, cols = predicted):\n", cm)

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
print("\n--- SANITY CHECKS ---")
flags = []

recalls = cm.diagonal() / np.maximum(cm.sum(axis=1), 1)
for name, r in zip(classes, recalls):
    print(f"Recall {name:18s}: {r:.3f}")
    if r < 0.30:
        flags.append(f"Class '{name}' is almost never recognised (recall {r:.2f}).")

print(f"\nMean confidence when correct: {conf[pred == true].mean():.3f}")
if (pred != true).any():
    print(f"Mean confidence when WRONG:   {conf[pred != true].mean():.3f}")
    if conf[pred != true].mean() > 0.9:
        flags.append("Model is very confident even when wrong (overconfident).")
frac_sure = float((conf > 0.99).mean())
print(f"Share of predictions with >99% confidence: {frac_sure:.1%}")
if frac_sure > 0.7:
    flags.append(">70% of predictions are >99% confident - suspicious for a subtle 4-class task.")

if acc > 0.97:
    flags.append("Test accuracy >97%: still suspiciously high - leakage may remain.")

# Junk inputs: a trustworthy model should not be certain about these
rng = np.random.default_rng(0)
junk = {
    "all-black image": np.zeros((1, IMG_SIZE, IMG_SIZE), np.uint8),
    "mid-gray image": np.full((1, IMG_SIZE, IMG_SIZE), 128, np.uint8),
    "random noise": rng.integers(0, 256, (1, IMG_SIZE, IMG_SIZE), dtype=np.uint8),
}
print("\nPredictions on junk inputs (these are not brains, so lower confidence is better):")
for name, img in junk.items():
    p = predict(img)[0]
    print(f"  {name:16s} -> {classes[p.argmax()]:18s} {p.max():.1%}")
    if p.max() > 0.95:
        flags.append(f"Model is >95% sure about '{name}' - it may be keying on non-anatomical cues.")

print("\n" + ("RESULT: no red flags raised." if not flags else "RED FLAGS:"))
for f_ in flags:
    print("  -", f_)

# ---------------------------------------------------------------------------
# Save confusion matrix plot + metrics
# ---------------------------------------------------------------------------
cmn = cm / np.maximum(cm.sum(axis=1, keepdims=True), 1)
fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(classes)), classes, rotation=30, ha="right")
ax.set_yticks(range(len(classes)), classes)
for i in range(len(classes)):
    for j in range(len(classes)):
        ax.text(j, i, f"{cm[i, j]}\n({cmn[i, j]:.0%})", ha="center", va="center",
                color="white" if cmn[i, j] > 0.5 else "black", fontsize=10)
ax.set_xlabel("Predicted label")
ax.set_ylabel("True label")
ax.set_title(f"Confusion Matrix - held-out test set (accuracy {acc:.2%})")
fig.colorbar(im, ax=ax, fraction=0.046, label="Row-normalised")
fig.tight_layout()
fig.savefig(results_dir / "confusion_matrix_v2.png", dpi=200)

with open(results_dir / "evaluation_full_v2.json", "w") as f:
    json.dump({
        "test_accuracy": float(acc),
        "n_test": int(len(test_idx)),
        "classes": classes,
        "confusion_matrix": cm.tolist(),
        "mean_confidence_correct": float(conf[pred == true].mean()),
        "share_over_99pct_confidence": frac_sure,
        "red_flags": flags,
        "report": classification_report(true, pred, target_names=classes, output_dict=True, zero_division=0),
    }, f, indent=2)
print("\nSaved: results/confusion_matrix_v2.png, results/evaluation_full_v2.json")
