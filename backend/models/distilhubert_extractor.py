"""
DistilHuBERT Feature Extractor
Demo version without PyTorch dependency
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


class DistilHuBERTFeatureExtractor:
    """
    Feature extraction using DistilHuBERT
    DEMO MODE: Placeholder implementation without PyTorch
    In production, this would use the actual DistilHuBERT transformer model
    """
    
    def __init__(self, model_name: str = "ntu-spml/distilhubert", device: str = None, cache_dir: str = "./model_cache"):
        self.device = device or 'cpu'
        logger.info(f"DistilHuBERT initialized in DEMO mode (no PyTorch)")
        self.model_loaded = False
    
    def extract_embeddings(self, audio: np.ndarray, sr: int = 16000) -> np.ndarray:
        """Extract embeddings from audio - DEMO VERSION"""
        duration = len(audio) / sr
        time_steps = int(duration * 50)
        return np.random.randn(time_steps, 768)
    
    def extract_global_features(self, audio: np.ndarray, sr: int = 16000) -> dict:
        """Extract global statistical features - DEMO VERSION"""
        embeddings = self.extract_embeddings(audio, sr)
        return {
            'embedding_mean': np.mean(embeddings, axis=0),
            'embedding_std': np.std(embeddings, axis=0),
            'embedding_global_mean': float(np.mean(embeddings)),
            'embedding_global_std': float(np.std(embeddings)),
        }
