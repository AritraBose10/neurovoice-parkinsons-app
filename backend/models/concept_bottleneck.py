"""
Concept Bottleneck Model for Parkinson's Detection
Demo version without PyTorch dependency
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


class ConceptBottleneckModel:
    """
    Concept Bottleneck Model
    DEMO MODE: Uses heuristic mapping instead of neural network
    In production, this would be a trained PyTorch model
    """
    
    CONCEPTS = ['tremor', 'breathiness', 'monotone', 'precision', 'rate_variability', 'harshness', 'strain']
    
    def __init__(self, input_dim: int = 768, n_concepts: int = 7, hidden_dim: int = 256):
        self.input_dim = input_dim
        self.n_concepts = n_concepts
        logger.info("CBM initialized in DEMO mode (no PyTorch)")
    
    def predict_with_explanation(self, features: np.ndarray, threshold: float = 0.5) -> dict:
        """Predict with human-readable explanation - DEMO VERSION"""
        # Placeholder - returns dummy predictions
        concepts = np.random.rand(self.n_concepts)
        diagnosis = np.random.rand()
        
        detected_concepts = []
        concept_scores = {}
        
        for i, concept_name in enumerate(self.CONCEPTS):
            score = float(concepts[i])
            concept_scores[concept_name] = score
            if score > threshold:
                detected_concepts.append({'name': concept_name, 'score': score})
        
        return {
            'risk_score': diagnosis,
            'concepts': concept_scores,
            'detected_concepts': detected_concepts,
            'explanation': "Demo mode - using heuristic mapping",
            'risk_level': 'moderate' if diagnosis > 0.5 else 'low'
        }
