"""
Forced Alignment for Parkinson's Voice Analysis
Simplified version using DTW
"""

import numpy as np
import librosa
from typing import List, Tuple, Dict


class ForcedAligner:
    """Simplified forced alignment using DTW"""
    
    def __init__(self, sr=22050):
        self.sr = sr
    
    def segment_by_pauses(self, audio: np.ndarray, min_pause_duration: float = 0.2, energy_threshold: float = 0.01) -> List[Tuple[float, float]]:
        """Segment audio by detecting pauses"""
        hop_length = 512
        rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        rms = rms / (np.max(rms) + 1e-10)
        is_pause = rms < energy_threshold
        
        segments = []
        in_speech = False
        start_frame = 0
        min_pause_frames = int(min_pause_duration * self.sr / hop_length)
        
        for i, pause in enumerate(is_pause):
            if not pause and not in_speech:
                start_frame = i
                in_speech = True
            elif pause and in_speech:
                pause_start = i
                pause_end = i
                while pause_end < len(is_pause) and is_pause[pause_end]:
                    pause_end += 1
                if pause_end - pause_start >= min_pause_frames:
                    segments.append((start_frame * hop_length / self.sr, pause_start * hop_length / self.sr))
                    in_speech = False
        
        if in_speech:
            segments.append((start_frame * hop_length / self.sr, len(audio) / self.sr))
        
        return segments


class AlignmentResult:
    """Container for alignment results"""
    
    def __init__(self, segments: List[Tuple[float, float]]):
        self.segments = segments
    
    def to_dict(self):
        return {
            'segments': [{'start': start, 'end': end, 'duration': end - start} for start, end in self.segments]
        }
