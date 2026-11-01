"""
Data loading for the OASIS-style dataset (file names like OAS1_0042_MR1_slice_30.jpg).
The patient ID is read from the file name, so train/val/test can be split BY PATIENT.
No TensorFlow needed here.
"""
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from preprocess import IMG_SIZE, load_brain

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
PATIENT_RE = re.compile(r"(OAS\d+_\d+)", re.I)
SESSION_RE = re.compile(r"(MR\d+)", re.I)
SLICE_RE = re.compile(r"(?:slice[_-]?|_)(\d+)$", re.I)      # slice number = trailing digits
MPR_RE = re.compile(r"mpr-?(\d+)", re.I)                    # acquisition number (mpr-1, mpr-2 ...)



def merge_name(name):
    """Convert original OASIS classes into binary classes."""

    normalized = re.sub(r"[\s_-]+", "", name).lower()

    if "non" in normalized and "dement" in normalized:
        return "Non Demented"

    if "dement" in normalized:
        return "Dementia"

    raise ValueError(f"Unknown dataset class folder: {name}")



def build_records(data_dir, max_per_scan=30, slice_min=None, slice_max=None, merge_moderate=False):
    """Return a list of (path, class_name, patient_id, scan_id, slice_no, mpr_no).
    At most `max_per_scan` evenly spaced slices are kept per scan, so 86,000 files
    become a fast-to-train sample without losing any patient."""
    data_dir = Path(data_dir)
    files = [p for p in data_dir.glob("**/*") if p.is_file() and p.suffix.lower() in EXTS]
    if not files:
        raise SystemExit(f"No images found in {data_dir}")

    rows, bad = [], []
    for p in files:
        m = PATIENT_RE.search(p.stem)
        if not m:
            bad.append(p.name)
            continue
        s = SLICE_RE.search(p.stem)
        sl = int(s.group(1)) if s else -1
        mr = SESSION_RE.search(p.stem)
        mpr = MPR_RE.search(p.stem)
        patient = m.group(1).upper()
        scan = f"{patient}_{mr.group(1).upper() if mr else 'MR'}"
        cls = merge_name(p.parent.name) if merge_moderate else p.parent.name
        rows.append((str(p), cls, patient, scan, sl, int(mpr.group(1)) if mpr else 0))
    if bad:
        print(f"WARNING: {len(bad)} files have no patient ID and were skipped, e.g. {bad[:3]}")
    if not rows:
        raise SystemExit("No file names contain a patient ID like OAS1_0042. Send me 5 example names.")

    by_scan = defaultdict(list)
    for r in rows:
        if slice_min is not None and r[4] < slice_min:
            continue
        if slice_max is not None and r[4] > slice_max:
            continue
        by_scan[(r[1], r[3])].append(r)

    chosen = []
    for items in by_scan.values():
        items.sort(key=lambda r: (r[4], r[5]))
        if len(items) > max_per_scan:
            idx = np.unique(np.linspace(0, len(items) - 1, max_per_scan).round().astype(int))
            items = [items[i] for i in idx]
        chosen += items
    chosen.sort(key=lambda r: r[0])
    print(f"Found {len(files)} images, using {len(chosen)} "
          f"(max {max_per_scan} slices per scan)")
    return chosen


def load_data(data_dir, out_dir, max_per_scan=30, slice_min=None, slice_max=None, merge_moderate=False):
    """Returns X (N,S,S) uint8, y, patient_ids, classes, cache_path. Cached on disk."""
    rows = build_records(data_dir, max_per_scan, slice_min, slice_max, merge_moderate)
    classes = sorted({r[1] for r in rows})
    class_to_idx = {c: i for i, c in enumerate(classes)}
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = [r[0] for r in rows]
    cache = out_dir / f"cache_{IMG_SIZE}_m{max_per_scan}_s{slice_min}-{slice_max}{'_binary' if merge_moderate else ''}.npz"
    if cache.exists():
        c = np.load(cache)
        if list(c["paths"]) == paths:
            print(f"Loaded cached preprocessed images from {cache}")
            return c["X"], c["y"], c["pat"], classes, cache
        print("Cache is out of date - rebuilding")

    X = np.zeros((len(rows), IMG_SIZE, IMG_SIZE), dtype=np.uint8)
    y = np.array([class_to_idx[r[1]] for r in rows], dtype=np.int64)
    pat = np.array([r[2] for r in rows])
    for i, r in enumerate(rows):
        X[i] = load_brain(r[0])
        if (i + 1) % 2000 == 0:
            print(f"  preprocessed {i + 1}/{len(rows)}")
    np.savez_compressed(cache, X=X, y=y, pat=pat, paths=np.array(paths))
    return X, y, pat, classes, cache
