# FeXsics Quick Start Guide

## Installation & Setup

### 1. Navigate to Project
```bash
cd /workspaces/advanced/fexsica
```

### 2. Create Virtual Environment
```bash
# Python 3.10+
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import fexsics; print('✓ FeXsics installed successfully!')"
```

## Usage Examples

### Basic Image Analysis
```python
from fexsics.core import ImageProcessor, Config

# Create processor
config = Config()
processor = ImageProcessor(config)

# Load and analyze image
processor.load_image("path/to/image.jpg")
results = processor.run_full_analysis()

# Get results
print(results)
```

### Command Line Usage
```bash
# Analyze image and generate report
python -m fexsics path/to/image.jpg --output report.html --format html

# With custom config
python -m fexsics path/to/image.jpg --config config.yaml
```

### Generate Forensic Report
```python
from fexsics.reports import ForensicReport

# Create and populate report
report = ForensicReport("Image Analysis Report")
report.add_section("Analysis Results", results)

# Export in different formats
html_report = report.generate_html_report()
json_report = report.generate_json_report()

# Save to file
with open("report.html", "w") as f:
    f.write(html_report)
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run specific test category
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only

# Run with coverage report
pytest --cov=fexsics --cov-report=html
```

## Project Structure Overview

```
fexsics/
├── core/              # Core components
├── layers/            # 7 Physics analysis layers
│   ├── photon_physics/          # Layer 1: Illumination
│   ├── signal_processing/       # Layer 2: Sensor noise
│   ├── geometry_perspective/    # Layer 3: 3D geometry
│   ├── compression_physics/     # Layer 4: JPEG analysis
│   ├── deep_learning/           # Layer 5: Neural networks
│   ├── metadata_chain/          # Layer 6: EXIF & provenance
│   └── bayesian_fusion/         # Layer 7: Verdict fusion
├── utils/             # Helper utilities
└── reports/           # Report generation
```

## Development Workflow

### Code Style
```bash
# Format code with Black
black fexsics tests

# Run linter
flake8 fexsics tests

# Type checking
mypy fexsics
```

### Adding New Layer Component
1. Create module in appropriate `layers/` subdirectory
2. Implement analysis methods
3. Return standardized result format
4. Add unit tests

### Configuration
```python
from fexsics.core import Config

# Load from file
config = Config.from_file("config.yaml")

# Or create with defaults
config = Config(debug_mode=True, log_level="DEBUG")

# Save configuration
config.to_file("my_config.yaml")
```

## Docker Support

### Build & Run
```bash
# Build image
docker build -t fexsics:latest .

# Run container
docker run -v /path/to/images:/data fexsics:latest

# Or use docker-compose
docker-compose up -d fexsics
```

## Documentation

- **README.md** - Project overview and features
- **docs/ARCHITECTURE.md** - Detailed architecture explanation
- **docs/PROJECT_STRUCTURE.md** - Module organization
- **.github/copilot-instructions.md** - Development guidelines

## Troubleshooting

### Import Errors
```bash
# Reinstall in development mode
pip install -e .
```

### Missing Dependencies
```bash
# Reinstall all requirements
pip install --no-cache-dir -r requirements.txt
```

### CUDA/GPU Issues
```bash
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# Use CPU fallback
export TORCH_DEVICE=cpu
```

## Next Steps

1. ✅ Review [ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. ✅ Run test suite to verify setup
3. ✅ Implement physics layer algorithms
4. ✅ Integrate deep learning models
5. ✅ Configure Bayesian fusion weights
6. ✅ Generate forensic reports

## Support

- Check [GitHub Issues](https://github.com/Ganeshmandala7/advanced/issues)
- Review documentation in `docs/`
- Check copilot instructions in `.github/`

---
**FeXsics** - Physics-Grounded Forensic Justification Architecture
