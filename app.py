from flask import Flask, render_template, Response, jsonify
from vision_engine.engine import OmniHandEngine
import time

app = Flask(__name__)
engine = OmniHandEngine()

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/video_feed")
def video_feed():
    def frames():
        while True:
            frame = engine.jpeg()
            if frame:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            else:
                time.sleep(.1)
    return Response(frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.get("/api/status")
def status():
    return jsonify(engine.status())

@app.post("/api/reset")
def reset():
    engine.reset()
    return jsonify(engine.status())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True, use_reloader=False)
