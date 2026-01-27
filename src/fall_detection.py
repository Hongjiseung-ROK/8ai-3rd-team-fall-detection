import cv2
import cv2.aruco as aruco
import numpy as np
import time

def calculate_angle(rvec):
    """
    Calculates the angle between the marker's Y-axis and the camera's Y-axis (vertical).
    Returns the angle in degrees.
    """
    try:
        # 1. Convert Rotation Vector to Rotation Matrix
        R, _ = cv2.Rodrigues(rvec)
        
        # 2. Extract Marker's Y-axis (The 'Up' direction of the sticker)
        # In the marker's local coordinate system, Y-axis is [0, 1, 0]
        # R * [0, 1, 0]^T corresponds to the second column of R.
        marker_y = R[:, 1]
        
        # 3. Define Camera's Vertical Axis (Assuming camera is upright)
        # In OpenCV, pure Y-axis points downwards from top-left.
        # However, for a user facing the camera, 'Up' in the world usually corresponds to the negative Y of the image plane 
        # (or depending on how they conceptualize "Up").
        # Let's stick to the plan: Camera's "Up" is [0, -1, 0] (Opposite to image Y-axis).
        camera_up = np.array([0, -1, 0])
        
        # 4. Compute Angle using Dot Product
        dot_prod = np.dot(marker_y, camera_up)
        norm_m = np.linalg.norm(marker_y)
        norm_c = np.linalg.norm(camera_up)
        
        # Calculate cosine and clamp value to [-1, 1] to prevent NaN errors due to float precision
        cos_theta = np.clip(dot_prod / (norm_m * norm_c), -1.0, 1.0)
        
        # Convert to degrees
        angle = np.degrees(np.arccos(cos_theta))
        return angle
        
    except Exception as e:
        print(f"[ERROR] Logic error in angle calculation: {e}")
        return 0.0

def main():
    # --- Configuration ---
    MARKER_SIZE = 0.05  # 5cm
    FALL_THRESHOLD = 45 # Degrees
    
    # --- Class Definitions ---
    # Customize these labels as needed
    MARKER_CLASSES = {
        0: "Target A (Normal)",
        1: "Target B (Special)"
    }

    
    # --- Camera Setup ---
    # Attempt to open the default camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # CAP_DSHOW often helps with faster startup on Windows
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Could not open webcam.")
            return

    # Set resolution (Lower resolution is faster and sufficient for this)
    width = 640
    height = 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # --- Approximate Calibration ---
    # Focal length ~ Width of image helps for a decent approximation without full calibration
    focal_length = width 
    center = (width/2, height/2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )
    dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
    
    # --- ArUco Setup ---
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()

    print(f"[INFO] Camera started ({width}x{height}). Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Failed to read frame")
                break
                
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect Markers
            corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
            if ids is not None:
                # Estimate Pose for all detected markers
                # estimatePoseSingleMarkers returns: rvecs, tvecs, _objPoints
                rvecs, tvecs, _ = aruco.estimatePoseSingleMarkers(corners, MARKER_SIZE, camera_matrix, dist_coeffs)
                
                for i, marker_id in enumerate(ids):
                    # Draw ID and Border
                    cv2.aruco.drawDetectedMarkers(frame, corners)
                    
                    # Draw Axis (X: Red, Y: Green, Z: Blue). length 0.03 meters -> 3cm
                    cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], 0.03)
                    
                    # Calculate Tilt Angle
                    angle = calculate_angle(rvecs[i])
                    
                    # Visual Logic for Fall Detection
                    if angle > FALL_THRESHOLD:
                        status = f"FALL DETECTED! ({int(angle)} deg)"
                        text_color = (0, 0, 255) # Red
                    else:
                        status = f"Stable ({int(angle)} deg)"
                        text_color = (0, 255, 0) # Green
                    
                    # Get Class Label
                    # marker_id is a numpy array (e.g. [0]), need scalar for dict lookup
                    cur_id = marker_id[0]
                    label = MARKER_CLASSES.get(cur_id, f"Unknown ID {cur_id}")
                    
                    # Display Text on Screen
                    # Line 1: Class Label
                    # Line 2: Status
                    top_left = corners[i][0][0]
                    text_pos_x = int(top_left[0])
                    base_y = int(top_left[1]) - 10
                    
                    cv2.putText(frame, f"[{label}]", (text_pos_x, max(20, base_y - 25)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)  # Cyan for Label
                                
                    cv2.putText(frame, status, (text_pos_x, max(45, base_y)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

                    
                    # Print to console occasionally or if status changes could be done here, 
                    # but kept silent for performance as requested.
            
            # Show result
            cv2.imshow("Real-time Fall Detection", frame)
            
            # Exit loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("[INFO] Interrupted by user.")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Resources released.")

if __name__ == "__main__":
    main()
