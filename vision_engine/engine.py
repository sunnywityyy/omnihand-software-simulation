import os, time, threading, urllib.request
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "models", "hand_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except Exception:
    mp = python = vision = None

class OmniHandEngine:
    def __init__(self):
        self.lock = threading.Lock()
        self.frame = None
        self.cap = None
        self.landmarker = None
        self.running = True
        self.last_select = 0
        self.hold_start = None
        self.last_gesture = "UNKNOWN"
        self.fist_start = None
        self.data = {
            "camera":"Starting", "model":"Checking", "gesture":"Waiting for hand",
            "active_device":None, "mode":"Select a device with a gesture",
            "message":"Show a gesture to connect to a device.",
            "devices":{
                "bulb":{"name":"Smart Bulb","active":False,"brightness":20,"status":"Standby"},
                "fan":{"name":"Smart Fan","active":False,"speed":0,"status":"Off"},
                "tv":{"name":"Smart TV","active":False,"volume":20,"channel":1,"status":"Standby"}
            }
        }
        threading.Thread(target=self.loop, daemon=True).start()

    def setup_model(self):
        if not vision:
            self.data["model"] = "MediaPipe unavailable"
            self.data["message"] = "Install requirements with setup.ps1."
            return False
        if not os.path.exists(MODEL):
            try:
                os.makedirs(os.path.dirname(MODEL), exist_ok=True)
                urllib.request.urlretrieve(MODEL_URL, MODEL)
            except Exception:
                self.data["model"] = "Model download failed"
                self.data["message"] = "Run setup.ps1 to download the hand model."
                return False
        try:
            opts = vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(model_asset_path=MODEL),
                running_mode=vision.RunningMode.VIDEO, num_hands=1,
                min_hand_detection_confidence=.5, min_hand_presence_confidence=.5,
                min_tracking_confidence=.5)
            self.landmarker = vision.HandLandmarker.create_from_options(opts)
            self.data["model"] = "Ready"
            return True
        except Exception as e:
            self.data["model"] = "Model error"
            self.data["message"] = "Could not initialize hand model: " + str(e)[:180]
            return False

    def open_camera(self):
        for idx in (0,1,2):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ok, f = cap.read()
                if ok and f is not None:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
                    self.data["camera"] = f"Connected (camera {idx})"
                    return cap
            cap.release()
        self.data["camera"] = "Not detected"
        self.data["message"] = "Webcam not detected. Close other camera apps and check Windows camera permissions."
        return None

    @staticmethod
    def extended(lm, tip, pip, mcp):
        return lm[tip].y < lm[pip].y < lm[mcp].y

    def classify(self, lm):
        ix = self.extended(lm,8,6,5); mid = self.extended(lm,12,10,9)
        ring = self.extended(lm,16,14,13); pinky = self.extended(lm,20,18,17)
        wrist = lm[0]
        thumb = np.hypot(lm[4].x-wrist.x,lm[4].y-wrist.y) > np.hypot(lm[3].x-wrist.x,lm[3].y-wrist.y)*1.12
        if thumb and not ix and not mid and not ring and not pinky: return "THUMBS UP"
        if ix and mid and not ring and not pinky: return "PEACE"
        if ix and mid and ring and pinky: return "OPEN PALM"
        if not ix and not mid and not ring and not pinky and not thumb: return "FIST"
        return "UNKNOWN"

    def loop(self):
        model_ok = self.setup_model()
        self.cap = self.open_camera()
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                self.status_frame("Webcam not detected", "Check camera permissions and restart.")
                time.sleep(.5); continue
            ok, frame = self.cap.read()
            if not ok or frame is None:
                time.sleep(.05); continue
            frame = cv2.flip(frame, 1)
            gesture, center, lm = "UNKNOWN", None, None
            if model_ok and self.landmarker:
                try:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = self.landmarker.detect_for_video(
                        mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                        int(time.monotonic()*1000))
                    if result.hand_landmarks:
                        lm = result.hand_landmarks[0]
                        gesture = self.classify(lm)
                        center = (sum(lm[i].x for i in (0,5,9,13,17))/5,
                                  sum(lm[i].y for i in (0,5,9,13,17))/5)
                        self.draw_hand(frame, lm)
                except Exception as e:
                    self.data["message"] = "Vision error: " + str(e)[:140]
            self.update(gesture, center)
            cv2.rectangle(frame,(10,10),(frame.shape[1]-10,76),(12,20,32),-1)
            cv2.putText(frame,"GESTURE: "+self.data["gesture"],(23,38),cv2.FONT_HERSHEY_SIMPLEX,.7,(70,230,255),2)
            cv2.putText(frame,"MODE: "+self.data["mode"][:48],(23,64),cv2.FONT_HERSHEY_SIMPLEX,.48,(235,240,250),1)
            good, enc = cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),82])
            if good:
                with self.lock: self.frame = enc.tobytes()
            time.sleep(.01)
        if self.cap: self.cap.release()
        if self.landmarker: self.landmarker.close()

    def draw_hand(self, frame, lm):
        h,w = frame.shape[:2]
        links = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]
        for a,b in links:
            cv2.line(frame,(int(lm[a].x*w),int(lm[a].y*h)),(int(lm[b].x*w),int(lm[b].y*h)),(50,220,255),2)
        for p in lm: cv2.circle(frame,(int(p.x*w),int(p.y*h)),4,(255,255,255),-1)

    def update(self, gesture, center):
        now = time.time()
        self.data["gesture"] = gesture if center else "Waiting for hand"
        if center is None:
            self.hold_start = None
            return
        mapping = {"THUMBS UP":"bulb","PEACE":"fan","OPEN PALM":"tv"}
        if gesture in mapping:
            if self.last_gesture != gesture: self.hold_start = now
            if self.hold_start and now-self.hold_start > .8 and now-self.last_select > 1.5:
                self.activate(mapping[gesture]); self.last_select = now
                self.data["message"] = f"{self.data['devices'][mapping[gesture]]['name']} connected. Move your hand to control it."
        elif gesture == "FIST":
            self.hold_start = None
            if self.last_gesture != "FIST": self.fist_start = now
            if self.fist_start and now-self.fist_start > 1.0 and self.data["active_device"]:
                self.deactivate()
        else:
            self.hold_start = None
        self.last_gesture = gesture
        key = self.data["active_device"]
        if key:
            x,y = max(.04,min(.96,center[0])),max(.08,min(.92,center[1]))
            d = self.data["devices"][key]
            if key == "bulb":
                d["brightness"] = max(0,min(100,round((.92-y)/.84*100)))
                d["status"] = "On" if d["brightness"] else "Off"
            elif key == "fan":
                d["speed"] = max(0,min(100,round((x-.04)/.92*100)))
                d["status"] = "Off" if d["speed"] < 8 else "Low" if d["speed"] < 38 else "Medium" if d["speed"] < 72 else "High"
            elif key == "tv":
                d["volume"] = max(0,min(100,round((.92-y)/.84*100)))
                d["channel"] = max(1,min(20,round(1+(x-.04)/.92*19)))
                d["status"] = "Playing"

    def activate(self, key):
        for k,d in self.data["devices"].items():
            d["active"] = k == key
            if k != key: d["status"] = "Standby"
        self.data["active_device"] = key
        self.data["mode"] = "Controlling " + self.data["devices"][key]["name"]

    def deactivate(self):
        key = self.data["active_device"]
        if key: self.data["devices"][key]["active"] = False; self.data["devices"][key]["status"] = "Standby"
        self.data["active_device"] = None
        self.data["mode"] = "Select a device with a gesture"
        self.data["message"] = "Device disconnected. Show a gesture to connect again."

    def status_frame(self, title, subtitle):
        f = np.zeros((540,960,3),dtype=np.uint8); f[:] = (22,28,40)
        cv2.putText(f,title,(60,235),cv2.FONT_HERSHEY_SIMPLEX,1.1,(80,220,255),2)
        cv2.putText(f,subtitle[:90],(60,285),cv2.FONT_HERSHEY_SIMPLEX,.55,(220,225,235),1)
        ok,enc=cv2.imencode(".jpg",f)
        if ok:
            with self.lock: self.frame=enc.tobytes()

    def jpeg(self):
        with self.lock: return self.frame

    def status(self):
        with self.lock: return {**self.data, "devices": {k:dict(v) for k,v in self.data["devices"].items()}}

    def reset(self):
        key=self.data["active_device"]
        if key: self.data["devices"][key]["active"]=False; self.data["devices"][key]["status"]="Standby"
        self.data["active_device"]=None
        self.data["mode"]="Select a device with a gesture"
        self.data["message"]="Selection reset. Show a gesture to connect to a device."
        self.hold_start=None
