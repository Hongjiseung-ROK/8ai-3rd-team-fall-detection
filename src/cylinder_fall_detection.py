import cv2
import cv2.aruco as aruco
import numpy as np
import psutil
import os

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
    MARKER_SIZE = 0.015  # 1.5cm (Must match usage in generate_cylinder_marker.py)
    FALL_THRESHOLD = 45 # Degrees to consider as "Fallen"
    
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
    # Use DICT_4X4_100 to support ID 99
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
    parameters = aruco.DetectorParameters()

    print(f"[INFO] Cylinder Monitor started. Target: Any marker in strip OR Bottom (ID 99). Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect Markers
        corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        
        if ids is not None:
            rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, MARKER_SIZE, camera_matrix, dist_coeffs)
            
            fall_detected = False
            bottom_detected = False
            max_angle = 0
            
            # Draw all markers first
            cv2.aruco.drawDetectedMarkers(frame, corners)
            
            for i in range(len(ids)):
                detected_id = ids[i][0]
                
                # Draw Axis
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.02)
                
                # Check for Bottom Marker (ID 99)
                if detected_id == 99:
                    fall_detected = True
                    bottom_detected = True
                    cv2.putText(frame, "BOTTOM DETECTED", (int(corners[i][0][0][0]), int(corners[i][0][0][1])), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                    continue # Skip angle check for bottom marker
                
                # Check tilt for normal markers
                angle = calculate_angle(rvecs[i])
                max_angle = max(max_angle, angle)
                
                if angle > FALL_THRESHOLD:
                    fall_detected = True
                    # Optimization: If one is fallen, the object is fallen.
                    # But we continue loop to draw all axes if needed, or break if performance is key.
            
            # --- Status Display ---
            if fall_detected:
                status = "FALL DETECTED!"
                color = (0, 0, 255) # Red
            else:
                status = "Standing"
                color = (0, 255, 0) # Green
            
            # Display overall status at the top of the screen
            cv2.putText(frame,f"Status: {status} (Max Tilt: {int(max_angle)} deg)", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Monitor RAM Usage
        process = psutil.Process(os.getpid())
        ram_usage_mb = process.memory_info().rss / (1024 * 1024)
        
        # Display RAM usage at bottom right
        ram_text = f"RAM: {ram_usage_mb:.1f} MB"
        text_size = cv2.getTextSize(ram_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        text_x = width - text_size[0] - 10
        text_y = height - 10
        
        cv2.putText(frame, ram_text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Cylinder Fall Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
