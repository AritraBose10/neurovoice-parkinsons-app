"""
Parkinson's Detection ML Model
Uses Random Forest classifier trained on acoustic features
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os


class ParkinsonsModel:
    """
    Machine Learning model for Parkinson's detection from voice features
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        
    def train_model(self):
        """
        Train model on synthetic/example data
        In production, this would use real clinical data
        """
        # Create synthetic training data based on research literature
        # Parkinson's patients typically show:
        # - Higher jitter and shimmer
        # - Lower HNR
        # - Higher RPDE
        # - Different DFA values
        
        np.random.seed(42)
        n_samples = 200
        
        # Healthy samples (class 0)
        healthy_samples = []
        for _ in range(n_samples // 2):
            sample = {
                'pitch_mean': np.random.normal(150, 20),
                'pitch_std': np.random.normal(10, 3),
                'pitch_min': np.random.normal(100, 15),
                'pitch_max': np.random.normal(200, 25),
                'jitter_local': np.random.normal(0.003, 0.001),
                'jitter_rap': np.random.normal(0.002, 0.0008),
                'jitter_ppq5': np.random.normal(0.002, 0.0008),
                'shimmer_local': np.random.normal(0.025, 0.008),
                'shimmer_apq3': np.random.normal(0.015, 0.005),
                'shimmer_apq5': np.random.normal(0.018, 0.006),
                'hnr': np.random.normal(22, 3),
                'spectral_centroid_mean': np.random.normal(2000, 300),
                'spectral_centroid_std': np.random.normal(500, 100),
                'spectral_rolloff_mean': np.random.normal(3500, 500),
                'zcr_mean': np.random.normal(0.05, 0.01),
                'rpde': np.random.normal(0.4, 0.05),
                'dfa': np.random.normal(0.7, 0.1),
            }
            healthy_samples.append(list(sample.values()))
        
        # Parkinson's samples (class 1)
        parkinsons_samples = []
        for _ in range(n_samples // 2):
            sample = {
                'pitch_mean': np.random.normal(145, 25),
                'pitch_std': np.random.normal(15, 5),
                'pitch_min': np.random.normal(95, 20),
                'pitch_max': np.random.normal(195, 30),
                'jitter_local': np.random.normal(0.006, 0.002),  # Higher
                'jitter_rap': np.random.normal(0.004, 0.0015),   # Higher
                'jitter_ppq5': np.random.normal(0.004, 0.0015),  # Higher
                'shimmer_local': np.random.normal(0.045, 0.015), # Higher
                'shimmer_apq3': np.random.normal(0.028, 0.010),  # Higher
                'shimmer_apq5': np.random.normal(0.032, 0.012),  # Higher
                'hnr': np.random.normal(18, 4),                  # Lower
                'spectral_centroid_mean': np.random.normal(1900, 350),
                'spectral_centroid_std': np.random.normal(550, 120),
                'spectral_rolloff_mean': np.random.normal(3300, 550),
                'zcr_mean': np.random.normal(0.06, 0.015),
                'rpde': np.random.normal(0.5, 0.08),             # Higher
                'dfa': np.random.normal(0.65, 0.12),
            }
            parkinsons_samples.append(list(sample.values()))
        
        # Combine data
        X = np.array(healthy_samples + parkinsons_samples)
        y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
        
        # Shuffle
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print(f"Model trained on {len(X)} samples")
        print(f"Training accuracy: {self.model.score(X_scaled, y):.3f}")
        
    def predict(self, features_array):
        """
        Predict Parkinson's risk from feature array
        
        Args:
            features_array: numpy array of acoustic features
            
        Returns:
            dict with risk_score and confidence
        """
        if not self.is_trained:
            self.train_model()
        
        # Ensure 2D array
        if features_array.ndim == 1:
            features_array = features_array.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features_array)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Risk score is probability of Parkinson's class
        risk_score = probabilities[1]
        
        # Confidence is the difference between the two probabilities
        confidence = abs(probabilities[1] - probabilities[0])
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'prediction': int(risk_score > 0.5)
        }
    
    def save_model(self, path='model_data'):
        """Save trained model and scaler"""
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.model, os.path.join(path, 'model.pkl'))
        joblib.dump(self.scaler, os.path.join(path, 'scaler.pkl'))
        
    def load_model(self, path='model_data'):
        """Load trained model and scaler"""
        try:
            self.model = joblib.load(os.path.join(path, 'model.pkl'))
            self.scaler = joblib.load(os.path.join(path, 'scaler.pkl'))
            self.is_trained = True
            return True
        except:
            return False


def calculate_metrics(features):
    """
    Calculate user-friendly metrics from acoustic features
    
    Returns:
        dict with stability, variability, and trend metrics
    """
    # Stability: inverse of jitter/shimmer (higher is better)
    jitter_avg = (features.get('jitter_local', 0) + 
                  features.get('jitter_rap', 0) + 
                  features.get('jitter_ppq5', 0)) / 3
    shimmer_avg = (features.get('shimmer_local', 0) + 
                   features.get('shimmer_apq3', 0) + 
                   features.get('shimmer_apq5', 0)) / 3
    
    # Normalize to 0-1 scale (typical ranges)
    jitter_norm = max(0, min(1, 1 - (jitter_avg / 0.01)))
    shimmer_norm = max(0, min(1, 1 - (shimmer_avg / 0.08)))
    stability = (jitter_norm + shimmer_norm) / 2
    
    # Variability: pitch standard deviation (normalized)
    pitch_std = features.get('pitch_std', 0)
    variability = min(2.0, pitch_std / 10)  # Scale to reasonable range
    
    # Trend: based on HNR and RPDE
    hnr = features.get('hnr', 20)
    rpde = features.get('rpde', 0.4)
    
    # Higher HNR and lower RPDE is better
    hnr_score = (hnr - 15) / 10  # Normalize around typical range
    rpde_score = (0.5 - rpde) / 0.2
    trend_value = (hnr_score + rpde_score) / 2
    
    # Convert to percentage
    trend_pct = int(trend_value * 10)
    trend = f"+{trend_pct}%" if trend_pct >= 0 else f"{trend_pct}%"
    
    return {
        'stability': round(stability, 2),
        'variability': round(variability, 1),
        'trend': trend
    }
