"""
Retrain the Alzheimer MRI classifier (v2).

Fixes vs. the original train_model.py:
  - Uses ORIGINAL scans only (augmented copies of the same scan leaked into the test set).
  - Near-duplicate images are grouped, and whole groups go to train OR val OR test.
  - Brain is cropped + contrast-normalised (removes background & brightness shortcuts).
  - Data augmentation is done on the fly, on TRAIN data only.
  - GlobalAveragePooling instead of Flatten (model looks at WHAT is there, not WHERE).
  - Last conv block is not pooled, so Grad-CAM has a finer map.
  - Class weights for the imbalanced classes.

Run from the project root:
    python src/train_model_v2.py
Saves: models/alzheimer_cnn_v2.keras, results/class_mapping.json, results/split_v2.npz
"""
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras
from tensorflow.keras import layers

from preprocess import (IMG_SIZE, ORIGINALS_ONLY, cache_file, dhash_bytes, is_original,
                        load_brain, make_groups, make_split)

SEED = 42
BATCH = 32
EPOCHS = 25
tf.keras.utils.set_random_seed(SEED)

base_dir = Path(".")
data_dir = base_dir / "data"
results_dir = base_dir / "results"
models_dir = base_dir / "models"
results_dir.mkdir(parents=True, exist_ok=True)
models_dir.mkdir(parents=True, exist_ok=True)
best_model_path = models_dir / "alzheimer_cnn_v2.keras"
cache_path = results_dir / cache_file()

# ---------------------------------------------------------------------------
# 1. Find images (originals only) + preprocess once (cached)
# ---------------------------------------------------------------------------
exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
all_files = [p for p in data_dir.glob("**/*") if p.is_file() and p.suffix.lower() in exts]
records = sorted((str(p), p.parent.name) for p in all_files if (not ORIGINALS_ONLY or is_original(p)))
print(f"Found {len(all_files)} images in data/, using {len(records)}"
      + (" (original scans only: names like mildDem12.jpg)" if ORIGINALS_ONLY else ""))
if len(records) < 1000 and ORIGINALS_ONLY:
    raise SystemExit("Fewer than 1000 original-named images found. Your original scans may be named "
                     "differently - tell me a few of your file names, or set ORIGINALS_ONLY = False "
                     "in preprocess.py (not recommended).")

classes = sorted({r[1] for r in records})
class_to_idx = {c: i for i, c in enumerate(classes)}
num_classes = len(classes)
with open(results_dir / "class_mapping.json", "w") as f:
    json.dump(class_to_idx, f, indent=4)
print(f"Classes ({num_classes}): {class_to_idx}")

if cache_path.exists():
    print(f"Loading cached preprocessed data from {cache_path}")
    c = np.load(cache_path, allow_pickle=True)
    X, y, H = c["X"], c["y"], c["H"]
    assert len(X) == len(records), "Cache does not match data/ - delete the cache file."
else:
    X = np.zeros((len(records), IMG_SIZE, IMG_SIZE), dtype=np.uint8)
    H = np.zeros((len(records), 32), dtype=np.uint8)
    y = np.array([class_to_idx[r[1]] for r in records], dtype=np.int64)
    for i, (path, _) in enumerate(records):
        X[i] = load_brain(path)
        H[i] = dhash_bytes(X[i])
        if (i + 1) % 1000 == 0:
            print(f"  preprocessed {i + 1}/{len(records)}")
    np.savez_compressed(cache_path, X=X, y=y, H=H)

print("Images per class:", {classes[k]: int((y == k).sum()) for k in range(num_classes)})

# ---------------------------------------------------------------------------
# 2. Group near-duplicates, then split BY GROUP
# ---------------------------------------------------------------------------
print("Grouping near-duplicate images...")
groups, thresh, largest = make_groups(H)
print(f"Using hash threshold {thresh} -> {len(np.unique(groups))} groups (largest {largest})")

