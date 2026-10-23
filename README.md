# OmniHand Software Simulation

Camera-based hand-gesture control for three simulated devices.

## Gesture mapping
- Thumbs up (hold briefly) → connect to Smart Bulb.
- Peace sign (hold briefly) → connect to Smart Fan.
- Open palm (hold briefly) → connect to Smart TV.
- Fist (hold briefly) → disconnect the active device.

After connecting:
- Bulb: move hand up for more brightness; down for less.
- Fan: move hand left for off/low; right for higher speed.
- TV: move hand up/down for volume and left/right for channel.

Device actions are simulated; this does not control real appliances.

## Setup (Windows + VS Code)
1. Extract this ZIP and open the extracted folder in VS Code.
2. Open a PowerShell terminal in the project root.
3. Run `.\setup.ps1`. If script execution is blocked in this terminal, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, then rerun setup.
4. Run `.\.venv\Scripts\python.exe app.py`.
5. Open http://127.0.0.1:5000 in your browser.

Python 3.11 is recommended. Setup installs Flask, OpenCV, MediaPipe and NumPy, then downloads the hand-landmarker model. The app also attempts to download the model at startup if it is missing.

## Troubleshooting
- Close Windows Camera, Teams, Zoom, other browser camera tabs, and other scripts using the webcam.
- Check Windows Settings → Privacy & security → Camera and allow desktop apps.
- Use good lighting and keep the whole hand in view, palm facing the camera.
- Stop the app with Ctrl+C in the terminal.
