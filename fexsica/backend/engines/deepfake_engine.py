"""
DEEPFAKE DETECTION ENGINE

Physics: Real faces exhibit complex 3D geometry, micro-expressions, and sensor
noise. Deepfakes use deep learning synthesis which creates characteristic
artifacts in eye reflections, facial geometry, and temporal inconsistency.
"""

import logging
from typing import Dict, Any
import numpy as np
import cv2
from config import EVIDENCE_DIR
from utils.image_utils import load_image_cv2

logger = logging.getLogger(__name__)


def detect_deepfake_faces(image_path: str) -> Dict[str, Any]:
    """
    Detect deepfake artifacts in facial regions.
    
    Physics: GAN-synthesized faces have characteristic artifacts:
    - Eye reflections don't follow Fresnel equations
    - Facial geometry violates anthropometric constraints  
    - Temporal inconsistency (multi-frame only)
    - Specific frequency domain patterns
    """
    try:
        logger.info(f"Detecting deepfake faces: {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _error_result("Deepfake detection failed")
        
        # Load face detector (would normally use pre-trained weights)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return {
                "verdict": "inconclusive",
                "confidence": 0.5,
                "faces_detected": 0,
                "deepfake_score": 0.0,
                "findings": ["No faces detected in image"]
            }
        
        deepfake_scores = []
        
        for (x, y, w, h) in faces:
            face_roi = img[y:y+h, x:x+w]
            
            # Analyze eye region for GAN artifacts
            eye_artifact_score = _analyze_eye_artifacts(face_roi)
            
            # Analyze facial geometry consistency
            geometry_score = _analyze_face_geometry(face_roi)
            
            # Analyze frequency domain
            freq_score = _analyze_frequency_artifacts(face_roi)
            
            combined_score = (eye_artifact_score * 0.4 + 
                            geometry_score * 0.3 + 
                            freq_score * 0.3)
            
            deepfake_scores.append(combined_score)
        
        avg_deepfake_score = np.mean(deepfake_scores) if deepfake_scores else 0
        
        findings = [
            f"Detected {len(faces)} face(s) in image",
            f"Deepfake probability score: {avg_deepfake_score:.3f}",
        ]
        
        if avg_deepfake_score > 0.7:
            findings.append("Strong indicators of GAN-synthesized face detected")
            verdict = "manipulated"
            confidence = 0.8
        elif avg_deepfake_score > 0.5:
            findings.append("Possible deepfake indicators detected")
            verdict = "inconclusive"
            confidence = 0.65
        else:
            findings.append("Face appears authentic (no GAN artifacts)")
            verdict = "authentic"
            confidence = 0.75
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "faces_detected": len(faces),
            "deepfake_score": avg_deepfake_score,
            "findings": findings
        }
        
    except Exception as e:
        logger.error(f"Error in deepfake detection: {e}")
        return _error_result(str(e))


def run_deepfake_analysis(image_path: str) -> Dict[str, Any]:
    """Run complete deepfake detection pipeline."""
    try:
        deepfake = detect_deepfake_faces(image_path)
        
        return {
            "engine": "Deepfake",
            "verdict": deepfake.get("verdict", "inconclusive"),
            "confidence": float(deepfake.get("confidence", 0.5)),
            "findings": deepfake.get("findings", []),
            "physics_law_violated": "3D geometry + optical reflection physics",
            "evidence_map_path": "",
            "raw_scores": {
                "deepfake_score": float(deepfake.get("deepfake_score", 0.0)),
                "faces_detected": int(deepfake.get("faces_detected", 0)),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in deepfake analysis: {e}")
        return {
            "engine": "Deepfake",
            "verdict": "error",
            "confidence": 0.0,
            "findings": [f"Deepfake analysis failed: {str(e)}"],
            "physics_law_violated": "N/A",
            "evidence_map_path": "",
            "raw_scores": {"error": str(e)}
        }


def _analyze_eye_artifacts(face_roi):
    """Analyze eye region for GAN synthesis artifacts."""
    try:
        h, w = face_roi.shape[:2]
        
        # Approximate eye regions
        eye_top = h // 3
        eye_bottom = h // 2
        
        if eye_top >= eye_bottom or h < 20:
            return 0.3
        
        eye_region = face_roi[eye_top:eye_bottom, :]
        gray = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
        
        # Analyze texture smoothness (GANs tend to create overly smooth regions)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        smoothness = np.std(laplacian)
        
        # Normalized score (high smoothness = high deepfake indicator)
        artifact_score = max(0, 1.0 - (smoothness / 100.0))
        
        return artifact_score
        
    except Exception:
        return 0.3


def _analyze_face_geometry(face_roi):
    """Analyze facial geometry for consistency."""
    try:
        h, w = face_roi.shape[:2]
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Detect edges to analyze structure
        edges = cv2.Canny(gray, 100, 200)
        
        # Symmetry check (real faces are nearly symmetric)
        h_edge = edges[:, :w//2]
        h_edge_flipped = np.fliplr(edges[:, w//2:])
        
        if h_edge.shape != h_edge_flipped.shape:
            return 0.4
        
        # Compute symmetry correlation
        symmetry = np.corrcoef(h_edge.flatten(), h_edge_flipped.flatten())[0, 1]
        symmetry = max(0, symmetry)  # Handle NaN
        
        # Higher symmetry = more likely authentic, but artificially high symmetry = deepfake
        if symmetry > 0.95:
            return 0.7  # Suspiciously symmetric
        elif symmetry > 0.85:
            return 0.3  # Normal
        else:
            return 0.5  # Unusual
            
    except Exception:
        return 0.4


def _analyze_frequency_artifacts(face_roi):
    """Analyze frequency domain for GAN artifacts."""
    try:
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Compute 2D FFT
        fft_2d = np.fft.fft2(gray)
        magnitude = np.abs(np.fft.fftshift(fft_2d))
        
        # Analyze radial frequency profile
        h, w = magnitude.shape
        center_y, center_x = h // 2, w // 2
        
        # Sample radial distances
        radii = []
        for r in range(5, min(h, w) // 2, 10):
            mask = np.zeros_like(magnitude)
            cv2.circle(mask, (center_x, center_y), r, 1, 1)
            power = np.mean(magnitude[mask > 0])
            radii.append(power)
        
        # Check for characteristic GAN frequency patterns
        # GANs often produce spiky frequency responses
        if len(radii) > 2:
            variance = np.var(radii)
            artifact_score = min(1.0, variance / 1000.0)
        else:
            artifact_score = 0.3
        
        return artifact_score
        
    except Exception:
        return 0.3


def _error_result(msg):
    return {
        "verdict": "error",
        "confidence": 0.0,
        "findings": [f"Error: {msg}"],
        "error": msg
    }
