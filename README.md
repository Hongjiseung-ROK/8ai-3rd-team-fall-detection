# 8ai-3rd-team-fall-detection

## 3D Fall Detection System with ArUco Markers

This project transforms a standard webcam into an intelligent 3D fall detection sensor using OpenCV and ArUco markers.

### Features
- **Real-time Detection**: Tracks ArUco markers (ID 0 & 1).
- **Multi-Class Recognition**: Identifies different targets ("Target A", "Target B") based on marker ID.
- **3D Pose Estimation**: Calculates the tilt angle of the marker in 3D space.
- **Fall Alert**: Triggers a visual "FALL DETECTED" alert if the angle exceeds 45 degrees.
- **Robustness**: Includes a "Quiet Zone" (white border) generator for reliable detection on screens or paper.

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. **Generate the Markers**:
   ```bash
   python src/generate_marker.py
   ```
   This saves `marker_id0.png` and `marker_id1.png`. Print these images or display them on a phone.

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
