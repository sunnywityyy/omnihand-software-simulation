# OmniHand — Gesture-Based Smart Device Control

**OmniHand** is a camera-based software simulation that demonstrates gesture-controlled interaction with smart devices using computer vision and hand tracking. It showcases how natural hand gestures can be translated into commands for a smart bulb, fan, and television, providing a demonstration of the intended working principle of the OmniHand hardware project.

## Features

- Real-time webcam-based hand tracking.
- Gesture-based device selection and disconnection.
- Hand-movement-based control of simulated device parameters.
- Browser-based dashboard served through a local Flask application.
- Modular Python implementation using OpenCV and MediaPipe.

## Gesture Recognition and Device Mapping

| Hand Gesture | Action |
|---|---|
| Thumbs up (held briefly) | Connect to the Smart Bulb |
| Peace sign (held briefly) | Connect to the Smart Fan |
| Open palm (held briefly) | Connect to the Smart TV |
| Fist (held briefly) | Disconnect the active device |

## Device Control

Once a device is selected, hand movement controls its simulated functions:

- **Smart Bulb:** Move the hand upward to increase brightness and downward to decrease it.
- **Smart Fan:** Move the hand horizontally to adjust fan speed, from off/low toward higher speed.
- **Smart TV:** Move the hand vertically to adjust volume and horizontally to change channels.

> **Note:** All device interactions are simulated in software. The application does not directly control physical appliances.

## Technology Stack

- **Python** — application logic and integration.
- **Flask** — local web application server.
- **OpenCV** — webcam access and image processing.
- **MediaPipe** — hand-landmark detection and tracking.
- **NumPy** — numerical processing.

## Installation and Setup

### Prerequisites

- Windows operating system
- Python 3.11 recommended
- Visual Studio Code
- A working webcam
- Internet connection for initial dependency and hand-landmarker model downloads

### Run Locally

1. Extract the project files and open the project root in Visual Studio Code.
2. Open a PowerShell terminal in the project directory.
3. Run the setup script:

   ```powershell
   .\setup.ps1
   ```

4. If PowerShell blocks script execution in the current terminal, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

   Then run `.\setup.ps1` again.

5. Start the application:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

6. Open the following address in your browser:

   **http://127.0.0.1:5000**

The setup script installs the required Python dependencies and downloads the hand-landmarker model. If the model is missing, the application also attempts to download it at startup.

## Troubleshooting

- **Camera unavailable:** Close Windows Camera, Microsoft Teams, Zoom, other browser camera tabs, and any other applications using the webcam.
- **Camera permission issues:** Open Windows Settings → Privacy & security → Camera and enable access for desktop applications.
- **Unstable gesture recognition:** Improve lighting, keep your entire hand visible, and face your palm toward the camera.
- **Stop the application:** Press `Ctrl+C` in the terminal running the Flask server.

## Project Purpose

OmniHand Software Simulation serves as a demonstration of gesture-based smart-device interaction. It provides an interactive environment for testing the gesture recognition and device-control logic before or alongside physical hardware development.

## Future Scope

Potential extensions include integration with physical smart devices, additional gesture customization, improved recognition robustness, and communication with embedded hardware.

---

**OmniHand — Turning Natural Hand Gestures into Smart Device Commands.**
