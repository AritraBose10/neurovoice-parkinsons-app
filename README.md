# NeuroVoice - Parkinson's Voice Analysis

**Clinical-grade AI-powered voice analysis for early neurological risk monitoring**

⚠️ **IMPORTANT MEDICAL DISCLAIMER**

This application is for **research and educational purposes ONLY**. It is NOT a medical diagnostic tool and should not be used as a substitute for professional medical advice, diagnosis, or treatment. If you have concerns about Parkinson's disease or any neurological condition, please consult a qualified healthcare provider or neurologist.

## Features

- 🎤 **15-Second Voice Recording** - Quick and easy voice sample capture
- 🧠 **ML-Powered Analysis** - 17 acoustic biomarkers analyzed
- 📊 **Detailed Risk Report** - Clear risk assessment with biomarker breakdown
- 🔒 **Privacy-Focused** - Voice data processed securely
- 📱 **Clinical Design** - Professional, trustworthy interface

## Technology Stack

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Web Audio API for voice recording
- Canvas API for visualizations

**Backend:**
- Python 3.14 + Flask 3.0
- librosa 0.11 (acoustic analysis)
- scikit-learn 1.8 (ML model)
- 17 acoustic biomarkers: jitter, shimmer, HNR, RPDE, DFA, pitch, spectral features

## Quick Start

### Local Development

1. **Start Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Backend runs on `http://localhost:5000`

2. **Open Frontend:**
```bash
# Open index.html in browser or use:
python -m http.server 8000
```
Frontend at `http://localhost:8000`

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment guide to Render.com.

## How It Works

1. **Record** - 15-second voice sample
2. **Analyze** - ML model extracts 17 acoustic features
3. **Report** - Detailed risk assessment with biomarker analysis

### Biomarkers Analyzed

- **Jitter** - Frequency variation (vocal fold instability)
- **Shimmer** - Amplitude variation (vocal fold weakness)
- **HNR** - Harmonics-to-Noise Ratio (voice quality)
- **Pitch Variability** - Fundamental frequency changes
- **RPDE** - Recurrence Period Density Entropy (complexity)
- Plus 12 additional spectral and nonlinear features

## Risk Levels

- **Low Risk (< 30%)** - Normal biomarkers
- **Moderate Risk (30-70%)** - Some elevated biomarkers
- **High Risk (> 70%)** - Multiple concerning biomarkers

## License & Disclaimer

**For Educational/Research Use Only**

- NOT FDA approved
- NOT clinically validated
- NOT HIPAA compliant
- Requires professional medical evaluation for any health concerns

## Project Structure

```
voice/
├── index.html              # Frontend application
├── styles.css              # Clinical design system
├── app.js                  # Frontend logic
├── backend/
│   ├── app.py             # Flask API server
│   ├── feature_extraction.py  # Acoustic analysis
│   ├── model.py           # ML model
│   ├── requirements.txt   # Python dependencies
│   ├── Procfile          # Deployment config
│   └── runtime.txt       # Python version
├── README.md
└── DEPLOYMENT.md
```

## Contributing

This is an educational project demonstrating voice biomarker analysis for Parkinson's detection. Contributions welcome for:
- Improved ML models
- Additional biomarkers
- UI/UX enhancements
- Documentation

## Acknowledgments

Built with clinical design principles for health-tech applications. Inspired by research in voice biomarkers for neurological conditions.

---

**Remember:** This tool is for informational purposes only. Always consult healthcare professionals for medical advice.
