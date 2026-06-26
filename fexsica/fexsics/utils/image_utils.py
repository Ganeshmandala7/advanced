"""Image processing utilities."""

import numpy as np
import cv2
from typing import Tuple


class ImageUtils:
    """Image processing helper functions."""
    
    @staticmethod
    def normalize(image: np.ndarray) -> np.ndarray:
        """Normalize image to 0-1 range."""
        return image.astype(np.float32) / 255.0
    
    @staticmethod
    def denormalize(image: np.ndarray) -> np.ndarray:
        """Denormalize image from 0-1 to 0-255 range."""
        return (np.clip(image, 0, 1) * 255).astype(np.uint8)
    
    @staticmethod
    def resize(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """Resize image to target size."""
        return cv2.resize(image, size)
    
    @staticmethod
    def rgb_to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert RGB image to grayscale."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def rgb_to_hsv(image: np.ndarray) -> np.ndarray:
        """Convert RGB image to HSV."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
