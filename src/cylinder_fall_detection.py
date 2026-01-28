import cv2
import cv2.aruco as aruco
import numpy as np
import psutil
import os
import time
import datetime
import requests
import json
import threading
from collections import deque
from db_logger import AzureDBLogger

LOGIC_APP_URL = "https://prod-28.koreacentral.logic.azure.com:443/workflows/96cca591f739451d92d2396e05a0043e/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=qBBbUmM-wA7lu_4C1TfEpcUzlWUW4Co3FEkUSQJSyTo"

def calculate_angle(rvec):
    """
    Calculates the angle between the marker's Y-axis and the camera's Y-axis (vertical).
    Returns the angle in degrees.
    """
    try:
        # 1. Convert Rotation Vector to Rotation Matrix
        R, _ = cv2.Rodrigues(rvec)
        
        # 2. Extract Marker's Y-axis (The 'Up' direction of the sticker)
        marker_y = R[:, 1]
        
        # 3. Define Camera's Vertical Axis (Assuming camera is upright)
        camera_up = np.array([0, -1, 0])
        
        # 4. Compute Angle using Dot Product
        dot_prod = np.dot(marker_y, camera_up)
        norm_m = np.linalg.norm(marker_y)
        norm_c = np.linalg.norm(camera_up)
        
        # Calculate cosine and clamp value to [-1, 1] to prevent NaN errors
        cos_theta = np.clip(dot_prod / (norm_m * norm_c), -1.0, 1.0)
        
        # Convert to degrees
        angle = np.degrees(np.arccos(cos_theta))
        return angle
        
    except Exception as e:
        print(f"[ERROR] Logic error in angle calculation: {e}")
        return 0.0

