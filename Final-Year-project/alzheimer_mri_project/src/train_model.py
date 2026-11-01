import os
import json
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

# Define paths
base_dir = Path(".")
data_dir = base_dir / "data"
results_dir = base_dir / "results"
models_dir = base_dir / "models"

results_dir.mkdir(parents=True, exist_ok=True)
models_dir.mkdir(parents=True, exist_ok=True)

valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}

print("Scanning dataset for training...")
image_records = []
for ext in valid_extensions:
    for img_path in data_dir.glob(f"**/*{ext}"):
        if img_path.is_file():
            cls_name = img_path.parent.name
            image_records.append((str(img_path), cls_name))

if not image_records:
    raise ValueError("No images found in data/ directory!")

# Discover classes and encode labels
classes = sorted(list(set([r[1] for r in image_records])))
class_to_idx = {cls_name: idx for idx, cls_name in enumerate(classes)}
num_classes = len(classes)

print(f"Discovered Classes ({num_classes}): {classes}")

# Save class mapping
with open(results_dir / "class_mapping.json", "w") as f:
    json.dump(class_to_idx, f, indent=4)

paths = [r[0] for r in image_records]
labels = [class_to_idx[r[1]] for r in image_records]

# Stratified Split: 70% Train, 15% Val, 15% Test
train_paths, temp_paths, train_labels, temp_labels = train_test_split(
    paths, labels, test_size=0.30, random_state=42, stratify=labels
)
val_paths, test_paths, val_labels, test_labels = train_test_split(
    temp_paths, temp_labels, test_size=0.50, random_state=42, stratify=temp_labels
)

print(f"Split sizes -> Train: {len(train_paths)}, Val: {len(val_paths)}, Test: {len(test_paths)}")

# tf.data Pipeline
def load_and_preprocess(path, label):
    image = tf.io.read_file(path)
    image = tf.image.decode_image(image, channels=3, expand_animations=False)
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, [224, 224])
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

AUTOTUNE = tf.data.AUTOTUNE

def create_dataset(image_paths, labels_list, is_training=False):
    dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels_list))
    dataset = dataset.map(load_and_preprocess, num_parallel_calls=AUTOTUNE)
    if is_training:
        dataset = dataset.shuffle(buffer_size=1000)
    dataset = dataset.batch(32)
    dataset = dataset.prefetch(buffer_size=AUTOTUNE)
    return dataset

train_dataset = create_dataset(train_paths, train_labels, is_training=True)
val_dataset = create_dataset(val_paths, val_labels, is_training=False)

# Build CNN Model
model = keras.Sequential([
    keras.Input(shape=(224, 224, 3)),
    layers.Conv2D(32, (3, 3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    
    layers.Conv2D(64, (3, 3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Dropout(0.25),
    
    layers.Conv2D(128, (3, 3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Dropout(0.25),
    
    layers.Flatten(),
    layers.Dense(256),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.Dropout(0.5),
    
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# Callbacks
best_model_path = models_dir / "alzheimer_cnn_best.keras"
callbacks = [
    keras.callbacks.EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True, verbose=1),
    keras.callbacks.ModelCheckpoint(filepath=str(best_model_path), monitor='val_loss', save_best_only=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6, verbose=1)
]

# Train Model (set epochs to 10 or 20 for local quick testing)
EPOCHS = 15
print(f"\nStarting local model training for up to {EPOCHS} epochs...")

history = model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=EPOCHS,
    callbacks=callbacks
)

print(f"\nTraining complete! Best model saved to: {best_model_path}")
