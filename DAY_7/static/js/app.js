/**
 * Violence Detection AI - Frontend Application
 * Handles video upload, webcam streaming, and real-time detection
 */

// ======================== State Management ========================

const state = {
    selectedFile: null,
    webcamActive: false,
    threshold: parseFloat(document.querySelector('input[type="range"]').value) || 0.5,
    webcamStream: null,
    webcamIntervalId: null
};

// ======================== DOM Elements ========================

const uploadZone = document.getElementById('uploadZone');
const videoInput = document.getElementById('videoInput');
const previewVideo = document.getElementById('previewVideo');
const videoPreviewContainer = document.getElementById('videoPreview');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const startWebcamBtn = document.getElementById('startWebcamBtn');
const stopWebcamBtn = document.getElementById('stopWebcamBtn');
const webcamPlaceholder = document.getElementById('webcamPlaceholder');
const webcamStream = document.getElementById('webcamStream');
const resultsContent = document.getElementById('resultsContent');
const emptyState = document.getElementById('emptyState');
const alertContainer = document.getElementById('alertContainer');
const thresholdSlider = document.getElementById('thresholdSlider');
const thresholdValue = document.getElementById('thresholdValue');

// ======================== Event Listeners ========================

/**
 * Upload Zone - Drag and Drop
 */
uploadZone.addEventListener('click', () => videoInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

/**
 * Video Input - File Selection
 */
videoInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

/**
 * Upload Button
 */
uploadBtn.addEventListener('click', uploadAndDetect);

/**
 * Clear Button
 */
clearBtn.addEventListener('click', clearSelection);

/**
 * Webcam Buttons
 */
startWebcamBtn.addEventListener('click', startWebcam);
stopWebcamBtn.addEventListener('click', stopWebcam);

/**
 * Threshold Slider
 */
thresholdSlider.addEventListener('input', (e) => {
    state.threshold = parseFloat(e.target.value);
    thresholdValue.textContent = state.threshold.toFixed(2);
});

// ======================== File Handling ========================

/**
 * Handle file selection from input or drag-drop
 */
function handleFileSelect(file) {
    // Validate file
    const maxSize = 500 * 1024 * 1024; // 500MB
    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 
                          'image/jpeg', 'image/png'];
    
    if (file.size > maxSize) {
        showAlert('File size exceeds 500MB limit', 'error');
        return;
    }

    if (!allowedTypes.some(type => file.type.startsWith(type.split('/')[0]))) {
        showAlert('Unsupported file type. Please upload a video or image.', 'error');
        return;
    }

    state.selectedFile = file;
    displayFilePreview(file);
    uploadBtn.disabled = false;
    clearBtn.style.display = 'block';
    uploadZone.style.opacity = '0.7';
}

/**
 * Display file preview
 */
function displayFilePreview(file) {
    if (file.type.startsWith('video/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewVideo.src = e.target.result;
            videoPreviewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewVideo.src = e.target.result;
            videoPreviewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

/**
 * Clear file selection
 */
function clearSelection() {
    state.selectedFile = null;
    videoInput.value = '';
    videoPreviewContainer.style.display = 'none';
    progressBar.style.display = 'none';
    uploadBtn.disabled = true;
    clearBtn.style.display = 'none';
    uploadZone.style.opacity = '1';
}

// ======================== Upload and Detection ========================

/**
 * Upload file and perform detection
 */
async function uploadAndDetect() {
    if (!state.selectedFile) {
        showAlert('Please select a file first', 'error');
        return;
    }

    uploadBtn.disabled = true;
    progressBar.style.display = 'block';

    const formData = new FormData();
    formData.append('file', state.selectedFile);
    formData.append('source', 'upload');

    try {
        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressFill.style.width = percentComplete + '%';
                progressText.textContent = Math.round(percentComplete);
            }
        });

        // Handle response
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                displayResults(response);
                showAlert('Detection completed successfully!', 'success');
            } else {
                const response = JSON.parse(xhr.responseText);
                showAlert(response.message || 'Detection failed', 'error');
            }
            uploadBtn.disabled = false;
        });

        xhr.addEventListener('error', () => {
            showAlert('Upload failed. Please try again.', 'error');
            uploadBtn.disabled = false;
        });

        xhr.open('POST', '/api/detect');
        xhr.send(formData);

    } catch (error) {
        console.error('Upload error:', error);
        showAlert('An error occurred during upload', 'error');
        uploadBtn.disabled = false;
    }
}

// ======================== Display Results ========================

/**
 * Display detection results
 */