def main():
    # --- Configuration ---
    MARKER_SIZE = 0.015  # 1.5cm 
    FALL_THRESHOLD = 45 # Degrees to consider as "Fallen"
    LOG_COOLDOWN = 2.0 # Seconds between DB logs
    CAMERA_ID = "Cylinder_Cam_01"
    
    # [NEW] Generate or Input Experiment ID at startup
    # This groups all logs from this specific run
    current_experiment_id = f"EXP_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
    print(f"[INFO] Current Experiment ID: {current_experiment_id}")

    # --- Database Setup ---
    print("[INFO] Connecting to Database...")
    db = AzureDBLogger()
    last_log_time = 0
    
    # --- Stabilization ---
    angle_buffer = deque(maxlen=5) # Averaging over 5 frames
    
    # --- Camera Setup ---
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return

    # Set resolution
    width, height = 640, 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # --- Approximate Calibration ---
    focal_length = width 
    center = (width/2, height/2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )
    dist_coeffs = np.zeros((4,1)) 
    
    # --- ArUco Setup ---
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
    parameters = aruco.DetectorParameters()

    print(f"[INFO] Cylinder Monitor started. Target: Any marker in strip OR Bottom (ID 99). Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Initialize Frame Variables
        fall_detected = False
        bottom_detected = False
        duration = 0.0
        max_angle = 0
        
        # Detect Markers
        corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        
        if ids is not None:
            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, MARKER_SIZE, camera_matrix, dist_coeffs)
            
            # Draw all markers first
            cv2.aruco.drawDetectedMarkers(frame, corners)
            
            for i in range(len(ids)):
                detected_id = ids[i][0]
                
                # Draw Axis (Short length to avoid warnings)
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.01)
                
                # Check for Bottom Marker (ID 99)
                if detected_id == 99:
                    fall_detected = True
                    bottom_detected = True
                    cv2.putText(frame, "BOTTOM DETECTED", (int(corners[i][0][0][0]), int(corners[i][0][0][1])), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                    continue 
                
                # Check tilt for normal markers
                angle = calculate_angle(rvecs[i])
                
                # --- Stabilization Logic ---
                angle_buffer.append(angle)
                avg_angle = sum(angle_buffer) / len(angle_buffer)
                
                max_angle = max(max_angle, avg_angle)
                
                if avg_angle > FALL_THRESHOLD:
                    fall_detected = True
            
        # --- Fall Duration & Logging Logic ---
        if fall_detected:
            if getattr(main, 'fall_start_time', None) is None:
                main.fall_start_time = time.time()
            
            duration = time.time() - main.fall_start_time
            
            if bottom_detected:
               status = "FALL (Bottom)"
               log_angle = 90.0
            else:
               status = f"FALLING ({duration:.1f}s)"
               log_angle = max_angle

            color = (0, 0, 255) # Red
            
            # REQUIREMENT: Log only after 2 seconds of continuous fall
            if duration >= 2.0 or bottom_detected:
                current_time = time.time()
                if current_time - last_log_time > LOG_COOLDOWN:
                    msg = f"[INFO] Confirmed Fall. Logging to DB. Angle: {int(log_angle)}deg"
                    print(msg)
                    
                    # --- Local File Logging ---
                    try:
                        with open("local_fall_log.txt", "a") as f:
                            f.write(f"{datetime.datetime.now()} - CONFIRMED FALL - {int(log_angle)}deg\n")
                        print("[LOCAL] Saved to local_fall_log.txt")
                    except Exception as e:
                        print(f"[LOCAL ERROR] {e}")
                        
                    # --- DB Logging ---
                    db.log_event(CAMERA_ID, log_angle, "FALL_CONFIRMED", current_experiment_id)
                    last_log_time = current_time
                    
                    # --- Logic App Webhook (Async) ---
                    def send_webhook_async(payload):
                        try:
                            headers = {'Content-Type': 'application/json'}
                            # Increased timeout to 30s as Logic App workflow might be slow for real events
                            response = requests.post(LOGIC_APP_URL, json=payload, headers=headers, timeout=30.0)
                            print(f"[WEBHOOK] Sent. Status: {response.status_code} | Body: {response.text}")
                        except Exception as e:
                            print(f"[WEBHOOK ERROR] {e}")

                    payload = {
                        "Timestamp": datetime.datetime.utcnow().isoformat()[:-3] + 'Z',
                        "CameraID": CAMERA_ID,
                        "RiskAngle": round(float(log_angle), 2),
                        "Status": "FALL_CONFIRMED"
                    }
                    
                    # Run in a separate thread to avoid blocking the video feed
                    threading.Thread(target=send_webhook_async, args=(payload,), daemon=True).start()
                        
                    last_log_time = current_time
        else:
            main.fall_start_time = None
            status = "Standing"
            color = (0, 255, 0) # Green
            
        # --- High-Frequency Debug Logging (0.1s interval) ---
        if time.time() - getattr(main, 'last_csv_log', 0) > 0.1:
            d_detected = 1 if fall_detected else 0
            d_markers = len(ids) if ids is not None else 0
            d_raw = int(max_angle)
            
            log_line = f"{datetime.datetime.now().strftime('%H:%M:%S.%f')},{d_markers},{d_raw},{d_detected},{duration:.2f}\n"
            
            try:
                with open("debug_stream.csv", "a") as f:
                    if os.path.getsize("debug_stream.csv") == 0:
                        f.write("Time,Markers,Angle,FallDetected,Duration\n")
                    f.write(log_line)
            except:
                pass
            main.last_csv_log = time.time()

        # --- Status Display ---
        cv2.putText(frame,f"Status: {status} (Angle: {int(max_angle)})", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # [DEBUG] Heartbeat (Unconditional)
        if time.time() - getattr(main, 'last_debug_print', 0) > 1.0:
            d_markers = len(ids) if ids is not None else 0
            print(f"[STATUS] Markers: {d_markers}, MaxAngle: {int(max_angle)}, FallDetected: {fall_detected}, Timer: {duration:.1f}s", flush=True)
            main.last_debug_print = time.time()
            
        # Monitor RAM Usage
        process = psutil.Process(os.getpid())
        ram_usage_mb = process.memory_info().rss / (1024 * 1024)
        ram_text = f"RAM: {ram_usage_mb:.1f} MB"
        text_size = cv2.getTextSize(ram_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = width - text_size[0] - 10
        text_y = height - 10
        cv2.putText(frame, ram_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Cylinder Fall Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
