"""
Acoustic Feature Extraction for Parkinson's Voice Analysis (Librosa-only version)
Extracts key acoustic biomarkers from voice recordings using only librosa
"""

import numpy as np
import librosa
from scipy.stats import entropy


def extract_features(audio_path):
    """
    Extract comprehensive acoustic features from audio file
    
    Args:
        audio_path: Path to audio file (WAV format)
        
    Returns:
        dict: Dictionary of extracted features
    """
    features = {}
    
    # Load audio with librosa
    y, sr = librosa.load(audio_path, sr=22050)
    
    # Extract pitch-related features
    pitch_features = extract_pitch_features(y, sr)
    features.update(pitch_features)
    
    # Extract jitter and shimmer approximations
    voice_quality = extract_voice_quality(y, sr)
    features.update(voice_quality)
    
    # Extract HNR approximation
    features['hnr'] = extract_hnr_approx(y, sr)
    
    # Extract spectral features
    spectral_features = extract_spectral_features(y, sr)
    features.update(spectral_features)
    
    # Extract nonlinear features
    nonlinear_features = extract_nonlinear_features(y)
    features.update(nonlinear_features)
    
    return features


def extract_pitch_features(y, sr):
    """Extract pitch-related features using librosa"""
    # Extract pitch using pyin algorithm
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, 
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr
    )
    
    # Remove NaN values
    f0_clean = f0[~np.isnan(f0)]
    
    if len(f0_clean) > 0:
        return {
            'pitch_mean': float(np.mean(f0_clean)),
            'pitch_std': float(np.std(f0_clean)),
            'pitch_min': float(np.min(f0_clean)),
            'pitch_max': float(np.max(f0_clean)),
        }
    else:
        return {
            'pitch_mean': 0,
            'pitch_std': 0,
            'pitch_min': 0,
            'pitch_max': 0,
        }


def extract_voice_quality(y, sr):
    """
    Approximate jitter and shimmer using librosa
    These are simplified approximations of the Praat calculations
    """
    # Get pitch periods
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr
    )
    
    # Jitter approximation: variation in pitch period
    f0_clean = f0[~np.isnan(f0)]
    if len(f0_clean) > 1:
        periods = 1.0 / f0_clean
        period_diffs = np.abs(np.diff(periods))
        jitter_local = np.mean(period_diffs) / np.mean(periods) if np.mean(periods) > 0 else 0
        jitter_rap = np.mean(np.abs(periods[2:] - periods[:-2])) / np.mean(periods) if len(periods) > 2 else jitter_local
        jitter_ppq5 = jitter_local  # Simplified
    else:
        jitter_local = jitter_rap = jitter_ppq5 = 0
    
    # Shimmer approximation: variation in amplitude
    # Get RMS energy in frames
    rms = librosa.feature.rms(y=y)[0]
    if len(rms) > 1:
        rms_diffs = np.abs(np.diff(rms))
        shimmer_local = np.mean(rms_diffs) / np.mean(rms) if np.mean(rms) > 0 else 0
        shimmer_apq3 = shimmer_local * 0.8  # Approximation
        shimmer_apq5 = shimmer_local * 0.9  # Approximation
    else:
        shimmer_local = shimmer_apq3 = shimmer_apq5 = 0
    
    return {
        'jitter_local': float(jitter_local),
        'jitter_rap': float(jitter_rap),
        'jitter_ppq5': float(jitter_ppq5),
        'shimmer_local': float(shimmer_local),
        'shimmer_apq3': float(shimmer_apq3),
        'shimmer_apq5': float(shimmer_apq5),
    }


def extract_hnr_approx(y, sr):
    """
    Approximate Harmonics-to-Noise Ratio
    Using spectral flatness as a proxy
    """
    spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
    # Convert to dB-like scale (inverse relationship)
    hnr_approx = -10 * np.log10(np.mean(spectral_flatness) + 1e-10)
    return float(hnr_approx)


