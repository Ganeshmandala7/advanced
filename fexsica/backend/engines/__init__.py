"""
ENGINES PACKAGE - ALL FORENSIC ANALYSIS ENGINES

7 physics-based forensic engines + Bayesian fusion:
1. ELA Engine - JPEG compression forensics
2. Metadata Engine - Camera metadata and chain of custody
3. Noise Engine - Sensor fingerprint and noise physics
4. Illumination Engine - Light source and shadow analysis
5. Geometry Engine - 3D perspective and vanishing points
6. Deepfake Engine - GAN-synthesized face detection
7. AI-Gen Engine - AI-generated image detection
8. Fusion Engine - Bayesian combination of all engines
"""

__all__ = [
    "ela_engine", "metadata_engine", "noise_engine", "illumination_engine",
    "geometry_engine", "deepfake_engine", "ai_gen_engine", "fusion_engine"
]
