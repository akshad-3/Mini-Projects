from flask import Flask, request, jsonify
from flask_cors import CORS
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

CORS(app)
print("⏳ Loading model...")
model = tf.keras.models.load_model("cifake_model.h5")
print("✅ Model loaded! Server ready.")

@app.route("/")
def home():
    return jsonify({"message": "CIFAKE API is running!"})

def prepare_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    img = img.resize((32, 32))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, 0)
    return img_array

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image found."}), 400

    image_bytes = request.files["image"].read()

    try:
        img_array = prepare_image(image_bytes)
    except Exception as e:
        return jsonify({"error": f"Could not read image: {str(e)}"}), 400

    prediction = model.predict(img_array)[0][0]

    if prediction >= 0.5:
        result = "REAL"
        confidence = round(float(prediction) * 100, 2)
    else:
        result = "FAKE"
        confidence = round((1 - float(prediction)) * 100, 2)

    return jsonify({"result": result, "confidence": confidence})

if __name__ == "__main__":
    #app.run(debug=True, port=5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)