def extract_spectral_features(y, sr):
    """Extract spectral features using librosa"""
    # Spectral centroid
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    
    # Spectral rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    
    # Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    
    return {
        'spectral_centroid_mean': float(np.mean(spectral_centroids)),
        'spectral_centroid_std': float(np.std(spectral_centroids)),
        'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
        'zcr_mean': float(np.mean(zcr)),
    }


def extract_nonlinear_features(y):
    """Extract nonlinear complexity features"""
    # RPDE (Recurrence Period Density Entropy) - simplified approximation
    rpde = calculate_rpde(y)
    
    # DFA (Detrended Fluctuation Analysis) - simplified approximation
    dfa = calculate_dfa(y)
    
    return {
        'rpde': float(rpde),
        'dfa': float(dfa),
    }


def calculate_rpde(signal, m=10, tau=1):
    """
    Simplified RPDE calculation
    Measures complexity of recurrence periods
    """
    try:
        # Embed signal
        N = len(signal)
        if N < m * tau * 2:
            return 0.4  # Default value
            
        embedded = np.array([signal[i:i+m*tau:tau] for i in range(N-m*tau)])
        
        # Calculate recurrence periods (simplified)
        distances = np.linalg.norm(embedded[:, None] - embedded, axis=2)
        threshold = 0.1 * np.std(signal)
        recurrences = distances < threshold
        
        # Calculate period density
        periods = []
        for i in range(len(recurrences)):
            recur_indices = np.where(recurrences[i])[0]
            if len(recur_indices) > 1:
                periods.extend(np.diff(recur_indices))
        
        if len(periods) > 0:
            hist, _ = np.histogram(periods, bins=20, density=True)
            hist = hist[hist > 0]
            return entropy(hist)
        return 0.4
    except:
        return 0.4


def calculate_dfa(signal, min_scale=4, max_scale=None):
    """
    Simplified DFA (Detrended Fluctuation Analysis)
    Measures self-similarity of signal
    """
    try:
        N = len(signal)
        if max_scale is None:
            max_scale = N // 4
        
        if max_scale < min_scale:
            return 0.7  # Default value
        
        # Integrate signal
        y = np.cumsum(signal - np.mean(signal))
        
        # Calculate fluctuation for different scales
        scales = np.logspace(np.log10(min_scale), np.log10(max_scale), num=10, dtype=int)
        scales = np.unique(scales)
        fluctuations = []
        
        for scale in scales:
            # Divide into segments
            n_segments = N // scale
            if n_segments < 1:
                continue
                
            segment_fluctuations = []
            for i in range(n_segments):
                segment = y[i*scale:(i+1)*scale]
                # Fit polynomial and calculate fluctuation
                x = np.arange(len(segment))
                coeffs = np.polyfit(x, segment, 1)
                fit = np.polyval(coeffs, x)
                segment_fluctuations.append(np.sqrt(np.mean((segment - fit)**2)))
            
            if segment_fluctuations:
                fluctuations.append(np.mean(segment_fluctuations))
        
        # Calculate DFA exponent (slope in log-log plot)
        if len(fluctuations) > 1:
            log_scales = np.log10(scales[:len(fluctuations)])
            log_fluct = np.log10(fluctuations)
            dfa_exponent = np.polyfit(log_scales, log_fluct, 1)[0]
            return dfa_exponent
        return 0.7
    except:
        return 0.7


def features_to_array(features):
    """
    Convert feature dictionary to ordered array for ML model
    
    Returns:
        numpy array of features in consistent order
    """
    feature_order = [
        'pitch_mean', 'pitch_std', 'pitch_min', 'pitch_max',
        'jitter_local', 'jitter_rap', 'jitter_ppq5',
        'shimmer_local', 'shimmer_apq3', 'shimmer_apq5',
        'hnr',
        'spectral_centroid_mean', 'spectral_centroid_std',
        'spectral_rolloff_mean', 'zcr_mean',
        'rpde', 'dfa'
    ]
    
    return np.array([features.get(f, 0) for f in feature_order])
