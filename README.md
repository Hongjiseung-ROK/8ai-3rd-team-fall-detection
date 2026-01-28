# Cylinder Fall Detection System

A robust computer vision system designed to detect fall events for cylindrical objects using ArUco markers. This project integrates real-time detection with Azure SQL Database logging and Azure Logic App alerts, featuring a verification workflow for Responsible AI.

## Key Features

*   **Cylindrical Object Tracking:** Uses a strip of ArUco markers to detect tilt from any angle.
*   **Robust Fall Detection Logic:**
    *   **Angle Smoothing:** Uses a moving average filter to reduce sensor noise.
    *   **2-Second Hold Verification:** Requires a continuous "fallen" state for 2.0 seconds to prevent false alarms from flickering.
    *   **Bottom Marker Trigger:** Immediate fall detection if the bottom marker (ID 99) is visible.
*   **Dual Logging System:**
    *   **Azure SQL Database:** Stores structured event data (`FallEvents` table) with `ExperimentID` and `VerificationStatus`.
    *   **Local Fallback Log:** Writes to `local_fall_log.txt` for offline debugging.
*   **Real-time Alerts:**
    *   **Logic App Webhook:** Asynchronously sends HTTP POST requests to Azure Logic Apps for email/SMS notifications without blocking the video feed.
*   **Responsible AI Verification:**
    *   **Database Schema:** Includes `VerificationStatus` (Pending/Verified/FalsePositive) and `VerifySubject` columns.
    *   **Experiment Tracking:** Generates unique `ExperimentID` per run for session management.
*   **Performance Monitoring:** Real-time RAM usage display.

## System Architecture

1.  **Detection Layer:** Python + OpenCV (ArUco).
2.  **Logic Layer:** Angle calculation, Smoothing, Thresholding (45 deg).
3.  **Data Layer:** Azure SQL Database (via ODBC).
4.  **Notification Layer:** Azure Logic Apps (HTTP Webhook).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd marker_dev
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup:**
    *   Ensure an Azure SQL Database is set up.
    *   Create a `sql.env` file in the root directory (not committed to git) with the following content:
        ```
        sql_id=your_username
        sql_pw=your_password
        sql_ocbc=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your_server.database.windows.net,1433;Database=your_database;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
        ```

## Usage

Run the main detection script:

```bash
python src/cylinder_fall_detection.py
```

### Operational Workflow
1.  **Startup:** The system generates a unique **Experiment ID**.
2.  **Monitoring:** The webcam feed monitors the object.
3.  **Fall Event:**
    *   If tilt > 45 degrees OR Bottom Marker (ID 99) is seen:
        *   Timer starts.
    *   If condition holds for **2.0 seconds**:
        *   **Log to DB:** Status `FALL_CONFIRMED`, VerificationStatus `0` (Pending).
        *   **Webhook:** Sends JSON payload to Logic App (Timeout 30s, Async).
        *   **Local Log:** Appends to `local_fall_log.txt`.

## Project Structure

*   `src/cylinder_fall_detection.py`: Main application entry point.
*   `src/db_logger.py`: Database interaction class.
*   `requirements.txt`: Python package dependencies.
*   `SQL_AGENT_TOOLS.md`: Documentation for SQL Agent verification tools.
