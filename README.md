# 8ai-3rd-team-fall-detection

## 3D Fall Detection System with ArUco Markers

This project transforms a standard webcam into an intelligent 3D fall detection sensor using OpenCV and ArUco markers.

### Features
- **Real-time Detection**: Tracks ArUco markers (ID 0 & 1) and **Cylindrical Marker Strips**.
- **Cylindrical Surface Tracking**: Uses a multi-marker strip approach to detect falls for curved objects (no blind spots).
- **Bottom Marker Detection**: Immediately triggers a fall alert if the bottom marker (ID 99) is visible.
- **Parametric Generator**: Automatically generates marker strips based on cylinder diameter input.
- **Precise Printing**: Generates A4 PDFs with exact physical dimensions (mm) for accurate tracking.
- **3D Pose Estimation**: Calculates the tilt angle of markers in 3D space.
- **System Monitoring**: Displays real-time RAM usage.
- **Robustness**: Includes a "Quiet Zone" (white border) generator for reliable detection.

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### 1. Cylindrical Object Tracking (Recommended)
This method is best for bottles, cans, or any cylindrical container.

**Step 1: Generate Marker Strip**
```bash
python src/generate_cylinder_marker.py
```
- Enter the diameter of your object (e.g., `60` for 60mm).
- Enter the desired marker size (e.g., `15` for 15mm).
- This creates a `strip_dXXmm.png` file.

**Step 2: Generate Bottom Marker (Optional)**
```bash
python src/generate_bottom_marker.py
```
- Creates `marker_bottom_id99.png`. Attach this to the bottom of the object.

**Step 3: Create Printable PDF**
```bash
python src/generate_print_pdf.py
```
- follow the prompts to create a precise A4 PDF (`print_strip_...pdf`) for printing.
- **Important**: Print with "Actual Size" (100% scale).

**Step 4: Run Detection**
```bash
python src/cylinder_fall_detection.py
```
- Monitors the object. If it tilts > 45 degrees OR the bottom marker is seen, it alerts "FALL DETECTED".

#### 2. Basic Single Marker Tracking
Legacy mode for flat surfaces.
```bash
python src/generate_marker.py
python src/fall_detection.py
```

### Requirements
- Python 3.x
- Webcam
- `opencv-contrib-python`
- `numpy`
- `fpdf` (For PDF generation)
- `psutil` (For system monitoring)
