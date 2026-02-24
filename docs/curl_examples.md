# API Curl Examples

> **Base URL:** `http://localhost:8000`
>
> **Start the server first:**
> ```bash
> uvicorn app:app --reload --port 8000
> ```

---

## Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

## Verify an Image

### ✅ Valid face photo (expect SUCCESS)

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/one_face.jpg"
```

**Response:**
```json
{
  "success": true,
  "result": {
    "valid": true,
    "reason": "SUCCESS",
    "message": "All validation checks passed. Image verified.",
    "details": { ... }
  },
  "timestamp": "2026-02-24T09:00:00.000000+00:00"
}
```

---

### 🔅 Too dark (expect TOO_DARK)

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/dark_image.jpg"
```

**Response:**
```json
{
  "success": true,
  "result": {
    "valid": false,
    "reason": "TOO_DARK",
    "message": "Image is too dark/underexposed. Please upload a well-lit photo."
  }
}
```

---

### 🔆 Too bright (expect TOO_BRIGHT)

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/bright_image.jpg"
```

**Response:**
```json
{
  "success": true,
  "result": {
    "valid": false,
    "reason": "TOO_BRIGHT",
    "message": "Image is too bright/overexposed. Please reduce lighting."
  }
}
```

---

### 🌀 Blurry image (expect TOO_BLURRY)

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/blurry_image.jpg"
```

**Response:**
```json
{
  "success": true,
  "result": {
    "valid": false,
    "reason": "TOO_BLURRY",
    "message": "Image is blurry or out of focus. Please upload a sharp photo."
  }
}
```

---

### 🚫 No face detected (expect NO_FACE)

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/no_face.jpg"
```

---

### 👥 Multiple faces (expect MULTIPLE_FACES)

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/two_faces.jpg"
```

---

## Error Cases

### ❌ Invalid file type (expect 400)

```bash
curl -X POST http://localhost:8000/verify -F "file=@requirements.txt;type=text/plain"
```

**Response (HTTP 400):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "File type '.txt' is not supported. Only JPEG and PNG image files are accepted."
  }
}
```

---

### 📄 Verbose output (see headers + status code)

```bash
curl -v -X POST http://localhost:8000/verify -F "file=@assets/one_face.jpg"
```

---

### 💾 Save response to a file

```bash
curl -X POST http://localhost:8000/verify -F "file=@assets/one_face.jpg" -o result.json
```

---

### 🐍 Python (requests) example

```python
import requests

response = requests.post(
    "http://localhost:8000/verify",
    files={"file": open("assets/one_face.jpg", "rb")}
)
print(response.json())
```

---

## Swagger / Interactive Docs

Open in your browser:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
