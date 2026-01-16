"""
Spectral Energy Voice Activity Detection (VAD)
Robust to hypophonia and dysarthric speech patterns
"""

import numpy as np
import librosa
from scipy.signal import medfilt


class SpectralEnergyVAD:
    """
    Voice Activity Detection using spectral energy
    More robust than amplitude thresholding for Parkinson's patients
    """
    
    def __init__(
        self,
        sr=22050,
        frame_length=2048,
        hop_length=512,
        energy_threshold=0.01,
        spectral_threshold=0.02,
        min_speech_duration=0.3,
        median_filter_size=5
    ):
        self.sr = sr
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.energy_threshold = energy_threshold
        self.spectral_threshold = spectral_threshold
        self.min_speech_frames = int(min_speech_duration * sr / hop_length)
        self.median_filter_size = median_filter_size
    
    def detect_speech(self, audio):
        """Detect speech segments in audio"""
        stft = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        spectral_energy = np.sum(np.abs(stft) ** 2, axis=0)
        spectral_flux = np.concatenate([[0], np.sqrt(np.sum(np.diff(np.abs(stft), axis=1) ** 2, axis=0))])
        
        spectral_energy = spectral_energy / (np.max(spectral_energy) + 1e-10)
        spectral_flux = spectral_flux / (np.max(spectral_flux) + 1e-10)
        
        energy_mean = np.mean(spectral_energy)
        energy_std = np.std(spectral_energy)
        adaptive_energy_threshold = max(self.energy_threshold, energy_mean + 0.5 * energy_std)
        
        voice_activity = ((spectral_energy > adaptive_energy_threshold) | (spectral_flux > self.spectral_threshold))
        voice_activity = medfilt(voice_activity.astype(float), kernel_size=self.median_filter_size).astype(bool)
        
        speech_segments = self._find_segments(voice_activity)
        speech_segments = [(start * self.hop_length / self.sr, end * self.hop_length / self.sr) for start, end in speech_segments]
        
        return speech_segments
    
    def _find_segments(self, voice_activity):
        """Find continuous speech segments"""
        segments = []
        in_speech = False
        start_frame = 0
        
        for i, is_speech in enumerate(voice_activity):
            if is_speech and not in_speech:
                start_frame = i
                in_speech = True
            elif not is_speech and in_speech:
                if i - start_frame >= self.min_speech_frames:
                    segments.append((start_frame, i))
                in_speech = False
        
        if in_speech and len(voice_activity) - start_frame >= self.min_speech_frames:
            segments.append((start_frame, len(voice_activity)))
        
        return segments
