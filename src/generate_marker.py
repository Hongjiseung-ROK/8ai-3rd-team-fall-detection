import cv2
import cv2.aruco as aruco
import os

def generate_marker():
    """Generates an ArUco marker image."""
    # Define dictionary - using 4x4 marker
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    
    # Generate marker (ID=0, 200x200 pixels)
    # 0 is the ID, 200 is the size in pixels
    img = aruco.generateImageMarker(aruco_dict, 0, 200)
    
    # CRITICAL: Add a white border (Quiet Zone) around the marker
    # ArUco detection fails if the black border merges with a dark screen background.
    border_size = 50
    img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, 
                             cv2.BORDER_CONSTANT, value=255) # 255 is White

    
    # Save the marker
    save_path = "marker_id0.png"
    cv2.imwrite(save_path, img)
    print(f"[SUCCESS] Saved '{save_path}'. Open this image on your phone or print it.")

if __name__ == "__main__":
    generate_marker()