train_idx, val_idx, test_idx = make_split(y, groups, SEED)
assert not set(groups[train_idx]) & set(groups[test_idx]), "group leakage train/test!"
assert not set(groups[train_idx]) & set(groups[val_idx]), "group leakage train/val!"
print(f"Split -> train {len(train_idx)}, val {len(val_idx)}, test {len(test_idx)}")
for name, idx in [("train", train_idx), ("val", val_idx), ("test", test_idx)]:
    print(f"  {name}:", {classes[k]: int((y[idx] == k).sum()) for k in range(num_classes)})

n = len(X)
if not (0.08 <= len(test_idx) / n <= 0.25 and 0.08 <= len(val_idx) / n <= 0.25):
    raise SystemExit("Split sizes look wrong (test/val should each be ~14% of the data). "
                     "Stopping so you don't waste hours training. Send me the lines above.")
np.savez(results_dir / "split_v2.npz", train=train_idx, val=val_idx, test=test_idx)

# ---------------------------------------------------------------------------
# 3. tf.data pipelines (augmentation on training data only)
# ---------------------------------------------------------------------------
augment = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.04),
    layers.RandomZoom(0.10),
    layers.RandomTranslation(0.05, 0.05),
    layers.RandomContrast(0.15),
])


def make_ds(idx, training):
    xs = X[idx][..., None]
    ds = tf.data.Dataset.from_tensor_slices((xs, y[idx]))
    if training:
        ds = ds.shuffle(2048, seed=SEED)
    ds = ds.map(lambda a, b: (tf.cast(a, tf.float32) / 255.0, b), num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH)
    if training:
        ds = ds.map(lambda a, b: (augment(a, training=True), b), num_parallel_calls=tf.data.AUTOTUNE)
    return ds.prefetch(tf.data.AUTOTUNE)


train_ds, val_ds, test_ds = make_ds(train_idx, True), make_ds(val_idx, False), make_ds(test_idx, False)

# ---------------------------------------------------------------------------
# 4. Model (functional, grayscale input, GAP head)
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
x = conv_block(inp, 32, pool=True)
x = conv_block(x, 64, pool=True)
x = conv_block(x, 128, pool=True)
x = conv_block(x, 256, pool=False)     # <- Grad-CAM layer (IMG_SIZE/8 grid)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
out = layers.Dense(num_classes, activation="softmax")(x)
model = keras.Model(inp, out, name="alzheimer_cnn_v2")

model.compile(optimizer=keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

cw = compute_class_weight("balanced", classes=np.arange(num_classes), y=y[train_idx])
class_weight = {i: float(w) for i, w in enumerate(cw)}
print("Class weights:", class_weight)

callbacks = [
    keras.callbacks.ModelCheckpoint(str(best_model_path), monitor="val_loss", save_best_only=True, verbose=1),
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=7, restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1),
]

model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS,
          class_weight=class_weight, callbacks=callbacks)

# ---------------------------------------------------------------------------
# 5. Honest evaluation on the held-out, group-separated test set
# ---------------------------------------------------------------------------
best = keras.models.load_model(best_model_path)
probs = best.predict(test_ds)
pred = probs.argmax(axis=1)
true = y[test_idx]

print("\n=== TEST RESULTS (no near-duplicates shared with training) ===")
print(classification_report(true, pred, target_names=classes, digits=3, zero_division=0))
cm = confusion_matrix(true, pred, labels=range(num_classes))
print("Confusion matrix (rows = true, cols = predicted):\n", cm)

with open(results_dir / "evaluation_metrics_v2.json", "w") as f:
    json.dump({
        "test_accuracy": float((pred == true).mean()),
        "classes": classes,
        "confusion_matrix": cm.tolist(),
        "report": classification_report(true, pred, target_names=classes, output_dict=True, zero_division=0),
    }, f, indent=2)
print(f"\nSaved model: {best_model_path}")
print("Next: python src/evaluate_model_v2.py")
print("Then: python src/generate_gradcam.py <image> --model models/alzheimer_cnn_v2.keras")
