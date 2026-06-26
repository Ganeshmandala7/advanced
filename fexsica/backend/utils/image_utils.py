"""Image utility functions for Fexsics."""

import logging
from pathlib import Path
from typing import Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)


def load_image_cv2(image_path: str) -> Optional[np.ndarray]:
    """
    Load image using OpenCV (BGR format).
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image as numpy array (BGR) or None if failed
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Failed to load image: {image_path}")
            return None
        logger.debug(f"Loaded image: {image_path} - shape: {img.shape}")
        return img
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None


def load_image_pil(image_path: str) -> Optional[Image.Image]:
    """
    Load image using PIL (RGB format).
    
    Args:
        image_path: Path to image file
        
    Returns:
        PIL Image object or None if failed
    """
    try:
        img = Image.open(image_path)
        logger.debug(f"Loaded PIL image: {image_path} - format: {img.format}, mode: {img.mode}")
        return img
    except Exception as e:
        logger.error(f"Error loading image with PIL {image_path}: {e}")
        return None


def convert_bgr_to_rgb(img_bgr: np.ndarray) -> np.ndarray:
    """Convert BGR image to RGB."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def convert_bgr_to_gray(img_bgr: np.ndarray) -> np.ndarray:
    """Convert BGR image to grayscale."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)


def convert_bgr_to_lab(img_bgr: np.ndarray) -> np.ndarray:
    """Convert BGR image to LAB color space."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)


def convert_bgr_to_hsv(img_bgr: np.ndarray) -> np.ndarray:
    """Convert BGR image to HSV color space."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)


def convert_bgr_to_ycrcb(img_bgr: np.ndarray) -> np.ndarray:
    """Convert BGR image to YCrCb color space."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)


def save_heatmap(heatmap: np.ndarray, output_path: str, cmap: str = "jet") -> None:
    """
    Save heatmap as image using matplotlib colormap.
    
    Args:
        heatmap: 2D array representing heatmap values
        output_path: Path to save heatmap image
        cmap: Matplotlib colormap name
    """
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 9))
        plt.imshow(heatmap, cmap=cmap)
        plt.colorbar()
        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches="tight")
        plt.close()
        logger.debug(f"Saved heatmap: {output_path}")
    except Exception as e:
        logger.error(f"Error saving heatmap {output_path}: {e}")


def normalize_image(img: np.ndarray) -> np.ndarray:
    """Normalize image to 0-1 range."""
    return img.astype(np.float32) / 255.0


def denormalize_image(img: np.ndarray) -> np.ndarray:
    """Denormalize image from 0-1 range to 0-255."""
    return np.clip(img * 255, 0, 255).astype(np.uint8)


def get_image_dimensions(image_path: str) -> Optional[Tuple[int, int, int]]:
    """
    Get image dimensions (height, width, channels).
    
    Returns:
        Tuple of (height, width, channels) or None if failed
    """
    img = load_image_cv2(image_path)
    if img is None:
        return None
    return img.shape


def crop_image(img: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """Crop image to specified region."""
    return img[y:y+height, x:x+width]


def resize_image(img: np.ndarray, width: int, height: int, 
                interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
    """Resize image to specified dimensions."""
    return cv2.resize(img, (width, height), interpolation=interpolation)


def apply_gaussian_blur(img: np.ndarray, kernel_size: int = 5, sigma: float = 1.0) -> np.ndarray:
    """Apply Gaussian blur to image."""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)


def apply_bilateral_filter(img: np.ndarray, diameter: int = 9, 
                          sigma_color: float = 75, sigma_space: float = 75) -> np.ndarray:
    """Apply bilateral filter (preserves edges while smoothing)."""
    if len(img.shape) == 2:  # grayscale
        return cv2.bilateralFilter(img, diameter, sigma_color, sigma_space)
    else:  # color
        return cv2.bilateralFilter(img, diameter, sigma_color, sigma_space)


def compute_histogram(img: np.ndarray, bins: int = 256) -> np.ndarray:
    """Compute image histogram."""
    if len(img.shape) == 3:
        img = convert_bgr_to_gray(img)
    return cv2.calcHist([img], [0], None, [bins], [0, 256])


def get_image_format(image_path: str) -> Optional[str]:
    """Get image format from file extension."""
    try:
        ext = Path(image_path).suffix.lower().strip('.')
        return ext if ext in {'jpeg', 'jpg', 'png', 'tiff', 'tif', 'webp', 'bmp'} else None
    except Exception as e:
        logger.error(f"Error getting image format: {e}")
        return None
