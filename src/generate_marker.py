import cv2
import cv2.aruco as aruco
import os

def generate_marker():
    """Generates an ArUco marker image."""
    # Define dictionary - using 4x4 marker
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    
    # Generate markers for ID 0 and ID 1
    ids_to_generate = [0, 1]
    
    for marker_id in ids_to_generate:
        # Generate marker (200x200 pixels)
        img = aruco.generateImageMarker(aruco_dict, marker_id, 200)
        
        # CRITICAL: Add a white border (Quiet Zone) around the marker
        border_size = 50
        img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, 
                                 cv2.BORDER_CONSTANT, value=255) # 255 is White

        # Save the marker
        save_path = f"marker_id{marker_id}.png"
        cv2.imwrite(save_path, img)
        print(f"[SUCCESS] Saved '{save_path}'.")


if __name__ == "__main__":
    generate_marker()
