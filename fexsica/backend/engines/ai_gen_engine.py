"""
AI-GENERATED IMAGE DETECTION ENGINE

Physics: Natural images come from photon capture with Poisson noise and
sensor properties. AI-generated images use neural network synthesis creating
characteristic statistical distributions, patch redundancy, and frequency artifacts.
"""

import logging
from typing import Dict, Any
import numpy as np
import cv2
from utils.image_utils import load_image_cv2, convert_bgr_to_gray

logger = logging.getLogger(__name__)


def detect_ai_generation(image_path: str) -> Dict[str, Any]:
    """
    Detect AI-generated images through multiple statistical indicators.
    
    Physics: AI models (GANs, diffusion) create images with:
    - Reduced noise variance in smooth regions
    - Characteristic patch redundancy
    - Anomalous high-frequency patterns
    - Non-Poisson noise distribution
    """
    try:
        logger.info(f"Detecting AI generation: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _error_result("AI detection failed")
        
        # Run multiple detection approaches
        noise_analysis = _analyze_noise_for_ai(img)
        patch_redundancy = _detect_patch_redundancy(img)
        texture_analysis = _analyze_texture_quality(img)
        frequency_analysis = _analyze_frequency_for_ai(img)
        
        # Combine scores
        scores = [
            noise_analysis["score"],
            patch_redundancy["score"],
            texture_analysis["score"],
            frequency_analysis["score"],
        ]
        
        ai_probability = np.mean(scores)
        
        findings = []
        findings.extend(noise_analysis["findings"])
        findings.extend(patch_redundancy["findings"])
        findings.extend(texture_analysis["findings"])
        findings.extend(frequency_analysis["findings"])
        
        if ai_probability > 0.75:
            verdict = "manipulated"
            confidence = 0.8
            findings.insert(0, f"High probability of AI generation: {ai_probability:.1%}")
        elif ai_probability > 0.55:
            verdict = "inconclusive"
            confidence = 0.65
            findings.insert(0, f"Moderate AI indicators detected: {ai_probability:.1%}")
        else:
            verdict = "authentic"
            confidence = 0.75
            findings.insert(0, f"Low probability of AI generation: {ai_probability:.1%}")
        
        return {
            "engine": "AI-Gen",
            "verdict": verdict,
            "confidence": float(confidence),
            "findings": findings,
            "physics_law_violated": "Natural sensor noise + optical physics",
            "evidence_map_path": "",
            "raw_scores": {
                "ai_probability": float(ai_probability),
                "noise_score": float(noise_analysis["score"]),
                "redundancy_score": float(patch_redundancy["score"]),
                "texture_score": float(texture_analysis["score"]),
                "frequency_score": float(frequency_analysis["score"]),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in AI generation detection: {e}")
        return {
            "engine": "AI-Gen",
            "verdict": "error",
            "confidence": 0.0,
            "findings": [f"AI detection failed: {str(e)}"],
            "physics_law_violated": "N/A",
            "evidence_map_path": "",
            "raw_scores": {"error": str(e)}
        }


def _analyze_noise_for_ai(img):
    """Analyze noise characteristics for AI indicators."""
    try:
        gray = convert_bgr_to_gray(img).astype(np.float32)
        
        # Extract noise via Gaussian blur subtraction
        blurred = cv2.GaussianBlur(gray, (15, 15), 1.0)
        noise = gray - blurred
        
        # Analyze noise distribution
        noise_std = np.std(noise)
        noise_kurtosis = np.mean((noise - np.mean(noise))**4) / (noise_std**4 + 1e-6)
        
        # Real camera noise: kurtosis ~3 (Gaussian)
        # AI images: often lower kurtosis (too clean)
        kurtosis_deviation = abs(noise_kurtosis - 3.0) / 5.0
        
        # AI-generated often have too-low noise
        ai_score = max(0, 1.0 - (noise_std / 50.0)) * 0.5 + kurtosis_deviation * 0.5
        
        findings = [
            f"Noise distribution kurtosis: {noise_kurtosis:.2f} (real camera ~3)",
            "Unusually clean noise distribution" if ai_score > 0.6 else "Noise consistent with camera"
        ]
        
        return {"score": ai_score, "findings": findings}
        
    except Exception:
        return {"score": 0.4, "findings": ["Noise analysis inconclusive"]}


def _detect_patch_redundancy(img):
    """Detect repeated patches (common in AI generation)."""
    try:
        gray = convert_bgr_to_gray(img).astype(np.uint8)
        
        # Extract patches
        patch_size = 32
        h, w = gray.shape
        patches = []
        
        for i in range(0, h - patch_size, patch_size):
            for j in range(0, w - patch_size, patch_size):
                patch = gray[i:i+patch_size, j:j+patch_size]
                # Convert to hash for comparison
                patch_hash = hash(patch.tobytes())
                patches.append(patch_hash)
        
        # Check for duplicate patches
        if len(patches) > 1:
            unique_patches = len(set(patches))
            redundancy = 1.0 - (unique_patches / len(patches))
        else:
            redundancy = 0.0
        
        findings = [
            f"Patch redundancy: {redundancy:.1%}",
            "High patch redundancy indicates repetitive patterns" if redundancy > 0.3 else "Diverse patch content"
        ]
        
        return {"score": redundancy, "findings": findings}
        
    except Exception:
        return {"score": 0.2, "findings": ["Patch analysis inconclusive"]}


def _analyze_texture_quality(img):
    """Analyze texture coherence and quality."""
    try:
        gray = convert_bgr_to_gray(img).astype(np.float32)
        
        # Compute local standard deviation (texture strength)
        kernel_size = 31
        mean = cv2.blur(gray, (kernel_size, kernel_size))
        sqr_mean = cv2.blur(gray**2, (kernel_size, kernel_size))
        variance = sqr_mean - mean**2
        texture_map = np.sqrt(np.maximum(variance, 0))
        
        # AI images often have regions with suspiciously uniform texture
        # Count low-variance regions
        low_variance_ratio = np.sum(texture_map < np.percentile(texture_map, 25)) / texture_map.size
        
        # If too many regions have very low variance = AI
        ai_score = max(0, low_variance_ratio - 0.2) * 1.5
        
        findings = [
            f"Uniform texture coverage: {low_variance_ratio:.1%}",
            "Excessive texture uniformity detected" if ai_score > 0.6 else "Texture variation typical of real images"
        ]
        
        return {"score": min(1.0, ai_score), "findings": findings}
        
    except Exception:
        return {"score": 0.3, "findings": ["Texture analysis inconclusive"]}


def _analyze_frequency_for_ai(img):
    """Analyze frequency domain for AI generation artifacts."""
    try:
        gray = convert_bgr_to_gray(img).astype(np.float32)
        
        # Compute FFT
        fft_2d = np.fft.fft2(gray)
        magnitude = np.abs(np.fft.fftshift(fft_2d))
        log_magnitude = np.log(magnitude + 1)
        
        # Analyze spectrum: real images have 1/f spectrum (smooth)
        # AI images show characteristic peaks/valleys
        h, w = log_magnitude.shape
        center_y, center_x = h // 2, w // 2
        
        # Sample radial frequency
        power_by_radius = []
        for r in range(1, min(h, w) // 2, 5):
            mask = np.zeros_like(log_magnitude)
            cv2.circle(mask, (center_x, center_y), r, 1, 1)
            power = np.mean(log_magnitude[mask > 0])
            power_by_radius.append(power)
        
        # Fit slope (should be negative for 1/f)
        if len(power_by_radius) > 2:
            x = np.arange(len(power_by_radius))
            y = np.array(power_by_radius)
            slope = np.polyfit(x, y, 1)[0]
            
            # 1/f spectrum: slope should be ~-0.5
            slope_deviation = abs(slope - (-0.5)) / 0.5
            ai_score = max(0, min(1.0, slope_deviation * 0.5))
        else:
            ai_score = 0.3
        
        findings = [
            f"Frequency spectrum slope deviation: {slope_deviation:.2f}" if len(power_by_radius) > 2 else "Insufficient frequency data",
            "Spectrum matches natural 1/f pattern" if ai_score < 0.3 else "Unusual frequency characteristics"
        ]
        
        return {"score": ai_score, "findings": findings}
        
    except Exception:
        return {"score": 0.2, "findings": ["Frequency analysis inconclusive"]}


def _error_result(msg):
    return {
        "engine": "AI-Gen",
        "verdict": "error",
        "confidence": 0.0,
        "findings": [f"Error: {msg}"],
        "physics_law_violated": "N/A",
        "evidence_map_path": "",
        "raw_scores": {"error": msg}
    }
