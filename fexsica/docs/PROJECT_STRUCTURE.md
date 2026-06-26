# FeXsics Project Structure

```
fexsica/
├── fexsics/                      # Main package
│   ├── __init__.py
│   ├── core/                     # Core components
│   │   ├── config.py             # Configuration management
│   │   ├── image_processor.py    # Central image processor
│   │   └── __init__.py
│   ├── layers/                   # 7 Physics layers
│   │   ├── photon_physics/       # Layer 1: Illumination & Photon Physics
│   │   ├── signal_processing/    # Layer 2: Sensor & Noise Physics
│   │   ├── geometry_perspective/ # Layer 3: Geometry & Perspective Physics
│   │   ├── compression_physics/  # Layer 4: JPEG Compression Physics
│   │   ├── deep_learning/        # Layer 5: Deep Learning Verification
│   │   ├── metadata_chain/       # Layer 6: Metadata & Chain of Custody
│   │   └── bayesian_fusion/      # Layer 7: Bayesian Fusion & Verdict
│   ├── utils/                    # Utility modules
│   │   ├── logger.py
│   │   ├── image_utils.py
│   │   ├── math_utils.py
│   │   └── __init__.py
│   ├── reports/                  # Report generation
│   │   ├── forensic_report.py
│   │   └── __init__.py
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   │   └── test_core.py
│   ├── integration/              # Integration tests
│   │   └── test_pipeline.py
│   └── conftest.py               # Pytest configuration
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # Architecture documentation
│   ├── API.md                    # API reference
│   └── layers/                   # Layer-specific docs
├── .github/                      # GitHub configuration
│   ├── workflows/                # CI/CD workflows
│   │   └── tests.yml
│   └── copilot-instructions.md   # Copilot instructions
├── .gitignore                    # Git ignore rules
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── Dockerfile                    # Docker containerization
├── docker-compose.yml            # Docker composition
├── setup.cfg                     # Setup configuration
└── README.md                     # Project README
```

## Layer Organization

Each of the 7 physics layers is organized in its own module under `fexsics/layers/`:

### Layer 1: Photon Physics (`photon_physics/`)
- `illumination_engine.py` - Lambertian/Phong reflectance verification
- `shadow_analyzer.py` - Shadow direction consistency
- `specular_analyzer.py` - Specular highlight analysis
- `gradient_field.py` - Global illumination mapping

### Layer 2: Signal Processing (`signal_processing/`)
- `prnu_analyzer.py` - Sensor fingerprinting
- `noise_field.py` - Noise distribution analysis
- `dct_analyzer.py` - DCT coefficient analysis
- `wavelet_analyzer.py` - Wavelet decomposition

### Layer 3: Geometry & Perspective (`geometry_perspective/`)
- `vanishing_point.py` - Vanishing point consistency
- `scale_distance.py` - Scale-distance verification
- `lens_distortion.py` - Lens distortion mapping
- `scene_reconstruction.py` - 3D scene reconstruction

### Layer 4: Compression Physics (`compression_physics/`)
- `error_level_analysis.py` - ELA forensics
- `double_compression.py` - Double compression detection
- `blocking_artifacts.py` - JPEG blocking analysis
- `quantization_fingerprint.py` - Quantization table analysis

### Layer 5: Deep Learning (`deep_learning/`)
- `mantranet.py` - Forgery localization
- `faceforensics.py` - Deepfake detection
- `cnndetect.py` - GAN/diffusion detection
- `mvss_net.py` - Pixel segmentation

### Layer 6: Metadata & Chain of Custody (`metadata_chain/`)
- `exif_validator.py` - EXIF validation
- `timestamp_validator.py` - Timestamp verification
- `gps_validator.py` - GPS consistency checking
- `provenance_tracker.py` - C2PA provenance

### Layer 7: Bayesian Fusion (`bayesian_fusion/`)
- `bayesian_fusion.py` - Bayesian evidence fusion
- `artifact_taxonomy.py` - Artifact classification
- `neuro_symbolic.py` - Logic constraint guardrails
- `justification_generator.py` - Expert testimony generation
