"""
Violence Detection System - Flask Application
Production-ready implementation with authentication and video processing
"""

import os
import cv2
import logging
import json
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

import numpy as np
from flask import (
    Flask, render_template, request, jsonify, session, 
    redirect, url_for, Response
)
from werkzeug.security import check_password_hash, generate_password_hash
from ultralytics import YOLO

# ======================== Configuration ========================

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# ======================== Logging Setup ========================

log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ======================== Model Loading ========================

try:
    model = YOLO("runs/detect/mall_yolov8/weights/best.pt")
    logger.info("YOLOv8 model loaded successfully")
except FileNotFoundError:
    logger.warning("Trained model not found. Using pretrained YOLOv8n model")
    model = YOLO("yolov8n.pt")

# ======================== Credentials (In Production: Use Database) ========================

USERS = {
    'admin': generate_password_hash('admin123'),
    'user': generate_password_hash('user123')
}

DETECTION_THRESHOLD = 0.5  # Confidence threshold for detections

# ======================== Decorators ========================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ======================== Authentication Routes ========================

@app.route('/')
def index():
    """Redirect to login if not authenticated, else to home page"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    """Home page after login"""
    logger.info(f"User '{session.get('user_id')}' accessed home page")
    return render_template('index.html', username=session.get('user_id'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # Input validation
        if not username or not password:
            logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
            return jsonify({'success': False, 'message': 'Username and password required'}), 400

        # Check credentials
        if username in USERS and check_password_hash(USERS[username], password):
            session.permanent = True
            session['user_id'] = username
            logger.info(f"User '{username}' logged in from {request.remote_addr}")
            return jsonify({'success': True, 'redirect': url_for('home')}), 200
        else:
            logger.warning(f"Failed login attempt for user '{username}' from {request.remote_addr}")
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    username = session.get('user_id', 'unknown')
    session.clear()
    logger.info(f"User '{username}' logged out")
    return redirect(url_for('login'))

# ======================== Detection Routes ========================

@app.route('/detection')
@login_required
def detection():
    """Main detection interface"""
    logger.info(f"User '{session.get('user_id')}' accessed detection page")
    return render_template('detection.html', 
                         username=session.get('user_id'),
                         threshold=DETECTION_THRESHOLD)

@app.route('/api/detect', methods=['POST'])
@login_required
def detect_objects():
    """
    Process uploaded video/image and perform object detection
    
    Expected form data:
    - 'file': uploaded file (video or image)
    - 'source': 'upload', 'webcam', or 'rtsp_stream'
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        file = request.files['file']
        source = request.form.get('source', 'upload')

        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        # Validate file type
        allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file type: {file_ext} from user {session.get('user_id')}")
            return jsonify({'success': False, 'message': 'Invalid file format'}), 400

        # Save temporary file
        temp_path = f"temp_{datetime.now().timestamp()}_{file.filename}"
        file.save(temp_path)

        try:
            # Run detection
            results = model.predict(
                source=temp_path,
                conf=DETECTION_THRESHOLD,
                save=False,
                verbose=False
            )

            # Process results
            detections = []
            for result in results:
                if result.boxes is not None:
                    for box, conf, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                        detections.append({
                            'class': result.names[int(cls)],
                            'confidence': float(conf),
                            'bbox': [float(x) for x in box.tolist()]
                        })

            logger.info(f"Detection completed: {len(detections)} objects found by {session.get('user_id')}")
            
            return jsonify({
                'success': True,
                'detections': detections,
                'frame_count': len(results),
                'timestamp': datetime.now().isoformat()
            }), 200

        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Error in detection: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Detection failed'}), 500

@app.route('/api/video-feed')
@login_required
def video_feed():
    """Stream video feed with real-time detection"""
    try:
        source = request.args.get('source', '0')  # '0' for webcam, or file path
        
        # Convert source to appropriate format
        if source == '0':
            source = 0  # Webcam
        elif not source.isdigit():
            source = str(source)  # File path or RTSP stream

        def generate():
            """Generator function for video frames"""
            cap = cv2.VideoCapture(source)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video source: {source}")
                yield b'Failed to open video source'
                return

            logger.info(f"Video stream started from {source} by {session.get('user_id')}")
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        logger.info(f"Video stream ended for {session.get('user_id')}")
                        break

                    # Resize for processing efficiency
                    frame = cv2.resize(frame, (640, 480))

                    # Run detection
                    results = model.predict(frame, conf=DETECTION_THRESHOLD, verbose=False)
                    
                    # Draw bounding boxes
                    annotated_frame = results[0].plot()

                    # Encode frame
                    ret, buffer = cv2.imencode('.jpg', annotated_frame)
                    frame_bytes = buffer.tobytes()

                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n'
                           b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                           + frame_bytes + b'\r\n')

            except Exception as e:
                logger.error(f"Error in video stream: {str(e)}", exc_info=True)
            finally:
                cap.release()

        return Response(generate(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')

    except Exception as e:
        logger.error(f"Video feed error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Video feed error'}), 500

@app.route('/api/model-info')
@login_required
def model_info():
    """Get model information"""
    return jsonify({
        'model_name': model.model_name if hasattr(model, 'model_name') else 'YOLOv8',
        'task': 'Detection',
        'threshold': DETECTION_THRESHOLD,
        'classes': list(model.names.values()) if hasattr(model, 'names') else []
    }), 200

# ======================== Error Handlers ========================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path} from {request.remote_addr}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(403)
def forbidden(e):
    """Handle 403 errors"""
    logger.warning(f"403 error from {request.remote_addr}")
    return redirect(url_for('login'))

# ======================== CLI Commands ========================

@app.cli.command()
def init_db():
    """Initialize default users (development only)"""
    print("✓ Users initialized:")
    print("  - admin / admin123")
    print("  - user / user123")
    print("\n⚠️  Change these credentials in production!")

# ======================== Application Entry Point ========================

if __name__ == '__main__':
    logger.info("Starting Violence Detection System")
    
    # Production: Use gunicorn or waitress
    # Development: Use Flask development server
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=os.environ.get('FLASK_ENV') == 'development',
        use_reloader=False
    )
