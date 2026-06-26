"""
ERROR LEVEL ANALYSIS ENGINE

Physics principle: JPEG compression is a deterministic DCT-based process. Re-saving at 
a known quality level reveals regions with different compression histories — these are 
edited regions. Every compression applies specific quantization patterns; resaving 
unmolested regions produces minimal error, while previously-compressed or edited regions 
produce higher error.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import cv2
from PIL import Image
import tempfile
from scipy import fft
import uuid

from config import EVIDENCE_DIR, JPEG_QUALITY_LEVELS, DEFAULT_ELA_QUALITY, ELA_ANOMALY_THRESHOLD
from utils.image_utils import save_heatmap, normalize_image, load_image_cv2

logger = logging.getLogger(__name__)


def run_ela(image_path: str, quality: int = DEFAULT_ELA_QUALITY) -> Dict[str, Any]:
    """
    Execute Error Level Analysis to detect JPEG compression inconsistencies.
    
    Physics: When a JPEG is re-compressed at a known quality, regions that have been
    previously modified (already compressed differently) will show higher error levels.
    This violates the deterministic compression process for unmodified regions.
    
    Args:
        image_path: Path to image file
        quality: JPEG quality level to re-compress at (default 90)
        
    Returns:
        Dictionary with ELA analysis results
    """
    try:
        logger.info(f"Starting ELA analysis on {image_path} with quality {quality}")
        
        # Load original image
        img = load_image_cv2(image_path)
        if img is None:
            return {
                "engine": "ELA",
                "verdict": "error",
                "confidence": 0.0,
                "findings": ["Failed to load image"],
                "physics_law_violated": "N/A",
                "evidence_map_path": "",
                "raw_scores": {"error": str("Image load failed")}
            }
        
        # Save original as JPEG temporarily to get reference
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_orig:
            cv2.imwrite(tmp_orig.name, img)
            original_data = np.fromfile(tmp_orig.name, dtype=np.uint8)
        
        # Re-save at target quality
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_resave:
            pil_img = Image.open(image_path)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            pil_img.save(tmp_resave.name, "JPEG", quality=quality, optimize=False)
            resaved_data = np.fromfile(tmp_resave.name, dtype=np.uint8)
        
        # Load resaved image
        resaved_img = load_image_cv2(tmp_resave.name)
        
        # Compute absolute difference
        diff = cv2.absdiff(img.astype(np.float32), resaved_img.astype(np.float32))
        diff_amplified = np.clip(diff * 10, 0, 255).astype(np.uint8)
        
        # Convert to grayscale for analysis
        if len(diff_amplified.shape) == 3:
            diff_gray = cv2.cvtColor(diff_amplified, cv2.COLOR_BGR2GRAY)
        else:
            diff_gray = diff_amplified
        
        # Analyze ELA at 8x8 block level (JPEG block size)
        block_size = 8
        height, width = diff_gray.shape
        
        # Pad to multiple of block_size
        padded_height = ((height + block_size - 1) // block_size) * block_size
        padded_width = ((width + block_size - 1) // block_size) * block_size
        diff_padded = np.pad(diff_gray, ((0, padded_height - height), (0, padded_width - width)))
        
        # Compute mean error per block
        num_blocks_h = padded_height // block_size
        num_blocks_w = padded_width // block_size
        block_means = np.zeros((num_blocks_h, num_blocks_w))
        
        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                block = diff_padded[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size]
                block_means[i, j] = np.mean(block)
        
        # Calculate statistics
        global_mean = np.mean(block_means)
        global_std = np.std(block_means)
        
        # Identify anomalous blocks (high error = likely manipulation)
        threshold = global_mean + ELA_ANOMALY_THRESHOLD * global_std
        anomaly_mask = (block_means > threshold).astype(np.uint8) * 255
        
        # Expand mask back to image size
        anomaly_mask_full = np.repeat(np.repeat(anomaly_mask, block_size, axis=0), 
                                      block_size, axis=1)[:height, :width]
        
        # Calculate percentage of anomalous regions
        anomaly_percentage = np.sum(anomaly_mask) / (num_blocks_h * num_blocks_w) * 100
        
        # Confidence based on anomaly percentage and distribution
        if anomaly_percentage == 0:
            confidence = 0.95  # Very confident image is authentic
            verdict = "authentic"
        elif anomaly_percentage < 5:
            confidence = 0.7
            verdict = "authentic"
        elif anomaly_percentage < 15:
            confidence = 0.6
            verdict = "inconclusive"
        elif anomaly_percentage < 40:
            confidence = 0.75
            verdict = "manipulated"
        else:
            confidence = 0.85
            verdict = "manipulated"
        
        # Save evidence maps
        ela_map_path = str(EVIDENCE_DIR / f"ela_map_{uuid.uuid4()}.png")
        anomaly_mask_path = str(EVIDENCE_DIR / f"ela_mask_{uuid.uuid4()}.png")
        heatmap_path = str(EVIDENCE_DIR / f"ela_heatmap_{uuid.uuid4()}.png")
        
        cv2.imwrite(ela_map_path, diff_amplified)
        cv2.imwrite(anomaly_mask_path, anomaly_mask_full)
        save_heatmap(block_means, heatmap_path, cmap="hot")
        
        # Generate findings
        findings = []
        if verdict == "manipulated":
            findings.append(
                f"Detected {anomaly_percentage:.1f}% of 8x8 JPEG blocks with anomalous error levels."
            )
            findings.append(
                f"When re-compressed at quality {quality}, unmodified regions should have minimal "
                f"error. Detected error levels {ELA_ANOMALY_THRESHOLD}σ above baseline in "
                f"{anomaly_percentage:.1f}% of blocks, indicating previous compression or modification."
            )
            if anomaly_percentage > 40:
                findings.append("Anomalies are widespread and concentrated, suggesting intentional splicing.")
        elif verdict == "inconclusive":
            findings.append(f"Moderate anomalies detected: {anomaly_percentage:.1f}% of blocks.")
            findings.append("Insufficient evidence to determine authenticity. Further analysis needed.")
        else:
            findings.append(f"ELA analysis shows minimal anomalies ({anomaly_percentage:.1f}% of blocks).")
            findings.append("Compression history appears consistent with single-save JPEG.")
        
        # Cleanup temp files
        Path(tmp_orig.name).unlink()
        Path(tmp_resave.name).unlink()
        
        logger.info(f"ELA analysis complete: {verdict} (confidence: {confidence:.2f})")
        
        return {
            "engine": "ELA",
            "verdict": verdict,
            "confidence": float(confidence),
            "findings": findings,
            "physics_law_violated": "Deterministic JPEG compression process",
            "evidence_map_path": ela_map_path,
            "raw_scores": {
                "anomaly_percentage": float(anomaly_percentage),
                "global_mean_error": float(global_mean),
                "global_std_error": float(global_std),
                "anomaly_threshold": float(threshold),
                "num_anomalous_blocks": int(np.sum(anomaly_mask)),
                "total_blocks": int(num_blocks_h * num_blocks_w),
                "anomaly_mask_path": anomaly_mask_path,
                "heatmap_path": heatmap_path,
            }
        }
        
    except Exception as e:
        logger.error(f"Error in ELA analysis: {e}", exc_info=True)
        return {
            "engine": "ELA",
            "verdict": "error",
            "confidence": 0.0,
            "findings": [f"Analysis failed: {str(e)}"],
            "physics_law_violated": "Deterministic JPEG compression",
            "evidence_map_path": "",
            "raw_scores": {"error": str(e)}
        }


def run_dct_analysis(image_path: str) -> Dict[str, Any]:
    """
    Analyze DCT coefficients to detect double JPEG compression.
    
    Physics: JPEG uses Discrete Cosine Transform (DCT) on 8x8 blocks. Double-compressed
    images show characteristic periodic peaks in the DCT coefficient histogram due to
    quantization artifacts. This violates the expected coefficient distribution for
    single-compressed images.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary with DCT analysis results
    """
    try:
        logger.info(f"Starting DCT analysis on {image_path}")
        
        # Load image and convert to YCbCr (JPEG working colorspace)
        img = load_image_cv2(image_path)
        if img is None:
            return _create_error_result("DCT", "Failed to load image")
        
        pil_img = Image.open(image_path)
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y_channel = img_ycrcb[:, :, 0].astype(np.float32)
        
        # Apply 8x8 DCT and collect coefficients
        block_size = 8
        height, width = y_channel.shape
        dct_coefficients = []
        
        for i in range(0, height - block_size + 1, block_size):
            for j in range(0, width - block_size + 1, block_size):
                block = y_channel[i:i+block_size, j:j+block_size]
                dct_block = fft.dctn(block, norm='ortho', axes=(0, 1))
                dct_coefficients.extend(np.abs(dct_block).flatten())
        
        dct_coefficients = np.array(dct_coefficients)
        
        # Build histogram
        hist, bins = np.histogram(dct_coefficients, bins=256, range=(0, 256))
        
        # Detect double compression by looking for periodic peaks
        # Double compression creates characteristic spikes at regular intervals
        peak_detection = _detect_dct_peaks(hist)
        has_periodic_peaks = peak_detection["has_peaks"]
        num_peaks = peak_detection["num_peaks"]
        peak_spacing_variance = peak_detection["spacing_variance"]
        
        # Calculate double compression confidence
        if has_periodic_peaks and num_peaks >= 3 and peak_spacing_variance < 10:
            is_double_compressed = True
            dct_confidence = 0.8
            compression_quality_estimate = _estimate_jpeg_quality(hist)
        else:
            is_double_compressed = False
            dct_confidence = 0.7
            compression_quality_estimate = None
        
        # Save histogram
        hist_path = str(EVIDENCE_DIR / f"dct_histogram_{uuid.uuid4()}.png")
        save_dct_histogram(hist, bins, hist_path)
        
        findings = []
        if is_double_compressed:
            findings.append(f"Detected {num_peaks} periodic peaks in DCT coefficient histogram.")
            findings.append(
                "Double JPEG compression creates characteristic quantization artifacts. "
                "Multiple compression stages violate the expected single-compression signature."
            )
            if compression_quality_estimate:
                findings.append(f"Estimated first compression quality: ~{compression_quality_estimate}%")
        else:
            findings.append("DCT histogram analysis shows single-compression characteristics.")
            findings.append("No periodic peaks indicating double JPEG compression detected.")
        
        logger.info(f"DCT analysis complete: double_compressed={is_double_compressed}")
        
        return {
            "engine": "DCT",
            "verdict": "manipulated" if is_double_compressed else "authentic",
            "confidence": float(dct_confidence),
            "findings": findings,
            "physics_law_violated": "DCT quantization distribution",
            "evidence_map_path": hist_path,
            "raw_scores": {
                "is_double_compressed": bool(is_double_compressed),
                "num_peaks": int(num_peaks),
                "peak_spacing_variance": float(peak_spacing_variance),
                "histogram_path": hist_path,
            }
        }
        
    except Exception as e:
        logger.error(f"Error in DCT analysis: {e}", exc_info=True)
        return _create_error_result("DCT", str(e))


def detect_blocking_artifacts(image_path: str) -> Dict[str, Any]:
    """
    Detect JPEG 8x8 block boundary misalignment.
    
    Physics: JPEG processes 8x8 blocks independently. Real JPEGs have consistent
    block grids throughout. Spliced regions from different sources have misaligned
    block grids (impossible without re-compression).
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dictionary with blocking artifact analysis
    """
    try:
        logger.info(f"Starting blocking artifact analysis on {image_path}")
        
        img = load_image_cv2(image_path)
        if img is None:
            return _create_error_result("Blocking", "Failed to load image")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Detect block boundaries by analyzing gradients at 8-pixel intervals
        block_size = 8
        height, width = gray.shape
        
        # Compute horizontal and vertical gradients
        sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        
        # Analyze boundary strength at multiples of 8
        horizontal_boundaries = []
        vertical_boundaries = []
        
        for i in range(block_size, height, block_size):
            row_gradient = np.mean(np.abs(sobel_y[max(0, i-1):min(height, i+1), :]))
            horizontal_boundaries.append(row_gradient)
        
        for j in range(block_size, width, block_size):
            col_gradient = np.mean(np.abs(sobel_x[:, max(0, j-1):min(width, j+1)]))
            vertical_boundaries.append(col_gradient)
        
        # Normal block boundaries should be slightly elevated
        # Misaligned regions have no boundary
        h_mean = np.mean(horizontal_boundaries) if horizontal_boundaries else 0
        h_std = np.std(horizontal_boundaries) if len(horizontal_boundaries) > 1 else 0
        v_mean = np.mean(vertical_boundaries) if vertical_boundaries else 0
        v_std = np.std(vertical_boundaries) if len(vertical_boundaries) > 1 else 0
        
        # Detect misaligned blocks (low gradient where boundary should be)
        h_threshold = h_mean - 2 * h_std
        v_threshold = v_mean - 2 * v_std
        
        misaligned_h = np.sum([g < h_threshold for g in horizontal_boundaries])
        misaligned_v = np.sum([g < v_threshold for g in vertical_boundaries])
        total_boundaries = len(horizontal_boundaries) + len(vertical_boundaries)
        
        misalignment_percentage = (misaligned_h + misaligned_v) / max(total_boundaries, 1) * 100
        
        # Confidence scoring
        if misalignment_percentage < 10:
            confidence = 0.85
            verdict = "authentic"
        elif misalignment_percentage < 25:
            confidence = 0.65
            verdict = "inconclusive"
        else:
            confidence = 0.80
            verdict = "manipulated"
        
        findings = []
        if misalignment_percentage > 20:
            findings.append(f"Detected {misalignment_percentage:.1f}% misaligned JPEG block boundaries.")
            findings.append(
                "JPEG blocks are 8x8 pixels and should have consistent grid alignment. "
                "Misaligned regions indicate content from different sources (different block grid phase)."
            )
        else:
            findings.append("JPEG block boundaries appear properly aligned throughout image.")
        
        logger.info(f"Blocking analysis complete: misalignment={misalignment_percentage:.1f}%")
        
        return {
            "engine": "Blocking",
            "verdict": verdict,
            "confidence": float(confidence),
            "findings": findings,
            "physics_law_violated": "Consistent JPEG block grid",
            "evidence_map_path": "",
            "raw_scores": {
                "misalignment_percentage": float(misalignment_percentage),
                "horizontal_misaligned": int(misaligned_h),
                "vertical_misaligned": int(misaligned_v),
                "boundary_strength_h_mean": float(h_mean),
                "boundary_strength_v_mean": float(v_mean),
            }
        }
        
    except Exception as e:
        logger.error(f"Error in blocking analysis: {e}", exc_info=True)
        return _create_error_result("Blocking", str(e))


# Helper functions

def _detect_dct_peaks(histogram: np.ndarray, threshold: float = 0.3) -> Dict[str, Any]:
    """
    Detect periodic peaks in DCT histogram (indicates double compression).
    
    Args:
        histogram: DCT coefficient histogram
        threshold: Peak detection threshold (fraction of max value)
        
    Returns:
        Dictionary with peak detection results
    """
    try:
        max_val = np.max(histogram)
        threshold_val = max_val * threshold
        
        peaks = []
        for i in range(1, len(histogram) - 1):
            if histogram[i] > threshold_val and histogram[i] > histogram[i-1] and histogram[i] > histogram[i+1]:
                peaks.append(i)
        
        if len(peaks) < 2:
            return {"has_peaks": False, "num_peaks": 0, "spacing_variance": 0}
        
        # Check if peaks are regularly spaced (periodic)
        spacings = np.diff(peaks)
        spacing_variance = np.var(spacings) if len(spacings) > 0 else 0
        
        return {
            "has_peaks": len(peaks) >= 3,
            "num_peaks": len(peaks),
            "spacing_variance": float(spacing_variance),
            "peak_positions": peaks.copy()
        }
    except Exception as e:
        logger.warning(f"Error detecting DCT peaks: {e}")
        return {"has_peaks": False, "num_peaks": 0, "spacing_variance": 0}


def _estimate_jpeg_quality(histogram: np.ndarray) -> Optional[int]:
    """
    Estimate original JPEG quality from DCT histogram.
    
    Uses heuristics based on peak positions and spacing.
    """
    try:
        # Simplified estimation based on histogram characteristics
        max_val = np.max(histogram)
        peak_count = np.sum(histogram > max_val * 0.3)
        
        if peak_count < 20:
            return 95
        elif peak_count < 40:
            return 85
        elif peak_count < 60:
            return 75
        else:
            return 65
    except Exception:
        return None


def save_dct_histogram(histogram: np.ndarray, bins: np.ndarray, output_path: str) -> None:
    """Save DCT histogram visualization."""
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        plt.bar(bins[:-1], histogram, width=1)
        plt.xlabel("DCT Coefficient Value")
        plt.ylabel("Frequency")
        plt.title("DCT Coefficient Histogram (Double Compression Detection)")
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
        logger.debug(f"Saved DCT histogram: {output_path}")
    except Exception as e:
        logger.error(f"Error saving DCT histogram: {e}")


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
