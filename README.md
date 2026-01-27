# 8ai-3rd-team-fall-detection

## 3D Fall Detection System with ArUco Markers

This project transforms a standard webcam into an intelligent 3D fall detection sensor using OpenCV and ArUco markers.

### Features
- **Real-time Detection**: Tracks a 4x4 ArUco marker (ID 0).
- **3D Pose Estimation**: Calculates the tilt angle of the marker in 3D space.
- **Fall Alert**: Triggers a visual "FALL DETECTED" alert if the angle exceeds 45 degrees.
- **Robustness**: Includes a "Quiet Zone" (white border) generator for reliable detection on screens or paper.

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Generate the Marker**:
   ```bash
   python src/generate_marker.py
   ```
   This saves `marker_id0.png`. Print this image or display it on a phone.

2. **Run the Sensor**:
   ```bash
   python src/fall_detection.py
   ```
   Point the webcam at the marker.

### Requirements
- Python 3.x
- Webcam
- `opencv-contrib-python`
- `numpy`
