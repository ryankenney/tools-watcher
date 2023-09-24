from flask import Flask, jsonify, send_from_directory, request, Response
import cv2
import numpy as np
from datetime import datetime
import sqlite3

app = Flask(__name__, static_folder='menu-app/build')

camera = cv2.VideoCapture(0)

database_path = "/db/database.sqlite"
memory_conn = None

# Initialize SQLite Database
def init_db():
    global memory_conn

    # Connect to disk-based database and in-memory database
    disk_conn = sqlite3.connect(database_path)
    memory_conn = sqlite3.connect("file::memory:?cache=shared", check_same_thread=False,     uri=True)

    # Create table if not exists in disk-based database
    cursor = disk_conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        timestamp TEXT,
        image BLOB
    );
    """)
    disk_conn.commit()

    # Copy data from disk-based database to in-memory database
    disk_conn.backup(memory_conn)

    disk_conn.close()

# Function to persist in-memory DB changes to disk-based DB
def persist_to_disk():
    global memory_conn

    disk_conn = sqlite3.connect(database_path)
    memory_conn.backup(disk_conn)
    disk_conn.close()

@app.route('/')
def index():
    return send_from_directory('/app/menu-app/build', 'index.html')

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('/app/menu-app/build', filename)

@app.route('/hello')
def hello():
    return "Hello, World!"

@app.route('/reference_images', methods=['POST'])
def save_reference_image():
    global memory_conn
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
        cursor = memory_conn.cursor()
        cursor.execute("INSERT INTO images (name, timestamp, image) VALUES (?, ?, ?)", (name, timestamp, img_binary))
        memory_conn.commit()

        persist_to_disk()

        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/reference_images', methods=['GET'])
def get_reference_images():
    global memory_conn
    try:
        cursor = memory_conn.cursor()
        cursor.execute("SELECT id, name, timestamp FROM images")
        
        images = []
        for row in cursor.fetchall():
            record_id, name, timestamp = row
            images.append({
                'id': record_id,
                'name': name,
                'timestamp': timestamp
            })
        
        memory_conn.commit()
        return jsonify(images)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/reference_images', methods=['DELETE'])
def delete_reference_image():
    global memory_conn
    try:
        id = request.args.get("id")
        
        if not id:
            return jsonify({"status": "error", "message": "ID is required"})
        
        cursor = memory_conn.cursor()
        cursor.execute("DELETE FROM images WHERE id = ?", (id,))
        memory_conn.commit()

        persist_to_disk()

        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/diff', methods=['GET'])
def video_diff():
    reference_image_id = request.args.get('reference_image_id')
    if not reference_image_id:
        return "reference_image_id is required", 400

    # Fetch reference image from the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM images WHERE id = ?", (reference_image_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return "Reference image not found", 404
    reference_image_data = np.frombuffer(row[0], dtype=np.uint8)
    reference_image = cv2.imdecode(reference_image_data, cv2.IMREAD_COLOR)

    def generate():
        while True:
            ret, frame = camera.read()
            if not ret:
                break

            # Compute difference and draw bounding boxes
            diff = cv2.absdiff(reference_image, frame)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) < 500:
                    continue
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port='5000')
