"""Artifact taxonomy for classifying forensic findings."""

from typing import Dict, List, Any
from enum import Enum


class ArtifactDomain(Enum):
    """Artifact classification domains."""
    STRUCTURAL = "structural"
    TEXTURAL = "textural"
    LIGHTING = "lighting"
    COMPOSITIONAL = "compositional"
    PERCEPTUAL = "perceptual"


class ArtifactTaxonomy:
    """Classifies flaws into five domains."""
    
    def __init__(self):
        """Initialize artifact taxonomy."""
        self.artifacts = {domain: [] for domain in ArtifactDomain}
    
    def classify_artifact(self, artifact_name: str, 
                         domain: ArtifactDomain, 
                         confidence: float,
                         details: Dict[str, Any]) -> None:
        """
        Classify and register an artifact.
        
        Args:
            artifact_name: Name of the artifact.
            domain: Domain classification.
            confidence: Confidence score.
            details: Artifact details.
        """
        self.artifacts[domain].append({
            "name": artifact_name,
            "confidence": confidence,
            "details": details
        })
    
    def get_taxonomy_report(self) -> Dict[str, Any]:
        """
        Generate taxonomy report.
        
        Returns:
            Report of all artifacts organized by domain.
        """
        return {
            "status": "taxonomy_generated",
            "artifacts_by_domain": {
                domain.value: self.artifacts[domain]
                for domain in ArtifactDomain
            },
            "total_artifacts": sum(
                len(artifacts) for artifacts in self.artifacts.values()
            )
        }
