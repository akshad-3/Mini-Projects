"""
Train on the big OASIS-style dataset (file names like OAS1_0042_MR1_slice_30.jpg),
splitting BY PATIENT so no person appears in both train and test.

Run from the project root:
    python src/train_model_oasis.py --data-dir data_86k
Options:
    --max-per-scan 30     slices kept per scan (lower = faster)
    --slice-min / --slice-max   keep only slices in this range (drop empty top/bottom slices)
    --epochs 20

Saves everything under results/oasis/ and models/alzheimer_oasis.keras,
so your other model and results are NOT touched.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras import layers

from oasis_data import load_data
from preprocess import IMG_SIZE, make_split

ap = argparse.ArgumentParser()
ap.add_argument("--data-dir", default="data_86k")
ap.add_argument("--max-per-scan", type=int, default=30)
ap.add_argument("--slice-min", type=int, default=None)
ap.add_argument("--slice-max", type=int, default=None)
ap.add_argument("--epochs", type=int, default=20)
ap.add_argument("--merge-moderate", action="store_true",
                help="convert all dementia folders into one Dementia class")
ap.add_argument("--inspect-only", action="store_true",
                help="inspect dataset and splits without training")
args = ap.parse_args()

SEED, BATCH = 42, 32
tf.keras.utils.set_random_seed(SEED)

out_dir = Path("results") / "oasis"
models_dir = Path("models")
out_dir.mkdir(parents=True, exist_ok=True)
models_dir.mkdir(parents=True, exist_ok=True)
model_path = models_dir / "alzheimer_oasis.keras"

# ---------------------------------------------------------------------------
# 1. Data + patient-level split
# ---------------------------------------------------------------------------
X, y, pat, classes, cache_path = load_data(args.data_dir, out_dir, args.max_per_scan,
                                           args.slice_min, args.slice_max, args.merge_moderate)
num_classes = len(classes)
with open(out_dir / "class_mapping.json", "w") as f:
    json.dump({c: i for i, c in enumerate(classes)}, f, indent=4)
print(f"Classes ({num_classes}): {classes}")


def per_class(idx):
    out = {}
    for k in range(num_classes):
        sel = idx[y[idx] == k]
        out[classes[k]] = f"{len(sel)} imgs / {len(set(pat[sel]))} patients"
    return out


print(f"\nTotal: {len(X)} images from {len(set(pat))} patients")
print("All data:", per_class(np.arange(len(X))))

for k in range(num_classes):
    n_all = len(set(pat[y == k]))
    if n_all < 10:
        print(f"  WARNING: '{classes[k]}' has only {n_all} patients in the WHOLE dataset - a model cannot learn "
              f"or be tested fairly on that few people. Consider --merge-moderate.")

multi = [p for p in set(pat) if len(set(y[pat == p])) > 1]
if multi:
    print(f"Note: {len(multi)} patients appear in more than one class folder (kept as is).")

_, groups = np.unique(pat, return_inverse=True)
train_idx, val_idx, test_idx = make_split(y, groups, SEED)
assert not set(pat[train_idx]) & set(pat[test_idx]), "patient leakage train/test!"
assert not set(pat[train_idx]) & set(pat[val_idx]), "patient leakage train/val!"

print(f"\nSplit -> train {len(train_idx)}, val {len(val_idx)}, test {len(test_idx)}  (NO patient shared)")
for name, idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
    print(f"  {name}:", per_class(idx))
for k in range(num_classes):
    n_test_pat = len(set(pat[test_idx][y[test_idx] == k]))
    if n_test_pat < 5:
        print(f"  WARNING: '{classes[k]}' has only {n_test_pat} test patients - its test result will be unreliable.")

n = len(X)
if not (0.05 <= len(test_idx) / n <= 0.30 and 0.05 <= len(val_idx) / n <= 0.30):
    raise SystemExit("Split sizes look wrong - stopping before wasting hours. Send me the lines above.")
if args.inspect_only:
    print("\nInspection completed. Training was NOT started.")
    raise SystemExit(0)

# ---------------------------------------------------------------------------
# 2. Pipelines (augmentation on training data only)
# ---------------------------------------------------------------------------
augment = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.04),
    layers.RandomZoom(0.10),
    layers.RandomTranslation(0.05, 0.05),
    layers.RandomContrast(0.15),
])


def make_ds(idx, training):
    ds = tf.data.Dataset.from_tensor_slices((X[idx][..., None], y[idx]))
    if training:
        ds = ds.shuffle(4096, seed=SEED)
    ds = ds.map(lambda a, b: (tf.cast(a, tf.float32) / 255.0, b), num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH)
    if training:
        ds = ds.map(lambda a, b: (augment(a, training=True), b), num_parallel_calls=tf.data.AUTOTUNE)
    return ds.prefetch(tf.data.AUTOTUNE)


train_ds, val_ds, test_ds = make_ds(train_idx, True), make_ds(val_idx, False), make_ds(test_idx, False)

# ---------------------------------------------------------------------------
# 3. Model
# ---------------------------------------------------------------------------
def conv_block(x, filters, pool):
    for _ in range(2):
        x = layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
    if pool:
        x = layers.MaxPooling2D(2)(x)
    return x


inp = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 1))
x = conv_block(inp, 32, True)
x = conv_block(x, 64, True)
x = conv_block(x, 128, True)
x = conv_block(x, 256, False)          # <- Grad-CAM layer
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
out = layers.Dense(num_classes, activation="softmax")(x)
model = keras.Model(inp, out, name="alzheimer_cnn_oasis")
model.compile(optimizer=keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

cw = compute_class_weight("balanced", classes=np.arange(num_classes), y=y[train_idx])
class_weight = {i: float(w) for i, w in enumerate(cw)}
print("Class weights:", class_weight)

callbacks = [
    keras.callbacks.ModelCheckpoint(str(model_path), monitor="val_loss", save_best_only=True, verbose=1),
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1),
]
model.fit(train_ds, validation_data=val_ds, epochs=args.epochs,
          class_weight=class_weight, callbacks=callbacks)

# ---------------------------------------------------------------------------
# 4. Quick test result (run evaluate_model_oasis.py for the full report)
# ---------------------------------------------------------------------------
best = keras.models.load_model(model_path)
pred = best.predict(test_ds).argmax(axis=1)
print("\n=== TEST RESULTS (patients never seen in training) ===")
print(classification_report(y[test_idx], pred, target_names=classes, digits=3, zero_division=0))
print(f"Saved model: {model_path}")
print("Next: python src/evaluate_model_oasis.py")
