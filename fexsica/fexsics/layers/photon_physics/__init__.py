"""Layer 1: Photon Physics & Illumination Consistency Engine"""

from .illumination_engine import IlluminationEngine
from .shadow_analyzer import ShadowAnalyzer
from .specular_analyzer import SpecularAnalyzer
from .gradient_field import GradientLightingField

__all__ = [
    "IlluminationEngine",
    "ShadowAnalyzer", 
    "SpecularAnalyzer",
    "GradientLightingField"
]