function displayResults(data) {
    if (!data.success) {
        showAlert('Error: ' + data.message, 'error');
        return;
    }

    const detections = data.detections || [];

    // Update stats
    document.getElementById('totalDetections').textContent = detections.length;
    
    const personDetections = detections.filter(d => d.class === 'person');
    document.getElementById('personCount').textContent = personDetections.length;
    
    const avgConfidence = detections.length > 0
        ? (detections.reduce((sum, d) => sum + d.confidence, 0) / detections.length * 100).toFixed(1)
        : '0';
    document.getElementById('avgConfidence').textContent = avgConfidence + '%';

    // Display detections
    const detectionsList = document.getElementById('detectionsList');
    detectionsList.innerHTML = '';

    if (detections.length === 0) {
        detectionsList.innerHTML = '<div class="empty-state"><p>No objects detected</p></div>';
    } else {
        detections.forEach((detection, index) => {
            const item = document.createElement('div');
            item.className = 'detection-item';
            item.innerHTML = `
                <strong>#${index + 1}: ${detection.class}</strong>
                <small>Confidence: <span class="confidence">${(detection.confidence * 100).toFixed(1)}%</span></small>
            `;
            detectionsList.appendChild(item);
        });
    }

    // Update timestamp
    document.getElementById('timestamp').textContent = `Analysis completed at ${new Date().toLocaleString()}`;

    // Show results
    resultsContent.classList.add('show');
    emptyState.style.display = 'none';
}

// ======================== Webcam Handling ========================

/**
 * Start webcam stream
 */
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 }
            }
        });

        state.webcamStream = stream;
        state.webcamActive = true;

        // Hide placeholder and show stream image
        webcamPlaceholder.style.display = 'none';
        webcamStream.style.display = 'block';

        // Update button states
        startWebcamBtn.style.display = 'none';
        stopWebcamBtn.style.display = 'block';

        showAlert('Webcam started. Processing frames...', 'info');

        // Start streaming frames
        streamWebcamFrames(stream);

    } catch (error) {
        console.error('Webcam error:', error);
        showAlert('Could not access webcam: ' + error.message, 'error');
    }
}

/**
 * Stream webcam frames to detection API
 */
function streamWebcamFrames(stream) {
    const video = document.createElement('video');
    video.srcObject = stream;
    video.play();

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size
    video.onloadedmetadata = () => {
        canvas.width = 640;
        canvas.height = 480;
    };

    // Stream frames to server every 500ms
    state.webcamIntervalId = setInterval(() => {
        if (!state.webcamActive) {
            clearInterval(state.webcamIntervalId);
            return;
        }

        // Draw video frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to blob and send
        canvas.toBlob((blob) => {
            const formData = new FormData();
            formData.append('file', blob, 'webcam_frame.jpg');
            formData.append('source', 'webcam');

            fetch('/api/detect', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Display frame in image element
                    const frameBlob = new Blob([blob], { type: 'image/jpeg' });
                    const frameUrl = URL.createObjectURL(frameBlob);
                    webcamStream.src = frameUrl;

                    // Update results
                    const detections = data.detections || [];
                    updateWebcamResults(detections);
                }
            })
            .catch(error => console.error('Stream error:', error));
        }, 'image/jpeg', 0.8);
    }, 500); // Send frames every 500ms
}

/**
 * Update results from webcam detection
 */
function updateWebcamResults(detections) {
    // Update quick stats
    document.getElementById('totalDetections').textContent = detections.length;
    
    const personDetections = detections.filter(d => d.class === 'person');
    document.getElementById('personCount').textContent = personDetections.length;
    
    const avgConfidence = detections.length > 0
        ? (detections.reduce((sum, d) => sum + d.confidence, 0) / detections.length * 100).toFixed(1)
        : '0';
    document.getElementById('avgConfidence').textContent = avgConfidence + '%';

    // Show results
    resultsContent.classList.add('show');
    emptyState.style.display = 'none';
}

/**
 * Stop webcam stream
 */
function stopWebcam() {
    state.webcamActive = false;

    if (state.webcamStream) {
        state.webcamStream.getTracks().forEach(track => track.stop());
    }

    if (state.webcamIntervalId) {
        clearInterval(state.webcamIntervalId);
    }

    // Reset UI
    webcamPlaceholder.style.display = 'flex';
    webcamStream.style.display = 'none';
    startWebcamBtn.style.display = 'block';
    stopWebcamBtn.style.display = 'none';

    showAlert('Webcam stopped', 'info');
}

// ======================== Utilities ========================

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert show alert-${type}`;
    alert.textContent = message;
    alertContainer.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Load model information
 */
async function loadModelInfo() {
    try {
        const response = await fetch('/api/model-info');
        const data = await response.json();
        
        const modelInfoDiv = document.getElementById('modelInfo');
        modelInfoDiv.innerHTML = `
            <div>Model: ${data.model_name}</div>
            <div>Task: ${data.task}</div>
            <div>Threshold: ${data.threshold}</div>
            <div>Classes: ${data.classes.join(', ')}</div>
        `;
    } catch (error) {
        console.error('Error loading model info:', error);
    }
}

// ======================== Initialization ========================

document.addEventListener('DOMContentLoaded', () => {
    loadModelInfo();
    
    // Set initial threshold display
    thresholdValue.textContent = state.threshold.toFixed(2);
    
    console.log('Violence Detection AI - Frontend loaded');
});
