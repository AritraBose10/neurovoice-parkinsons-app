"""
Flask API Server for Parkinson's Voice Analysis
Provides REST endpoints for audio analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import tempfile
import traceback

from feature_extraction import extract_features, features_to_array
from model import ParkinsonsModel, calculate_metrics

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize ML model
model = ParkinsonsModel()

# Try to load pre-trained model, otherwise train on startup
if not model.load_model():
    print("No pre-trained model found. Training new model...")
    model.train_model()
    model.save_model()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_trained': model.is_trained
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_voice():
    """
    Analyze voice recording for Parkinson's biomarkers
    
    Expects JSON with:
        - audio: base64 encoded WAV data
        - duration: recording duration in seconds
    
    Returns JSON with:
        - risk_score: 0-1 probability of Parkinson's indicators
        - confidence: model confidence
        - features: extracted acoustic features
        - metrics: user-friendly metrics
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'audio' not in data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        # Decode base64 audio
        audio_base64 = data['audio']
        
        # Remove data URL prefix if present
        if ',' in audio_base64:
            audio_base64 = audio_base64.split(',')[1]
        
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Extract acoustic features
            print(f"Extracting features from {temp_path}...")
            features = extract_features(temp_path)
            
            # Convert to array for model
            features_array = features_to_array(features)
            
            # Get prediction
            print("Running ML model prediction...")
            prediction = model.predict(features_array)
            
            # Calculate user-friendly metrics
            metrics = calculate_metrics(features)
            
            # Prepare response
            response = {
                'success': True,
                'analysis': {
                    'risk_score': prediction['risk_score'],
                    'confidence': prediction['confidence'],
                    'features': {
                        'jitter': round(features.get('jitter_local', 0), 6),
                        'shimmer': round(features.get('shimmer_local', 0), 6),
                        'hnr': round(features.get('hnr', 0), 2),
                        'pitch_mean': round(features.get('pitch_mean', 0), 2),
                        'pitch_std': round(features.get('pitch_std', 0), 2),
                        'rpde': round(features.get('rpde', 0), 3),
                        'dfa': round(features.get('dfa', 0), 3),
                    },
                    'metrics': metrics
                }
            }
            
            print(f"Analysis complete. Risk score: {prediction['risk_score']:.3f}")
            return jsonify(response)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'message': 'Parkinson\'s Voice Analysis API is running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'analyze': '/api/analyze (POST)',
            'test': '/api/test'
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Parkinson's Voice Analysis API Server")
    print("=" * 60)
    print(f"Model trained: {model.is_trained}")
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
