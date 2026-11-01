"""
Shared MRI preprocessing + dataset helpers. Used by train_model_v2.py,
evaluate_model_v2.py and generate_gradcam.py so everything stays consistent.

Image preprocessing (load_brain):
  1. grayscale
  2. crop tightly to the brain (removes black background / position cues)
  3. pad to a square (keeps aspect ratio - no stretching)
  4. per-image contrast normalisation (removes brightness/scanner shortcuts)
  5. resize to IMG_SIZE x IMG_SIZE
Returns a uint8 array of shape (IMG_SIZE, IMG_SIZE).
"""
import re
from pathlib import Path

import numpy as np
from PIL import Image

IMG_SIZE = 128          # 128 = fast on a laptop. Use 224 if you have a GPU.

# The Kaggle data contains ~6,400 ORIGINAL scans (names like mildDem99.jpg) plus tens of
# thousands of AUGMENTED copies (random-ID names like 2b70a7c4-....jpg). Augmented copies
# of the same scan end up in train AND test = leakage. Keep this True.
ORIGINALS_ONLY = True


def is_original(path):
    """Original scans are named like mildDem12, moderateDem3, nonDem100, verymildDem7."""
    return re.search(r"dem\d+$", Path(path).stem, re.I) is not None


def cache_file(size=IMG_SIZE):
    return f"cache_{size}_{'orig' if ORIGINALS_ONLY else 'all'}.npz"


def load_brain(path, size=IMG_SIZE, thresh=10, margin=4):
    with Image.open(path) as im:
        a = np.array(im.convert("L"), dtype=np.uint8)

    # 2. crop to brain bounding box
    mask = a > thresh
    if mask.sum() > 50:
        ys, xs = np.where(mask)
        y0, y1 = max(ys.min() - margin, 0), min(ys.max() + margin + 1, a.shape[0])
        x0, x1 = max(xs.min() - margin, 0), min(xs.max() + margin + 1, a.shape[1])
        a = a[y0:y1, x0:x1]

    # 4. contrast normalisation using brain pixels only
    brain_px = a[a > thresh]
    if brain_px.size > 50:
        lo, hi = np.percentile(brain_px, [1, 99])
        if hi > lo:
            a = np.clip((a.astype(np.float32) - lo) / (hi - lo), 0, 1)
            a = (a * 255).astype(np.uint8)

    # 3. pad to square
    h, w = a.shape
    s = max(h, w)
    canvas = np.zeros((s, s), dtype=np.uint8)
    oy, ox = (s - h) // 2, (s - w) // 2
    canvas[oy:oy + h, ox:ox + w] = a

    # 5. resize
    return np.array(Image.fromarray(canvas).resize((size, size), Image.BILINEAR))


def dhash_bytes(img_u8):
    """256-bit difference hash as 32 bytes. Used only to find near-duplicate images."""
    small = np.array(Image.fromarray(img_u8).resize((17, 16), Image.BILINEAR), dtype=np.int16)
    bits = (small[:, 1:] > small[:, :-1]).flatten()
    return np.packbits(bits)  # shape (32,), uint8


# ---------------------------------------------------------------------------
# Near-duplicate grouping + leak-free split
# ---------------------------------------------------------------------------
_POPCNT = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)


def _group(hashes, thresh):
    n = len(hashes)
    parent = np.arange(n)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n - 1):
        dist = _POPCNT[hashes[i + 1:] ^ hashes[i]].sum(axis=1)
        for j in np.nonzero(dist <= thresh)[0]:
            a, b = find(i), find(i + 1 + j)
            if a != b:
                parent[b] = a
    return np.array([find(i) for i in range(n)])


def make_groups(hashes, max_frac=0.05, thresholds=(20, 14, 10, 8, 6, 4, 2, 0)):
    """Group near-duplicates. Picks the LARGEST threshold that does not chain the whole
    dataset into one giant group (largest group must be <= max_frac of all images).
    Returns (group_ids, chosen_threshold, largest_group_size)."""
    n = len(hashes)
    for t in thresholds:
        g = _group(hashes, t)
        largest = int(np.unique(g, return_counts=True)[1].max())
        print(f"  hash threshold {t:2d}: {len(np.unique(g))} groups, largest = {largest}")
        if largest <= max_frac * n or t == thresholds[-1]:
            return g, t, largest


def make_split(y, groups, seed=42):
    """~72% train / ~14% val / ~14% test, whole groups stay together, classes stratified."""
    from sklearn.model_selection import StratifiedGroupKFold
    sg = StratifiedGroupKFold(n_splits=7, shuffle=True, random_state=seed)
    folds = [te for _, te in sg.split(np.zeros(len(y)), y, groups)]
    test_idx, val_idx = folds[0], folds[1]
    train_idx = np.setdiff1d(np.arange(len(y)), np.concatenate([test_idx, val_idx]))
    return train_idx, val_idx, test_idx
