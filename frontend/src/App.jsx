import { useState, useCallback } from 'react';
import HealthBadge from './components/HealthBadge';
import UploadZone from './components/UploadZone';
import ResultCard from './components/ResultCard';

const API_BASE = import.meta.env.VITE_API_URL || 'https://vision.rentalforce.app';

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verbose, setVerbose] = useState(false);

  const handleVerify = useCallback(async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const url = `${API_BASE}/verify${verbose ? '?verbose=true' : ''}`;
      const res = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      if (!data.success) {
        setError(data.error?.message || 'Verification failed.');
        return;
      }

      // Normalize response for both minimal and verbose modes
      setResult({
        valid: data.valid ?? data.result?.valid,
        reason: data.reason ?? data.result?.reason,
        message: data.message ?? data.result?.message,
        result: data.result || null,
        inference_time_ms: data.inference_time_ms,
      });
    } catch (err) {
      setError(`Could not reach the API. Please ensure the server is running.\n${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [file, verbose]);

  const handleFileSelect = useCallback((f) => {
    setFile(f);
    setResult(null);
    setError(null);
  }, []);

  return (
    <div className="app">
      {/* Hero Section */}
      <header className="hero">
        <div className="hero__badge">
          <span className="hero__badge-dot" />
          AI-Powered Verification
        </div>
        <h1 className="hero__title">Image Verification</h1>
        <p className="hero__subtitle">
          Upload a photo to verify it meets quality standards —
          good lighting, sharp clarity, and exactly one face detected.
        </p>
        <HealthBadge />
      </header>

      {/* Upload Zone */}
      <UploadZone
        file={file}
        onFileSelect={handleFileSelect}
        disabled={loading}
      />

      {/* Controls */}
      <div className="controls">
        <button
          className="controls__btn controls__btn--primary"
          onClick={handleVerify}
          disabled={!file || loading}
          id="verify-btn"
        >
          {loading ? (
            <>
              <span className="spinner" />
              Analyzing...
            </>
          ) : (
            <>🔍 Verify Image</>
          )}
        </button>

        <label className="controls__toggle" id="verbose-toggle">
          <input
            type="checkbox"
            checked={verbose}
            onChange={(e) => setVerbose(e.target.checked)}
          />
          <span className="controls__toggle-track" />
          Verbose
        </label>
      </div>

      {/* Error */}
      {error && (
        <div className="error-card" id="error-card">
          <span className="error-card__icon">⚠️</span>
          <div className="error-card__text">
            <strong>Error</strong>
            {error}
          </div>
        </div>
      )}

      {/* Result */}
      <ResultCard result={result} verbose={verbose} />
    </div>
  );
}
