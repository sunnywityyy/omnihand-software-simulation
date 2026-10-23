$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
New-Item -ItemType Directory -Force -Path "models" | Out-Null
if (-not (Test-Path "models\hand_landmarker.task")) {
  Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "models\hand_landmarker.task"
}
Write-Host "Setup complete. Run: .\.venv\Scripts\python.exe app.py" -ForegroundColor Green
