"""Main image processor for FeXsics analysis pipeline."""

from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import cv2
from loguru import logger

from .config import Config


class ImageProcessor:
    """Central image processor coordinating all 7 physics layers."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize ImageProcessor.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self.image: Optional[np.ndarray] = None
        self.image_path: Optional[Path] = None
        self.analysis_results: Dict[str, Any] = {}
        
        logger.remove()  # Remove default handler
        logger.add(
            lambda msg: print(msg, end=''),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level=self.config.log_level
        )
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file.
        
        Args:
            image_path: Path to image file.
            
        Returns:
            Loaded image as numpy array.
        """
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        self.image = cv2.imread(str(self.image_path))
        if self.image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        logger.info(f"Loaded image: {self.image_path}")
        logger.debug(f"Image shape: {self.image.shape}")
        
        return self.image
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Run complete physics-grounded forensic analysis pipeline.
        
        Returns:
            Dictionary containing analysis results from all 7 layers.
        """
        if self.image is None:
            raise ValueError("No image loaded. Call load_image() first.")
        
        logger.info("Starting full forensic analysis pipeline...")
        
        # Placeholder for layer coordination
        # Will be populated as layers are implemented
        self.analysis_results = {
            "status": "analysis_initiated",
            "image_shape": self.image.shape,
            "layers_completed": []
        }
        
        return self.analysis_results
    
    def get_results(self) -> Dict[str, Any]:
        """Get current analysis results."""
        return self.analysis_results
