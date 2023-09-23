from flask import Flask, Response
import cv2
import time
from collections import deque

app = Flask(__name__)
camera = cv2.VideoCapture(0)  # 0 is the index for the default webcam

# Deque to act as a circular buffer to hold last N frames and their capture times
frame_buffer = deque(maxlen=300)  # Assuming 30 fps, this holds the last 10-second worth of frames

def generate():
    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()
        if not ret:
            break
        else:
            current_time = time.time()
            frame_buffer.append((frame.copy(), current_time))  # Store a copy of the original frame

            # Find the frame captured closest to 10 seconds ago
            ref_time = current_time - 10
            ref_frame = None
            for old_frame, old_time in reversed(frame_buffer):
                if old_time <= ref_time:
                    ref_frame = old_frame
                    break

            # If we have a reference frame, highlight differences
            output_frame = frame.copy()  # Create a copy for highlighting differences
            if ref_frame is not None:
                difference = cv2.absdiff(frame, ref_frame)
                gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
                ret, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
                output_frame[thresh != 0] = [0, 0, 255]  # Highlight differences in red

            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Concatenate image frame bytes and return them in a HTTP response

@app.route('/')
def index():
    return "Webcam Feed"

@app.route('/video')
def video():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_diff')
def video_diff():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
