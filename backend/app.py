"""
Flask API Server for Parkinson's Voice Analysis
Advanced ML Pipeline Integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import tempfile
import traceback
import numpy as np
import logging

# Legacy modules (fallback)
from feature_extraction import extract_features, features_to_array
from model import ParkinsonsModel, calculate_metrics

# Advanced ML modules
from preprocessing import SpectralEnergyVAD
from models import DistilHuBERTFeatureExtractor, ConceptBottleneckModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ==========================================
# Initialize Models
# ==========================================
logger.info("Initializing ML Pipeline...")

# 1. Legacy Model (Random Forest)
legacy_model = ParkinsonsModel()
if not legacy_model.load_model():
    logger.info("Training legacy model on synthetic data...")
    legacy_model.train_model()

# 2. Advanced Preprocessing
vad = SpectralEnergyVAD()

# 3. Deep Learning Models (Lazy loading suggested for production)
try:
    # Initialize DistilHuBERT (pre-trained)
    logger.info("Loading DistilHuBERT...")
    distilhubert = DistilHuBERTFeatureExtractor()
    
    # Initialize CBM (Untrained - using heuristic mode for demo)
    cbm = ConceptBottleneckModel()
    logger.info("Advanced models loaded successfully")
    advanced_models_active = True
except Exception as e:
    logger.warning(f"Could not load deep learning models: {e}")
    logger.warning("Running in LEGACY mode (Random Forest only)")
    advanced_models_active = False


def heuristic_concept_mapping(legacy_features):
    """
    Demo helper: Map legacy acoustic features to clinical concepts
    Used until CBM is fully trained on labeled data
    """
    # Normalize features roughly to 0-1 range
    jitter = min(legacy_features.get('jitter_local', 0) * 100, 1.0)
    shimmer = min(legacy_features.get('shimmer_local', 0) * 20, 1.0)
    hnr = max(0, (25 - legacy_features.get('hnr', 20)) / 25)  # Lower HNR is worse
    pitch_std = max(0, (50 - legacy_features.get('pitch_std', 20)) / 50) # Lower std is worse (monitone)
    
    return {
        'tremor': jitter * 0.8 + 0.1,         # Jitter relates to tremor
        'breathiness': hnr * 0.7 + 0.1,       # Low HNR relates to breathiness
        'monotone': pitch_std * 0.9,          # Low pitch var relates to monotone
        'precision': shimmer * 0.6 + 0.2,     # Shimmer relates to articulation
        'rate_variability': 0.3,              # Placeholder
        'harshness': jitter * 0.5 + shimmer * 0.5,
        'strain': jitter * 0.4 + 0.1
    }

@app.route('/api/analyze', methods=['POST'])
def analyze_voice():
    try:
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode audio
        audio_base64 = data['audio']
        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # 1. Pipeline: Legacy Feature Extraction (Fast & Reliable baseline)
            features = extract_features(temp_path)
            features_array = features_to_array(features)
            legacy_pred = legacy_model.predict(features_array)
            
            # 2. Pipeline: Advanced Analysis
            concepts = {}
            explanation = ""
            
            if advanced_models_active:
                # In a real deployed training loop, we would:
                # 1. Load audio with librosa
                # 2. Run VAD
                # 3. Extract DistilHuBERT embeddings
                # 4. Run CBM forward pass
                
                # For this DEMO without trained CBM weights, we use the 
                # heuristic mapping to show the UI capabilities
                concepts = heuristic_concept_mapping(features)
                
                # Generate explanation based on these scores
                triggers = []
                if concepts['tremor'] > 0.4: triggers.append('detectable vocal tremor')
                if concepts['monotone'] > 0.5: triggers.append('reduced pitch variation (monotone)')
                if concepts['breathiness'] > 0.4: triggers.append('breathy voice quality')
                
                if triggers:
                    explanation = f"Analysis detects {', '.join(triggers)}."
                else:
                    explanation = "Voice characteristics appear stable with no significant clinical indicators."
            
            # Prepare Response
            response = {
                'success': True,
                'analysis': {
                    'risk_score': legacy_pred['risk_score'],
                    'confidence': legacy_pred['confidence'],
                    'features': {
                        'jitter': round(features.get('jitter_local', 0), 5),
                        'shimmer': round(features.get('shimmer_local', 0), 5),
                        'hnr': round(features.get('hnr', 0), 2),
                        'pitch_std': round(features.get('pitch_std', 0), 2),
                        'rpde': round(features.get('rpde', 0), 3)
                    },
                    'clinical_concepts': concepts,  # NEW: For CBM display
                    'explanation': explanation      # NEW: NLP explanation
                }
            }
            
            return jsonify(response)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'advanced_models': advanced_models_active,
        'legacy_model': legacy_model.is_trained
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
