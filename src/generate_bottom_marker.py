import cv2
import cv2.aruco as aruco
import numpy as np

def generate_bottom_marker():
    """Generates the Bottom Marker (ID 99)."""
    # Define dictionary
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    
    # ID 99 is not in DICT_4X4_50 (0-49). We need a larger dictionary or just use max ID.
    # DICT_4X4_50 only has 50 markers (0-49).
    # Let's switch to DICT_4X4_100 or DICT_4X4_250 for ID 99.
    # However, the detection script parses 4X4_50. 
    # If we change dictionary here, we MUST change it in detection script too.
    # Let's use ID 49 (Last one of 4x4_50) as "Bottom Marker" to avoid changing dictionary globally?
    # Or just switch global dictionary to DICT_4X4_100.
    
    # User asked for "ID 99". I should use DICT_4X4_100.
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
    
    marker_id = 99
    marker_size_px = 200
    
    img = aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
    
    # Add White Border (Quiet Zone)
    border_size = 50
    img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, 
                             cv2.BORDER_CONSTANT, value=255) # White

    save_path = f"marker_bottom_id{marker_id}.png"
    cv2.imwrite(save_path, img)
    print(f"[SUCCESS] Saved '{save_path}'.")
    print("NOTE: Ensure detection script uses DICT_4X4_100 or compatible dictionary.")

if __name__ == "__main__":
    generate_bottom_marker()
