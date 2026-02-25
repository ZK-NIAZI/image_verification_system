# Benchmark Report: Inference Time Optimization

## Hardware
- **OS**: Windows
- **Python**: 3.13.3
- **Model**: BlazeFace Short Range (TFLite, float16)

## Test Images

| Image | Resolution | File Size |
|-------|-----------|-----------|
| `one_face.jpg` | 2816x1536 | 691 KB |
| `normal_lighting.jpg` | 840x560 | 84 KB |

---

## Before Optimization (BASELINE)

### one_face.jpg (2816x1536)

| Stage | Min | p50 | p95 | Max |
|-------|-----|-----|-----|-----|
| load | 35.1ms | 46.4ms | 56.4ms | 94.7ms |
| lighting | 6.7ms | 9.4ms | 14.8ms | 23.0ms |
| clarity | 58.2ms | 76.2ms | 113.4ms | 159.6ms |
| face_detection | 15.0ms | 19.6ms | 31.2ms | 51.4ms |
| **total** | **116.3ms** | **150.2ms** | **213.3ms** | **269.5ms** |

### normal_lighting.jpg (840x560)

| Stage | Min | p50 | p95 | Max |
|-------|-----|-----|-----|-----|
| load | 5.2ms | 7.2ms | 8.6ms | 8.6ms |
| lighting | 1.2ms | 1.4ms | 1.7ms | 1.8ms |
| clarity | 6.9ms | 9.5ms | 13.1ms | 22.9ms |
| face_detection | 4.8ms | 6.6ms | 8.1ms | 8.2ms |
| **total** | **18.3ms** | **24.0ms** | **30.3ms** | **38.4ms** |

**Baseline Summary**: p50 = 77.4ms, p95 = 199.9ms

---

## After Optimization (OPTIMIZED)

### Optimizations Applied
1. **Image resize cap** at 640px (longest side) before any checks
2. **Shared grayscale conversion** across lighting + clarity checks
3. **In-memory image decode** (eliminated temp-file I/O in API)
4. **Per-stage timing instrumentation** via `time.perf_counter()`

### one_face.jpg (2816x1536)

| Stage | Min | p50 | p95 | Max |
|-------|-----|-----|-----|-----|
| load | 35.5ms | 44.7ms | 60.8ms | 62.6ms |
| preprocess | 10.8ms | 12.5ms | 35.4ms | 39.8ms |
| lighting | 0.3ms | 0.4ms | 1.0ms | 1.4ms |
| clarity | 2.6ms | 3.5ms | 6.0ms | 6.0ms |
| face_detection | 3.9ms | 4.7ms | 7.1ms | 8.1ms |
| **total** | **54.4ms** | **66.2ms** | **106.1ms** | **109.0ms** |

### normal_lighting.jpg (840x560)

| Stage | Min | p50 | p95 | Max |
|-------|-----|-----|-----|-----|
| load | 5.5ms | 6.2ms | 9.6ms | 9.6ms |
| preprocess | 2.5ms | 2.8ms | 4.2ms | 4.4ms |
| lighting | 0.7ms | 0.7ms | 0.8ms | 0.9ms |
| clarity | 3.4ms | 4.0ms | 6.3ms | 6.3ms |
| face_detection | 4.4ms | 5.0ms | 7.7ms | 7.8ms |
| **total** | **17.2ms** | **19.3ms** | **27.2ms** | **27.5ms** |

**Optimized Summary**: p50 = 41.0ms, p95 = 90.0ms

---

## Improvement Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Overall p50 | 77.4ms | 41.0ms | **47% faster** |
| Overall p95 | 199.9ms | 90.0ms | **55% faster** |
| Large image p50 | 150.2ms | 66.2ms | **56% faster** |
| Large image p95 | 213.3ms | 106.1ms | **50% faster** |
| Clarity p50 (large) | 76.2ms | 3.5ms | **95% faster** |
| Face detection p50 (large) | 19.6ms | 4.7ms | **76% faster** |

## Target Confirmation

> **p95 latency: 90.0ms -- TARGET MET (< 500ms)**
