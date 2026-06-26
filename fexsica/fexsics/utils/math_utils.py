"""Mathematical utilities."""

import numpy as np
from typing import Tuple


class MathUtils:
    """Mathematical helper functions."""
    
    @staticmethod
    def normalize_vector(v: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length."""
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v
    
    @staticmethod
    def angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float:
        """Compute angle between two vectors in radians."""
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.arccos(np.clip(cos_angle, -1, 1))
    
    @staticmethod
    def compute_statistics(data: np.ndarray) -> dict:
        """Compute basic statistics."""
        return {
            "mean": np.mean(data),
            "std": np.std(data),
            "min": np.min(data),
            "max": np.max(data),
            "median": np.median(data)
        }
