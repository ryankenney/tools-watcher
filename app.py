from flask import Flask, jsonify, send_from_directory, request, Response
import cv2
import numpy as np
from datetime import datetime
import sqlite3

app = Flask(__name__, static_folder='menu-app/build')

camera = cv2.VideoCapture(0)

historical_frames = {
    "ten_seconds": {"frame": None, "timestamp": None},
    "one_minute": {"frame": None, "timestamp": None},
    "one_hour": {"frame": None, "timestamp": None},
    "one_day": {"frame": None, "timestamp": None},
    "one_week": {"frame": None, "timestamp": None},
    "one_month": {"frame": None, "timestamp": None},
}

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("images.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        timestamp TEXT,
        image BLOB
    );
    """)
    conn.commit()
    conn.close()

def update_historical_frames(frame):
    now = datetime.now()
    for period, data in historical_frames.items():
        # Check if it's time to update the frame for each period
        if period == "ten_seconds" and (data['timestamp'] is None or now.second % 10 == 0):
            historical_frames[period]['frame'] = frame.copy()
            historical_frames[period]['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        elif period == "one_minute" and (data['timestamp'] is None or now.minute != datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S").minute):
            historical_frames[period]['frame'] = frame.copy()
            historical_frames[period]['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        elif period == "one_hour" and (data['timestamp'] is None or now.hour != datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S").hour):
            historical_frames[period]['frame'] = frame.copy()
            historical_frames[period]['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        elif period == "one_day" and (data['timestamp'] is None or now.day != datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S").day):
            historical_frames[period]['frame'] = frame.copy()
            historical_frames[period]['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        elif period == "one_week" and (data['timestamp'] is None or now.isocalendar()[1] != datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S").isocalendar()[1]):
            historical_frames[period]['frame'] = frame.copy()
            historical_frames[period]['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        elif period == "one_month" and (data['timestamp'] is None or now.month != datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S").month):
            historical_frames[period]['frame'] = frame.copy()
            historical_frames[period]['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")

def generate_grid():
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        update_historical_frames(frame)

        grid_frames = []
        for period, data in historical_frames.items():
            ref_frame = data['frame']
            timestamp = data['timestamp']
            description = period.replace("_", " ").capitalize()
            
            if ref_frame is None:
                grid_frame = np.zeros_like(frame)
            else:
                # Calculate absolute difference
                difference = cv2.absdiff(frame, ref_frame)
                gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

                # Thresholding to create a binary image
                ret, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Draw bounding boxes around contours
                grid_frame = frame.copy()
                for contour in contours:
                    if cv2.contourArea(contour) > 100:  # Threshold to filter small changes
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(grid_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Add timestamp
                cv2.putText(grid_frame, timestamp, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Add description
                cv2.putText(grid_frame, description, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            resized_frame = cv2.resize(grid_frame, (0, 0), fx=0.5, fy=0.5)
            grid_frames.append(resized_frame)

        # Combine into a 2x3 grid
        top_row = np.hstack(grid_frames[0:3])
        bottom_row = np.hstack(grid_frames[3:6])
        combined_grid = np.vstack([top_row, bottom_row])

        ret, buffer = cv2.imencode('.jpg', combined_grid)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return send_from_directory('/app/menu-app/build', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('/app/menu-app/build', filename)

@app.route('/hello')
def hello():
    return "Hello, World!"

@app.route('/video_grid')
def video_grid():
    return Response(generate_grid(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/reference_images', methods=['POST'])
def save_reference_image():
    try:
        name = request.form.get("name")  # Getting the 'name' field from POST request
        
        if not name:
            return jsonify({"status": "error", "message": "Name is required"})

        # Check if the webcam is opened correctly
        if not camera.isOpened():
            return jsonify({"status": "error", "message": "Could not open webcam"})

        # Capture a single frame
        ret, frame = camera.read()

        if not ret:
            return jsonify({"status": "error", "message": "Failed to capture image"})

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Convert image to binary data
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_binary = img_encoded.tobytes()

        # Insert name, timestamp, and image into the SQLite database
        conn = sqlite3.connect("images.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO images (name, timestamp, image) VALUES (?, ?, ?)", (name, timestamp, img_binary))
        conn.commit()
        conn.close()

        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/reference_images', methods=['GET'])
def get_reference_images():
    try:
        conn = sqlite3.connect("images.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, timestamp FROM images")
        
        images = []
        for row in cursor.fetchall():
            record_id, name, timestamp = row
            images.append({
                'id': record_id,
                'name': name,
                'timestamp': timestamp
            })
        
        conn.close()
        return jsonify(images)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port='5000')
