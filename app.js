// ===========================
// Navigation System
// ===========================
function navigateTo(screenId) {
    // Hide all screens
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => screen.classList.remove('active'));

    // Show target screen
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');

        // Initialize chart and update metrics if navigating to analytics
        if (screenId === 'analytics') {
            updateAnalyticsWithRealData();
            initializeChart();
        }
    }
}

// ===========================
// Voice Recording Functionality
// ===========================
let mediaRecorder = null;
let recordingTimer = null;
let recordingSeconds = 0;
let audioChunks = [];

async function toggleRecording() {
    const recordButton = document.getElementById('recordButton');
    const recordButtonText = document.getElementById('recordButtonText');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const successMessage = document.getElementById('successMessage');

    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());

                // Create audio blob
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

                // Upload to backend for analysis
                await uploadAndAnalyze(audioBlob);

                // Show success message
                successMessage.classList.remove('hidden');
                setTimeout(() => {
                    successMessage.classList.add('hidden');
                }, 3000);

                // Update last upload status
                updateLastUploadStatus();
            };

            mediaRecorder.start();

            // Update UI
            recordButton.classList.add('recording');
            recordButtonText.textContent = 'Stop Recording';
            recordingIndicator.classList.remove('hidden');

            // Start timer
            recordingSeconds = 0;
            updateRecordingTimer();
            recordingTimer = setInterval(() => {
                recordingSeconds++;
                updateRecordingTimer();

                // Auto-stop at 15 seconds
                if (recordingSeconds >= 15) {
                    toggleRecording();
                }
            }, 1000);

        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Unable to access microphone. Please check your permissions.');
        }
    } else {
        // Stop recording
        mediaRecorder.stop();

        // Update UI
        recordButton.classList.remove('recording');
        recordButtonText.textContent = 'Record Voice Sample';
        recordingIndicator.classList.add('hidden');

        // Clear timer
        clearInterval(recordingTimer);
        recordingSeconds = 0;
    }
}

