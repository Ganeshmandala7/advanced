"""Configuration management for FeXsics."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import yaml
from pathlib import Path


class PhysicsConfig(BaseModel):
    """Configuration for physics engines."""
    
    enable_illumination_analysis: bool = True
    enable_prnu_analysis: bool = True
    enable_geometry_verification: bool = True
    enable_compression_analysis: bool = True
    enable_metadata_validation: bool = True


class DeepLearningConfig(BaseModel):
    """Configuration for deep learning models."""
    
    enable_mantranet: bool = True
    enable_faceforensics: bool = True
    enable_cnndetect: bool = True
    enable_mvss_net: bool = True
    model_confidence_threshold: float = Field(0.75, ge=0.0, le=1.0)
    device: str = "cuda"  # 'cuda' or 'cpu'


class BayesianConfig(BaseModel):
    """Configuration for Bayesian fusion engine."""
    
    use_prior_knowledge: bool = True
    artifact_taxonomy: Dict[str, Any] = Field(default_factory=dict)
    enable_neuro_symbolic: bool = True
    enable_automated_reasoning: bool = True


class ReportConfig(BaseModel):
    """Configuration for report generation."""
    
    output_format: str = "pdf"  # 'pdf', 'html', 'json'
    include_pixel_maps: bool = True
    include_statistical_analysis: bool = True
    include_physics_justification: bool = True
    anonymize_metadata: bool = False


class Config(BaseModel):
    """Main configuration for FeXsics system."""
    
    project_name: str = "FeXsics"
    version: str = "0.1.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    physics: PhysicsConfig = Field(default_factory=PhysicsConfig)
    deep_learning: DeepLearningConfig = Field(default_factory=DeepLearningConfig)
    bayesian: BayesianConfig = Field(default_factory=BayesianConfig)
    reports: ReportConfig = Field(default_factory=ReportConfig)
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**config_dict)
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to YAML file."""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
