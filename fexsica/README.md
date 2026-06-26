"""FeXsics: Physics-Grounded Multimodal Forensic Justification Architecture

## Overview

FeXsics is a comprehensive forensic image analysis platform designed for courtroom-grade evidence verification. It moves beyond traditional "black box" tools by ensuring every verdict is justified at the physics level.

## Features

- **7-Layer Physics Architecture**: Each layer analyzes different physical principles
- **Physics-Grounded Verification**: Verdicts justified by measurable physical law violations
- **Deep Learning Integration**: Specialist neural networks with confidence thresholds
- **Bayesian Fusion**: Statistical combination of evidence from all layers
- **Expert Testimony Generation**: Automated justification narratives for judicial review
- **Neuro-Symbolic Guardrails**: ALP and automated reasoning to prevent AI hallucinations

## Installation

### Prerequisites
- Python 3.10+
- CUDA toolkit (for GPU acceleration)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Ganeshmandala7/advanced.git
cd advanced/fexsica

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"
```

## Architecture

### Layer 1: Photon Physics & Illumination Engine
Detects impossible lighting geometry through Lambertian and Phong reflectance analysis.

- Shadow Direction Analysis
- Specular Highlight Mapping
- Chromatic Aberration Analysis
- Gradient Lighting Field

### Layer 2: Signal Processing & Noise Physics Engine
Analyzes unique sensor noise patterns and compression signatures.

- PRNU (Photo Response Non-Uniformity) Analysis
- Noise Field Inconsistency Detection
- DCT Coefficient Analysis
- Wavelet Decomposition

### Layer 3: Geometry & Perspective Physics Engine
Verifies 3D projective geometry consistency.

- Vanishing Point Analysis
- Scale-Distance Ratio Verification
- Lens Distortion Mapping
- 3D Scene Reconstruction

### Layer 4: Compression Physics & JPEG Forensics Engine
Analyzes deterministic JPEG compression artifacts.

- Error Level Analysis (ELA)
- Double Compression Detection
- Blocking Artifact Analysis
- Quantization Table Fingerprinting

### Layer 5: Deep Learning Multimodal Verification Engine
Fuses specialist neural networks for high-precision analysis.

- MantraNet: Forgery localization
- FaceForensics++: Deepfake detection
- CNNDetect: GAN/diffusion detection
- MVSS-Net: Pixel-level segmentation

### Layer 6: Metadata & Chain of Custody Engine
Validates metadata against physical reality.

- EXIF Deep Extraction (200+ fields)
- Timestamp Physics Validation
- GPS Consistency Checking
- Provenance Tracking (C2PA)

### Layer 7: Bayesian Fusion & Verdict Engine
Converts physics findings into expert testimony.

- Bayesian Evidence Fusion
- Artifact Taxonomy Classification
- Neuro-Symbolic Guardrails
- Justification Generation

## Usage

```python
from fexsics.core import ImageProcessor, Config

# Create processor with configuration
config = Config()
processor = ImageProcessor(config)

# Load image for analysis
image = processor.load_image("test_image.jpg")

# Run full analysis pipeline
results = processor.run_full_analysis()

# Get verdict
verdict = results.get_verdict()
```

## Testing

```bash
# Run all tests
pytest

# Run specific test category
pytest -m unit
pytest -m integration

# Run with coverage
pytest --cov=fexsics --cov-report=html
```

## Documentation

- [Architecture Design](docs/ARCHITECTURE.md)
- [Layer Implementation Guides](docs/layers/)
- [API Reference](docs/API.md)

## Development

```bash
# Code formatting
black fexsics tests

# Linting
flake8 fexsics tests

# Type checking
mypy fexsics

# Run pre-commit hooks
pre-commit run --all-files
```

## Docker Support

```bash
# Build Docker image
docker build -t fexsics:latest .

# Run in Docker
docker run -v /path/to/images:/data fexsics:latest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Citation

If you use FeXsics in your research, please cite:

```bibtex
@software{fexsics2024,
  title={FeXsics: Physics-Grounded Multimodal Forensic Justification Architecture},
  author={Development Team},
  year={2024},
  url={https://github.com/Ganeshmandala7/advanced}
}
```

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

For questions, issues, or collaborations, please open an issue on GitHub or contact the development team.
"""