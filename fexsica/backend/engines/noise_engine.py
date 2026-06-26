"""
NOISE PHYSICS ENGINE

Physics: Every sensor introduces unique statistical noise. PRNU (Photo Response 
Non-Uniformity) is the sensor's fingerprint. Edited regions have different noise 
signatures. Noise variance must be uniform across single-source image.
"""

import logging
import numpy as np
from typing import Dict, Any
import cv2
import uuid
from scipy import fft
from config import EVIDENCE_DIR, NOISE_STD_MULTIPLIER
from utils.image_utils import load_image_cv2, convert_bgr_to_gray, save_heatmap

logger = logging.getLogger(__name__)


def analyze_noise_field(image_path: str) -> Dict[str, Any]:
    """
    Analyze noise distribution to detect regions from different sources.
    
    Physics: Noise variance should be uniform if image is single-source. 
    Patches with variance > mean+2σ or < mean-2σ indicate manipulation.
    """
    try:
        logger.info(f"Analyzing noise field: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _create_error_result("Noise", "Failed to load image")
        
        gray = convert_bgr_to_gray(img).astype(np.float32)
        
        # Apply Gaussian blur to extract signal
        signal = cv2.GaussianBlur(gray, (15, 15), 1.0)
        
        # Extract noise
        noise = gray - signal
        
        # Analyze variance in 64x64 patches
        patch_size = 64
        h, w = gray.shape
        variances = []
        
        for i in range(0, h - patch_size, patch_size):
            for j in range(0, w - patch_size, patch_size):
                patch_noise = noise[i:i+patch_size, j:j+patch_size]
                var = np.var(patch_noise)
                variances.append(var)
        
        variances = np.array(variances)
        global_mean = np.mean(variances)
        global_std = np.std(variances)
        
        # Detect anomalies
        threshold_high = global_mean + NOISE_STD_MULTIPLIER * global_std
        threshold_low = global_mean - NOISE_STD_MULTIPLIER * global_std
        
        anomalies = np.sum((variances > threshold_high) | (variances < threshold_low))
        anomaly_percentage = (anomalies / len(variances) * 100) if len(variances) > 0 else 0
        
        # Build variance map for visualization
        num_blocks_h = (h - patch_size) // patch_size + 1
        num_blocks_w = (w - patch_size) // patch_size + 1
        variance_map = np.reshape(variances[:num_blocks_h * num_blocks_w], 
                                  (num_blocks_h, num_blocks_w))
        
        # Save heatmap
        heatmap_path = str(EVIDENCE_DIR / f"noise_variance_{uuid.uuid4()}.png")
        save_heatmap(variance_map, heatmap_path, cmap="coolwarm")
        
        # Confidence scoring
        uniformity_score = 1.0 - (anomaly_percentage / 100.0)
        if anomaly_percentage < 10:
            confidence = 0.8
            verdict = "authentic"
        elif anomaly_percentage < 30:
            confidence = 0.65
            verdict = "inconclusive"
        else:
            confidence = 0.75
            verdict = "manipulated"
        
        findings = []
        if anomaly_percentage > 15:
            findings.append(f"Detected {anomaly_percentage:.1f}% of patches with anomalous noise variance.")
            findings.append("Noise statistics violate single-source image property.")
        else:
            findings.append("Noise variance appears uniform across image (single source).")
        
        logger.info(f"Noise analysis: {anomaly_percentage:.1f}% anomalies")
        
        return {
            "engine": "Noise",
            "verdict": verdict,
            "confidence": float(confidence),
            "findings": findings,
            "physics_law_violated": "Uniform noise distribution (single sensor)",
            "evidence_map_path": heatmap_path,
            "raw_scores": {
                "anomaly_percentage": float(anomaly_percentage),
                "uniformity_score": float(uniformity_score),
                "global_noise_mean": float(global_mean),
                "global_noise_std": float(global_std),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in noise analysis: {e}")
        return _create_error_result("Noise", str(e))


def estimate_prnu(image_path: str) -> Dict[str, Any]:
    """
    Estimate Photo Response Non-Uniformity pattern (camera fingerprint).
    
    Physics: Each sensor has unique PRNU pattern. Extracting PRNU from different
    regions and checking correlation reveals if all regions came from same sensor.
    """
    try:
        logger.info(f"Estimating PRNU: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _create_error_result("PRNU", "Failed to load image")
        
        gray = convert_bgr_to_gray(img).astype(np.float32)
        
        # Apply Wiener filter to extract PRNU
        # Simplified: use bilateral filter to smooth signal while preserving PRNU
        signal = cv2.bilateralFilter((gray * 255).astype(np.uint8), 9, 75, 75).astype(np.float32)
        
        # PRNU = noise residual
        prnu = gray - (signal / 255.0)
        
        # Divide image into quadrants and check correlation
        h, w = prnu.shape
        q1 = prnu[:h//2, :w//2].flatten()
        q2 = prnu[:h//2, w//2:].flatten()
        q3 = prnu[h//2:, :w//2].flatten()
        q4 = prnu[h//2:, w//2:].flatten()
        
        # Compute correlations
        corr_12 = np.corrcoef(q1, q2)[0, 1]
        corr_34 = np.corrcoef(q3, q4)[0, 1]
        corr_13 = np.corrcoef(q1, q3)[0, 1]
        
        correlations = [corr_12, corr_34, corr_13]
        mean_correlation = np.mean(correlations)
        
        # High correlation = same source
        is_single_source = mean_correlation > 0.5
        confidence = min(0.9, 0.5 + abs(mean_correlation) * 0.4)
        
        findings = []
        if is_single_source:
            findings.append(f"PRNU correlation: {mean_correlation:.3f} (single sensor)")
            findings.append("Sensor fingerprint pattern is consistent across image.")
        else:
            findings.append(f"PRNU correlation: {mean_correlation:.3f} (multiple sources)")
            findings.append("Sensor fingerprint inconsistency detected across regions.")
        
        return {
            "engine": "PRNU",
            "verdict": "authentic" if is_single_source else "manipulated",
            "confidence": float(confidence),
            "findings": findings,
            "physics_law_violated": "Consistent sensor fingerprint (PRNU)",
            "evidence_map_path": "",
            "raw_scores": {
                "is_single_source": bool(is_single_source),
                "mean_correlation": float(mean_correlation),
                "correlations": [float(c) for c in correlations],
            }
        }
        
    except Exception as e:
        logger.error(f"Error in PRNU estimation: {e}")
        return _create_error_result("PRNU", str(e))


def analyze_frequency_domain(image_path: str) -> Dict[str, Any]:
    """
    Analyze frequency domain for manipulation indicators.
    
    Physics: Real photos have 1/f power spectrum. AI-generated images have
    different spectrum. Manipulated regions show anomalous frequency patterns.
    """
    try:
        logger.info(f"Analyzing frequency domain: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _create_error_result("FFT", "Failed to load image")
        
        gray = convert_bgr_to_gray(img).astype(np.float32)
        
        # Compute 2D FFT
        fft_2d = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft_2d)
        magnitude = np.abs(fft_shift)
        
        # Compute power spectrum
        power = np.log(magnitude + 1)
        
        # Analyze power spectrum characteristics
        # 1/f spectrum: log(power) should decrease linearly with log(frequency)
        h, w = power.shape
        center_y, center_x = h // 2, w // 2
        
        # Sample radial profile
        radii = []
        power_samples = []
        for r in range(10, min(h, w) // 2, 10):
            mask = np.zeros_like(power)
            cv2.circle(mask, (center_x, center_y), r, 1, 1)
            power_samples.append(np.mean(power[mask > 0]))
            radii.append(r)
        
        # Check if power decreases (1/f characteristic)
        if len(power_samples) > 1:
            slope = (power_samples[-1] - power_samples[0]) / len(power_samples)
            is_1f_spectrum = slope < -0.05  # Should decrease with frequency
        else:
            is_1f_spectrum = True
        
        findings = []
        if not is_1f_spectrum:
            findings.append("Frequency spectrum deviates from natural 1/f pattern.")
            findings.append("May indicate AI generation or significant processing.")
        else:
            findings.append("Frequency spectrum consistent with natural image (1/f).")
        
        return {
            "engine": "FFT",
            "verdict": "authentic" if is_1f_spectrum else "inconclusive",
            "confidence": 0.65,
            "findings": findings,
            "physics_law_violated": "1/f power spectrum (natural images)",
            "evidence_map_path": "",
            "raw_scores": {
                "is_1f_spectrum": bool(is_1f_spectrum),
                "spectrum_slope": float(slope) if len(power_samples) > 1 else 0.0,
            }
        }
        
    except Exception as e:
        logger.error(f"Error in FFT analysis: {e}")
        return _create_error_result("FFT", str(e))


def run_noise_analysis(image_path: str) -> Dict[str, Any]:
    """Run complete noise physics analysis pipeline."""
    try:
        noise_field = analyze_noise_field(image_path)
        prnu = estimate_prnu(image_path)
        fft = analyze_frequency_domain(image_path)
        
        # Combine results
        avg_confidence = (
            noise_field.get("confidence", 0) * 0.4 +
            prnu.get("confidence", 0) * 0.3 +
            fft.get("confidence", 0) * 0.3
        )
        
        findings = []
        findings.extend(noise_field.get("findings", []))
        findings.extend(prnu.get("findings", []))
        findings.extend(fft.get("findings", []))
        
        # Majority verdict
        verdicts = [
            noise_field.get("verdict", "inconclusive"),
            prnu.get("verdict", "inconclusive"),
            fft.get("verdict", "inconclusive"),
        ]
        manipulated_count = sum(1 for v in verdicts if v == "manipulated")
        
        if manipulated_count >= 2:
            verdict = "manipulated"
        elif manipulated_count == 0:
            verdict = "authentic"
        else:
            verdict = "inconclusive"
        
        return {
            "engine": "Noise",
            "verdict": verdict,
            "confidence": float(avg_confidence),
            "findings": findings,
            "physics_law_violated": "Sensor noise physics (PRNU, 1/f spectrum)",
            "evidence_map_path": noise_field.get("evidence_map_path", ""),
            "raw_scores": {
                "noise_field_anomaly": noise_field.get("raw_scores", {}).get("anomaly_percentage", 0),
                "prnu_correlation": prnu.get("raw_scores", {}).get("mean_correlation", 0),
                "fft_1f_spectrum": fft.get("raw_scores", {}).get("is_1f_spectrum", False),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in noise analysis pipeline: {e}")
        return _create_error_result("Noise", str(e))


def _create_error_result(engine_name: str, error_msg: str) -> Dict[str, Any]:
    """Create standardized error result."""
    return {
        "engine": engine_name,
        "verdict": "error",
        "confidence": 0.0,
        "findings": [f"Analysis failed: {error_msg}"],
        "physics_law_violated": "N/A",
        "evidence_map_path": "",
        "raw_scores": {"error": error_msg}
    }