function updateRecordingTimer() {
    const timerElement = document.getElementById('recordingTimer');
    const minutes = Math.floor(recordingSeconds / 60);
    const seconds = recordingSeconds % 60;
    timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateLastUploadStatus() {
    const statusElement = document.getElementById('lastUploadStatus');
    statusElement.textContent = 'Last sample uploaded: Just now';
}

// ===========================
// Backend API Integration
// ===========================
const API_URL = 'http://localhost:5000';
let latestAnalysis = null;

async function uploadAndAnalyze(audioBlob) {
    try {
        console.log('Converting audio to base64...');

        // Convert blob to base64
        const reader = new FileReader();
        const base64Audio = await new Promise((resolve, reject) => {
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(audioBlob);
        });

        console.log('Uploading to backend for analysis...');

        // Show loading state
        showAnalysisLoading();

        // Send to backend
        const response = await fetch(`${API_URL}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                audio: base64Audio,
                duration: recordingSeconds
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();
        console.log('Analysis complete:', result);

        if (result.success) {
            latestAnalysis = result.analysis;
            console.log('Risk score:', result.analysis.risk_score);
            console.log('Features:', result.analysis.features);
        } else {
            throw new Error(result.error || 'Analysis failed');
        }

        hideAnalysisLoading();

    } catch (error) {
        console.error('Error uploading audio:', error);
        hideAnalysisLoading();

        // Fallback to mock data if backend unavailable
        console.warn('Using mock data - backend may not be running');
        latestAnalysis = {
            risk_score: 0.23,
            confidence: 0.78,
            features: {
                jitter: 0.0045,
                shimmer: 0.032,
                hnr: 21.5,
                pitch_mean: 145.2,
                pitch_std: 12.3
            },
            metrics: {
                stability: 0.85,
                variability: 1.2,
                trend: '+3%'
            }
        };
    }
}

function showAnalysisLoading() {
    // Could add a loading spinner here
    console.log('Analyzing voice sample...');
}

function hideAnalysisLoading() {
    console.log('Analysis complete');
}

// ===========================
// Chart Visualization
// ===========================
function initializeChart() {
    const canvas = document.getElementById('voiceChart');
    const ctx = canvas.getContext('2d');

    // Set canvas size
    const container = canvas.parentElement;
    canvas.width = container.clientWidth - 48; // Account for padding
    canvas.height = 200;

    // Sample data for 12 weeks
    const data = [1.0, 0.95, 1.1, 1.2, 0.98, 1.05, 0.92, 1.15, 1.08, 1.0, 1.12, 1.25];
    const weeks = data.length;

    // Chart dimensions
    const padding = 30;
    const chartWidth = canvas.width - (padding * 2);
    const chartHeight = canvas.height - (padding * 2);

    // Calculate scales
    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);
    const valueRange = maxValue - minValue;
    const xStep = chartWidth / (weeks - 1);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid lines
    ctx.strokeStyle = '#E5E7EB';
    ctx.lineWidth = 1;

    // Horizontal grid lines
    for (let i = 0; i <= 4; i++) {
        const y = padding + (chartHeight / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(canvas.width - padding, y);
        ctx.stroke();
    }

    // Draw data line
    ctx.strokeStyle = '#6B9BD1';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    ctx.beginPath();
    data.forEach((value, index) => {
        const x = padding + (index * xStep);
        const normalizedValue = (value - minValue) / valueRange;
        const y = canvas.height - padding - (normalizedValue * chartHeight);

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();

    // Draw data points
    ctx.fillStyle = '#6B9BD1';
    data.forEach((value, index) => {
        const x = padding + (index * xStep);
        const normalizedValue = (value - minValue) / valueRange;
        const y = canvas.height - padding - (normalizedValue * chartHeight);

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });

    // Draw axis labels
    ctx.fillStyle = '#6B7280';
    ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.textAlign = 'center';

    // X-axis labels (weeks)
    [0, 3, 6, 9, 12].forEach(week => {
        const x = padding + ((week / (weeks - 1)) * chartWidth);
        ctx.fillText(week.toString(), x, canvas.height - 10);
    });

    // Y-axis label
    ctx.textAlign = 'left';
    ctx.fillText('Weeks', canvas.width / 2 - 15, canvas.height - 10);
}

// ===========================
// Initialize App
// ===========================
document.addEventListener('DOMContentLoaded', () => {
    // Show dashboard on load
    navigateTo('dashboard');

    // Handle window resize for chart
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const analyticsScreen = document.getElementById('analytics');
            if (analyticsScreen.classList.contains('active')) {
                initializeChart();
            }
        }, 250);
    });
});

// ===========================
// Update Detailed Report with Real Data
// ===========================
function updateAnalyticsWithRealData() {
    if (!latestAnalysis) {
        // Show default message
        document.getElementById('riskValue').textContent = 'No data';
        document.getElementById('scoreValue').textContent = '--';
        document.getElementById('confidenceValue').textContent = '--';
        return;
    }

    const { risk_score, confidence, features, clinical_concepts, explanation } = latestAnalysis;

    // Update Risk Assessment
    updateRiskAssessment(risk_score, confidence);

    // Update Clinical Analysis (CBM)
    updateClinicalAnalysis(clinical_concepts, explanation);

    // Update Biomarkers
    updateBiomarkers(features);

    // Update Interpretation
    updateInterpretation(risk_score, features);
}

function updateClinicalAnalysis(concepts, explanation) {
    const cbmCard = document.getElementById('cbmAnalysis');
    const conceptGrid = document.getElementById('conceptGrid');
    const explanationText = document.getElementById('aiExplanationText');

    if (!concepts) {
        cbmCard.style.display = 'none';
        return;
    }

    cbmCard.style.display = 'block';
    conceptGrid.innerHTML = ''; // Clear previous

    // Create progress bars for each concept
    Object.entries(concepts).forEach(([name, score]) => {
        // Determine color class
        let colorClass = 'low';
        if (score > 0.6) colorClass = 'high';
        else if (score > 0.3) colorClass = 'medium';

        const html = `
            <div class="concept-item">
                <div class="concept-header">
                    <span class="concept-name">${name.replace(/_/g, ' ')}</span>
                    <span class="concept-value">${(score * 100).toFixed(0)}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill ${colorClass}" style="width: ${score * 100}%"></div>
                </div>
            </div>
        `;
        conceptGrid.innerHTML += html;
    });

    // Update explanation
    if (explanation) {
        explanationText.textContent = explanation;
    } else {
        explanationText.textContent = "No explanation available.";
    }
}

function updateRiskAssessment(riskScore, confidence) {
    const riskValueEl = document.getElementById('riskValue');
    const scoreValueEl = document.getElementById('scoreValue');
    const confidenceValueEl = document.getElementById('confidenceValue');

    // Determine risk level
    let riskLevel, riskClass;
    if (riskScore < 0.3) {
        riskLevel = 'Low Risk';
        riskClass = 'low';
    } else if (riskScore < 0.7) {
        riskLevel = 'Moderate Risk';
        riskClass = 'moderate';
    } else {
        riskLevel = 'High Risk';
        riskClass = 'high';
    }

    riskValueEl.textContent = riskLevel;
    riskValueEl.className = `risk-value ${riskClass}`;
    scoreValueEl.textContent = `${(riskScore * 100).toFixed(1)}%`;
    confidenceValueEl.textContent = `${(confidence * 100).toFixed(1)}%`;
}

function updateBiomarkers(features) {
    // Jitter
    const jitterValue = features.jitter || 0;
    document.getElementById('jitterValue').textContent = jitterValue.toFixed(4);
    document.getElementById('jitterStatus').textContent = jitterValue > 0.006 ? 'Elevated' : 'Normal';
    document.getElementById('jitterStatus').className = `biomarker-status ${jitterValue > 0.006 ? 'elevated' : 'normal'}`;

    // Shimmer
    const shimmerValue = features.shimmer || 0;
    document.getElementById('shimmerValue').textContent = shimmerValue.toFixed(4);
    document.getElementById('shimmerStatus').textContent = shimmerValue > 0.04 ? 'Elevated' : 'Normal';
    document.getElementById('shimmerStatus').className = `biomarker-status ${shimmerValue > 0.04 ? 'elevated' : 'normal'}`;

    // HNR
    const hnrValue = features.hnr || 0;
    document.getElementById('hnrValue').textContent = hnrValue.toFixed(2) + ' dB';
    document.getElementById('hnrStatus').textContent = hnrValue < 20 ? 'Low' : 'Normal';
    document.getElementById('hnrStatus').className = `biomarker-status ${hnrValue < 20 ? 'elevated' : 'normal'}`;

    // Pitch Variability
    const pitchStd = features.pitch_std || 0;
    document.getElementById('pitchValue').textContent = pitchStd.toFixed(2) + ' Hz';
    document.getElementById('pitchStatus').textContent = pitchStd < 10 ? 'Reduced' : 'Normal';
    document.getElementById('pitchStatus').className = `biomarker-status ${pitchStd < 10 ? 'elevated' : 'normal'}`;

    // RPDE
    const rpdeValue = features.rpde || 0;
    document.getElementById('rpdeValue').textContent = rpdeValue.toFixed(3);
    document.getElementById('rpdeStatus').textContent = rpdeValue > 0.5 ? 'Elevated' : 'Normal';
    document.getElementById('rpdeStatus').className = `biomarker-status ${rpdeValue > 0.5 ? 'elevated' : 'normal'}`;
}

function updateInterpretation(riskScore, features) {
    const interpretationEl = document.getElementById('interpretationContent');

    let interpretation = '';

    if (riskScore < 0.3) {
        interpretation = `
            <p><strong>Low Risk Detected</strong></p>
            <p>Your voice analysis shows patterns consistent with healthy vocal characteristics. 
            The biomarkers measured (jitter, shimmer, HNR, pitch variability, and voice complexity) 
            are within normal ranges.</p>
            <p><strong>Recommendation:</strong> Continue regular monitoring. If you have any concerns about 
            your health or notice changes in your voice, speech, or movement, consult a healthcare provider.</p>
        `;
    } else if (riskScore < 0.7) {
        interpretation = `
            <p><strong>Moderate Risk Detected</strong></p>
            <p>Your voice analysis shows some biomarkers that deviate from typical healthy patterns. 
            This may indicate early changes in voice production, but does NOT confirm any medical condition.</p>
            <p><strong>Key Findings:</strong></p>
            <ul>
                ${features.jitter > 0.006 ? '<li>Elevated jitter (frequency variation) detected</li>' : ''}
                ${features.shimmer > 0.04 ? '<li>Elevated shimmer (amplitude variation) detected</li>' : ''}
                ${features.hnr < 20 ? '<li>Reduced voice quality (HNR) detected</li>' : ''}
                ${features.pitch_std < 10 ? '<li>Reduced pitch variability detected</li>' : ''}
                ${features.rpde > 0.5 ? '<li>Increased voice complexity (RPDE) detected</li>' : ''}
            </ul>
            <p><strong>Recommendation:</strong> Consider consulting a neurologist or healthcare provider 
            for a comprehensive evaluation. This analysis is NOT a diagnosis.</p>
        `;
    } else {
        interpretation = `
            <p><strong>High Risk Detected</strong></p>
            <p>Your voice analysis shows multiple biomarkers that significantly deviate from typical healthy patterns. 
            Several voice characteristics associated with neurological conditions have been detected.</p>
            <p><strong>Key Findings:</strong></p>
            <ul>
                ${features.jitter > 0.006 ? '<li>Significantly elevated jitter (frequency instability)</li>' : ''}
                ${features.shimmer > 0.04 ? '<li>Significantly elevated shimmer (amplitude instability)</li>' : ''}
                ${features.hnr < 20 ? '<li>Reduced voice quality and clarity</li>' : ''}
                ${features.pitch_std < 10 ? '<li>Reduced pitch range (monotone speech)</li>' : ''}
                ${features.rpde > 0.5 ? '<li>Irregular vocal patterns detected</li>' : ''}
            </ul>
            <p><strong>Important:</strong> This analysis is for informational purposes only and is NOT a medical diagnosis. 
            These findings warrant professional medical evaluation.</p>
            <p><strong>Urgent Recommendation:</strong> Please schedule an appointment with a neurologist or 
            movement disorder specialist for a comprehensive clinical assessment. Early detection and intervention 
            can be beneficial for many neurological conditions.</p>
        `;
    }

    interpretationEl.innerHTML = interpretation;
}
