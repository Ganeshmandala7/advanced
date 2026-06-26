# FeXsics: Copilot Customization Instructions

## Project Overview
FeXsics is a physics-grounded multimodal forensic justification architecture. The project
consists of 7 specialized physics layers that analyze different aspects of image authenticity.

## Development Priorities
1. Implement physics layer algorithms
2. Integrate deep learning models
3. Develop Bayesian fusion engine
4. Generate forensic reports

## Code Standards
- Python 3.10+
- Type hints required
- Docstrings for all public methods
- Unit tests for new functions
- Black formatter (line length: 100)

## Key Modules
- `fexsics/layers/` - Physics analysis layers
- `fexsics/core/` - Core components
- `fexsics/utils/` - Utility functions
- `tests/` - Test suite

## Testing
- Run pytest for validation
- Maintain >80% code coverage
- Use pytest marks: @pytest.mark.unit, @pytest.mark.integration

## Common Tasks
- Add new layer component: Create file in appropriate `layers/` subdirectory
- Update config: Edit `fexsics/core/config.py`
- Add utility: Create file in `fexsics/utils/`
- Add test: Create in `tests/unit/` or `tests/integration/`
