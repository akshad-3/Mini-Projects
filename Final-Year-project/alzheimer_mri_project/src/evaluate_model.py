import os
import json
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns

# Define paths
base_dir = Path(".")
data_dir = base_dir / "data"
results_dir = base_dir / "results"
models_dir = base_dir / "models"

# 1. Load class mapping
mapping_path = results_dir / "class_mapping.json"
if not mapping_path.exists():
    raise FileNotFoundError(f"Class mapping not found at {mapping_path}.")

with open(mapping_path, "r") as f:
    class_to_idx = json.load(f)

idx_to_class = {v: k for k, v in class_to_idx.items()}
classes = [idx_to_class[i] for i in range(len(idx_to_class))]
num_classes = len(classes)

print(f"Loaded classes for evaluation: {classes}")

# 2. Reconstruct Test Split
valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
image_records = []
for ext in valid_extensions:
    for img_path in data_dir.glob(f"**/*{ext}"):
        if img_path.is_file():
            cls_name = img_path.parent.name
            if cls_name in class_to_idx:
                image_records.append((str(img_path), class_to_idx[cls_name]))

paths = [r[0] for r in image_records]
labels = [r[1] for r in image_records]

# Stratified split mirroring training
train_paths, temp_paths, train_labels, temp_labels = train_test_split(
    paths, labels, test_size=0.30, random_state=42, stratify=labels
)
val_paths, test_paths, val_labels, test_labels = train_test_split(
    temp_paths, temp_labels, test_size=0.50, random_state=42, stratify=temp_labels
)

print(f"Test Dataset Size: {len(test_paths)} images")

# 3. Create Test tf.data Pipeline
def load_and_preprocess(path, label):
    image = tf.io.read_file(path)
    image = tf.image.decode_image(image, channels=3, expand_animations=False)
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, [224, 224])
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

AUTOTUNE = tf.data.AUTOTUNE
test_dataset = tf.data.Dataset.from_tensor_slices((test_paths, test_labels))
test_dataset = test_dataset.map(load_and_preprocess, num_parallel_calls=AUTOTUNE).batch(32).prefetch(AUTOTUNE)

# 4. Load Best Trained Model
best_model_path = models_dir / "alzheimer_cnn_best.keras"
if not best_model_path.exists():
    raise FileNotFoundError(f"Best model not found at {best_model_path}. Please complete training first!")

model = keras.models.load_model(best_model_path)
print("Loaded best trained model successfully.")

# 5. Evaluate on Test Dataset
print("\nEvaluating model on test dataset...")
test_loss, test_acc = model.evaluate(test_dataset)

# Get Predictions
y_true = np.array(test_labels)
y_pred_probs = model.predict(test_dataset)
y_pred = np.argmax(y_pred_probs, axis=1)

# Calculate Macro/Weighted Metrics (handling class imbalance safely)
precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)

print("\n" + "=" * 50)
print("TEST EVALUATION METRICS:")
print("=" * 50)
print(f"Test Loss:      {test_loss:.4f}")
print(f"Test Accuracy:  {test_acc:.4f}")
print(f"Weighted Precision: {precision:.4f}")
print(f"Weighted Recall:    {recall:.4f}")
print(f"Weighted F1-Score:  {f1:.4f}")

# Classification Report
report = classification_report(y_true, y_pred, target_names=classes, zero_division=0)
print("\nClassification Report:\n")
print(report)

# Save evaluation results
eval_results = {
    "test_loss": float(test_loss),
    "test_accuracy": float(test_acc),
    "weighted_precision": float(precision),
    "weighted_recall": float(recall),
    "weighted_f1": float(f1),
    "classification_report": classification_report(y_true, y_pred, target_names=classes, output_dict=True, zero_division=0)
}

with open(results_dir / "evaluation_metrics.json", "w") as f:
    json.dump(eval_results, f, indent=4)
print(f"📁 Saved evaluation metrics to: {results_dir / 'evaluation_metrics.json'}")

# 6. Confusion Matrix Plot & Save
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title(f'Confusion Matrix (Test Accuracy: {test_acc:.2%})', fontsize=12)
plt.xlabel('Predicted Label', fontsize=10)
plt.ylabel('True Label', fontsize=10)
plt.tight_layout()

cm_path = results_dir / "confusion_matrix.png"
plt.savefig(cm_path, dpi=300)
print(f"📊 Saved confusion matrix plot to: {cm_path}")
plt.show()

print("\n=== Step 7: Model Evaluation Completed Successfully ===")
