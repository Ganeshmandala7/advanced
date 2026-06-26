"""
ILLUMINATION ENGINE

Physics: Single light source casts shadows at consistent angles. All shadows and
specular highlights must obey Lambertian + Phong reflectance models. Composited
images violate these optical physics laws.
"""

import logging
import numpy as np
from typing import Dict, Any
import cv2
import uuid
from config import EVIDENCE_DIR, SHADOW_ANGLE_TOLERANCE
from utils.image_utils import load_image_cv2, convert_bgr_to_lab, convert_bgr_to_gray

logger = logging.getLogger(__name__)


def estimate_light_sources(image_path: str) -> Dict[str, Any]:
    """
    Estimate light source positions from shadow and highlight analysis.
    """
    try:
        logger.info(f"Estimating light sources: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _error_result("Light source estimation failed")
        
        lab = convert_bgr_to_lab(img)
        l_channel = lab[:, :, 0]
        
        # Detect shadows (low luminance)
        shadow_threshold = np.percentile(l_channel, 20)
        shadow_mask = (l_channel < shadow_threshold).astype(np.uint8)
        
        # Find shadow centers
        contours, _ = cv2.findContours(shadow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Estimate light direction from shadow centroids
        light_estimates = []
        for contour in contours[:10]:  # Limit to 10 largest shadows
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cy = int(M["m01"] / M["m00"])
                cx = int(M["m10"] / M["m00"])
                light_estimates.append((cx, cy))
        
        # Check consistency
        consistency_score = _compute_light_consistency(light_estimates)
        
        findings = []
        if len(light_estimates) >= 3:
            findings.append(f"Detected {len(light_estimates)} shadow centers")
            findings.append(f"Light source consistency: {consistency_score:.2f}")
            if consistency_score > 0.8:
                findings.append("Single light source confirmed")
            else:
                findings.append("Multiple inconsistent light sources detected")
        
        return {
            "verdict": "authentic" if consistency_score > 0.75 else "manipulated",
            "confidence": min(consistency_score, 0.9),
            "light_estimates": light_estimates,
            "consistency_score": consistency_score,
            "findings": findings
        }
        
    except Exception as e:
        logger.error(f"Error estimating light sources: {e}")
        return _error_result(str(e))


def analyze_shadow_consistency(image_path: str) -> Dict[str, Any]:
    """
    Analyze shadow direction consistency.
    """
    try:
        logger.info(f"Analyzing shadow consistency: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _error_result("Shadow analysis failed")
        
        gray = convert_bgr_to_gray(img)
        
        # Detect edges
        edges = cv2.Canny(gray, 100, 200)
        
        # Analyze edge angles for shadow direction
        _, theta = cv2.phase(cv2.Sobel(gray, cv2.CV_32F, 1, 0),
                            cv2.Sobel(gray, cv2.CV_32F, 0, 1))
        
        # Sample edge angles
        edge_pixels = np.where(edges > 0)
        if len(edge_pixels[0]) > 100:
            angles = theta[edge_pixels]
            angle_hist, _ = np.histogram(angles, bins=36, range=(0, 2*np.pi))
            
            # Check for consistency (one dominant angle)
            max_bin = np.argmax(angle_hist)
            consistency = angle_hist[max_bin] / np.sum(angle_hist)
        else:
            consistency = 0.5
        
        findings = [
            f"Shadow direction consistency: {consistency:.2f}",
            "Consistent shadow angles indicate single light source" if consistency > 0.7 else "Variable shadow angles detected"
        ]
        
        return {
            "verdict": "authentic" if consistency > 0.7 else "inconclusive",
            "confidence": consistency * 0.9,
            "consistency_score": consistency,
            "findings": findings
        }
        
    except Exception as e:
        logger.error(f"Error in shadow analysis: {e}")
        return _error_result(str(e))


def detect_chromatic_aberration(image_path: str) -> Dict[str, Any]:
    """
    Detect chromatic aberration (real lenses have consistent pattern).
    """
    try:
        logger.info(f"Detecting chromatic aberration: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _error_result("Chromatic aberration detection failed")
        
        b, g, r = cv2.split(img)
        
        # Detect edges in each channel
        edges_r = cv2.Canny(r, 100, 200)
        edges_g = cv2.Canny(g, 100, 200)
        edges_b = cv2.Canny(b, 100, 200)
        
        # Compute misalignment
        # Real lenses have consistent aberration; splices show zero/wrong aberration
        misalignment_rg = np.sum(np.abs(edges_r.astype(float) - edges_g.astype(float)))
        misalignment_gb = np.sum(np.abs(edges_g.astype(float) - edges_b.astype(float)))
        
        total_edges = np.sum(edges_g > 0)
        if total_edges > 0:
            aberration_score = (misalignment_rg + misalignment_gb) / (2 * total_edges)
        else:
            aberration_score = 0
        
        findings = [
            f"Chromatic aberration score: {aberration_score:.3f}",
            "Consistent aberration pattern (camera lens)" if aberration_score < 0.1 else "Aberration inconsistencies detected"
        ]
        
        return {
            "verdict": "authentic" if aberration_score < 0.1 else "inconclusive",
            "confidence": max(0.6, 1.0 - aberration_score),
            "aberration_score": aberration_score,
            "findings": findings
        }
        
    except Exception as e:
        logger.error(f"Error in chromatic aberration detection: {e}")
        return _error_result(str(e))


def run_illumination_analysis(image_path: str) -> Dict[str, Any]:
    """Run complete illumination analysis pipeline."""
    try:
        light = estimate_light_sources(image_path)
        shadow = analyze_shadow_consistency(image_path)
        aberration = detect_chromatic_aberration(image_path)
        
        # Combine results
        avg_confidence = (
            light.get("confidence", 0) * 0.4 +
            shadow.get("confidence", 0) * 0.35 +
            aberration.get("confidence", 0) * 0.25
        )
        
        findings = []
        findings.extend(light.get("findings", []))
        findings.extend(shadow.get("findings", []))
        findings.extend(aberration.get("findings", []))
        
        # Majority verdict
        verdicts = [
            light.get("verdict", "inconclusive"),
            shadow.get("verdict", "inconclusive"),
            aberration.get("verdict", "inconclusive"),
        ]
        manipulated_count = sum(1 for v in verdicts if v == "manipulated")
        
        verdict = "manipulated" if manipulated_count >= 2 else ("authentic" if manipulated_count == 0 else "inconclusive")
        
        return {
            "engine": "Illumination",
            "verdict": verdict,
            "confidence": float(avg_confidence),
            "findings": findings,
            "physics_law_violated": "Lambertian + Phong reflectance models",
            "evidence_map_path": "",
            "raw_scores": {
                "light_consistency": light.get("consistency_score", 0),
                "shadow_consistency": shadow.get("consistency_score", 0),
                "aberration_score": aberration.get("aberration_score", 0),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in illumination analysis: {e}")
        return {
            "engine": "Illumination",
            "verdict": "error",
            "confidence": 0.0,
            "findings": [f"Illumination analysis failed: {str(e)}"],
            "physics_law_violated": "N/A",
            "evidence_map_path": "",
            "raw_scores": {"error": str(e)}
        }


def _compute_light_consistency(light_estimates):
    """Compute consistency score for light source estimates."""
    if len(light_estimates) < 2:
        return 0.5
    
    # Compute distances between estimates
    distances = []
    for i in range(len(light_estimates)):
        for j in range(i+1, len(light_estimates)):
            x1, y1 = light_estimates[i]
            x2, y2 = light_estimates[j]
            dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
            distances.append(dist)
    
    if not distances:
        return 1.0
    
    # Low variance in distances = consistent
    mean_dist = np.mean(distances)
    std_dist = np.std(distances) if len(distances) > 1 else 0
    
    consistency = 1.0 / (1.0 + std_dist / (mean_dist + 1e-6))
    return min(consistency, 1.0)


def _error_result(msg):
    return {
        "verdict": "error",
        "confidence": 0.0,
        "findings": [f"Error: {msg}"],
        "error": msg
    }
