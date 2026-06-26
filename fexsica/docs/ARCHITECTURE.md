# FeXsics: Architecture Documentation

## System Architecture Overview

FeXsics implements a 7-layer physics-grounded architecture for forensic image analysis.

### Core Philosophy

Traditional forensic tools provide binary classifications without scientific foundation.
FeXsics ensures every verdict is justified by measuring violations against physical laws
and statistical principles.

### Layer Integration Flow

```
Input Image
    ↓
Layer 1: Photon Physics (Illumination Analysis)
    ↓
Layer 2: Signal Processing (Sensor & Noise Physics)
    ↓
Layer 3: Geometry & Perspective (3D Consistency)
    ↓
Layer 4: Compression Physics (JPEG Analysis)
    ↓
Layer 5: Deep Learning (Neural Network Verification)
    ↓
Layer 6: Metadata & Chain of Custody (EXIF & Provenance)
    ↓
Layer 7: Bayesian Fusion → Expert Testimony → Verdict
```

## Implementation Guidelines

### Adding a New Physics Engine

1. Create module in appropriate `layers/` subdirectory
2. Inherit from base physics engine (if applicable)
3. Implement core analysis methods
4. Return standardized result dictionary:
   ```python
   {
       "status": "analysis_complete",
       "findings": {...},
       "confidence": 0.0-1.0,
       "evidence": {...}
   }
   ```

### Integration with Bayesian Engine

Each layer provides evidence that updates the Bayesian posterior:

```python
likelihood_ratio = P(evidence|forged) / P(evidence|authentic)
engine.add_evidence(layer_name, likelihood_ratio)
verdict = engine.get_verdict()
```

### Reporting Standards

All analysis results must be:
1. **Reproducible**: Same input → Same output
2. **Explainable**: Physics-grounded reasoning
3. **Defensible**: Courtroom-grade evidence

## Performance Considerations

- Layer execution time: < 30 seconds per 4K image
- Memory usage: < 8GB for standard analysis
- GPU acceleration: Optional but recommended
- Batch processing: Supported for multiple images

## Extending FeXsics

### Adding a New Detection Model

1. Implement in `layers/deep_learning/`
2. Lazy-load pretrained weights
3. Provide confidence thresholds
4. Integrate with Layer 5 fusion

### Adding a New Analysis Metric

1. Create method in appropriate layer
2. Return standardized evidence format
3. Update Bayesian fusion weights
4. Add unit test coverage

## Quality Assurance

- All code requires type hints
- Minimum 80% test coverage
- Code review before merge
- Performance benchmarks maintained
