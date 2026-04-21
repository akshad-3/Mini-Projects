import { useRef, useState } from "react";

export default function Main() {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const clickInputBtn = () => fileInputRef.current.click();

  const onFileSelected = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setConfidence(null);
    setError(null);
  };

  const analyzeImage = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);
    setConfidence(null);
    setError(null);

    const formData = new FormData();
    formData.append("image", file);

    // Reads from .env when local, reads from Vercel dashboard when deployed
    const API = import.meta.env.VITE_API_URL || "http://localhost:5000";
    //              ↑ if env variable missing, falls back to localhost automatically

    try {
      const response = await fetch(`${API}/predict`, {
      method: "POST",
      body: formData
});

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data.result);
      setConfidence(data.confidence);

    } catch (err) {
      setError("Could not reach the server. Is app.py running?");
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <h1>Fake Image Detection</h1>
      <p>
        Enter an image to check if it's <strong>Real</strong> or{" "}
        <strong>AI Generated</strong>
      </p>

      <div id="drop-area" onClick={clickInputBtn}>
        <p>Select an image</p>
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={onFileSelected}
        />
        {preview && <img src={preview} alt="preview" />}
      </div>

      <button
        id="analyzerBtn"
        disabled={!file || loading}
        onClick={analyzeImage}
      >
        {loading ? "Analyzing..." : "Analyze Image"}
      </button>

      {result && (
        <div id="result" className={result}>
          {result === "REAL" ? "✅ REAL Image" : "🤖 AI-Generated (FAKE)"}
        </div>
      )}

      {confidence !== null && (
        <div id="confidence">Confidence: {confidence}%</div>
      )}

      {error && (
        <div id="error">{error}</div>
      )}
    </main>
  );
}