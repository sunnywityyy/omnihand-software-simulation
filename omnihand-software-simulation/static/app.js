import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";
const $ = (id) => document.getElementById(id);
const video = $("camera"), canvas = $("overlay"), ctx = canvas.getContext("2d");
let landmarker = null, stream = null, running = false, raf = 0, lastDetect = 0, lastGesture = "", gestureSince = 0, activeDevice = null, lastControl = 0, toastTimer = 0;
const state = { bulb: 20, fan: 0, volume: 20, channel: 1 };
const fingerTips = [8,12,16,20], fingerPips = [6,10,14,18];
function message(text){ $("messageText").textContent=text; }
function toast(text){const el=$("toast");el.textContent=text;el.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove("show"),2200)}
function clamp(n,min,max){return Math.max(min,Math.min(max,n))}
function fingerUp(lm,tip,pip){return lm[tip].y < lm[pip].y - .025}
function classify(lm){
  const index=fingerUp(lm,8,6), middle=fingerUp(lm,12,10), ring=fingerUp(lm,16,14), pinky=fingerUp(lm,20,18);
  // Thumb direction is measured in screen coordinates; camera preview is mirrored for a natural selfie view.
  const thumbUp=lm[4].y < lm[3].y-.035 && lm[3].y < lm[2].y+.02;
  const thumbExtended=Math.hypot(lm[4].x-lm[2].x,lm[4].y-lm[2].y) > .13;
  if(thumbUp && !index && !middle && !ring && !pinky) return "thumbs_up";
  if(index && middle && !ring && !pinky) return "peace";
  if(index && middle && ring && pinky) return "open_palm";
  if(!index && !middle && !ring && !pinky && !thumbExtended) return "fist";
  // Fist is common in a slightly rotated hand; folded fingers remain the strongest signal.
  if(!index && !middle && !ring && !pinky) return "fist";
  return "unknown";
}
function gestureLabel(g){return ({thumbs_up:"Thumbs up",peace:"Peace sign",open_palm:"Open palm",fist:"Fist",unknown:"Hand detected"})[g]||"Waiting for hand"}
function selectDevice(device){activeDevice=device;for(const key of ["bulb","fan","tv"])$("card-"+key).classList.toggle("active",key===device);$("activeDevice").textContent=device?({bulb:"Smart Bulb connected",fan:"Smart Fan connected",tv:"Smart TV connected"})[device]:"No device connected";$("modeText").textContent=device?({bulb:"Move your hand vertically to adjust brightness.",fan:"Move your hand horizontally to adjust fan speed.",tv:"Move vertically for volume and horizontally for channel."})[device]:"Hold a selection gesture briefly.";renderDevices()}
function renderDevices(){$("bulbValue").textContent=state.bulb+"%";$("bulbStatus").textContent=activeDevice==="bulb"?"Connected · Active":"Standby";$("bulbMeter").style.width=state.bulb+"%";$("fanValue").textContent=state.fan+"%";$("fanStatus").textContent=state.fan===0?"Off":activeDevice==="fan"?"Connected · Active":"Ready";$("fanMeter").style.width=state.fan+"%";$("tvValue").textContent="Vol "+state.volume;$("tvExtra").textContent="Channel "+state.channel;$("tvStatus").textContent=activeDevice==="tv"?"Connected · Active":"Standby";$("tvMeter").style.width=(state.volume*100/100)+"%"}
function handleGesture(g, lm, now){
  if(g!==lastGesture){lastGesture=g;gestureSince=now}
  const held=now-gestureSince;
  if(held>850 && ["thumbs_up","peace","open_palm"].includes(g)){
    const target=({thumbs_up:"bulb",peace:"fan",open_palm:"tv"})[g];
    if(activeDevice!==target){selectDevice(target);toast(({bulb:"Smart Bulb selected",fan:"Smart Fan selected",tv:"Smart TV selected"})[target]);lastControl=now}
  } else if(g==="fist" && held>900 && activeDevice){selectDevice(null);toast("Device disconnected");lastControl=now}
  if(!activeDevice || now-lastControl<120)return;
  const x=lm[9].x, y=lm[9].y;
  // Relative hand position maps to controls. Throttle updates to keep values stable.
  if(activeDevice==="bulb") state.bulb=Math.round(clamp((.88-y)*125,0,100));
  if(activeDevice==="fan") state.fan=Math.round(clamp((x-.12)*140,0,100));
  if(activeDevice==="tv") {state.volume=Math.round(clamp((.9-y)*125,0,100));state.channel=Math.round(clamp(x*20,1,20));}
  lastControl=now;renderDevices();
}
function drawLandmarks(lm){const w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);if(!lm)return;const links=[[0,1,2,3,4],[0,5,6,7,8],[5,9,10,11,12],[9,13,14,15,16],[13,17,18,19,20],[0,17]];ctx.lineWidth=Math.max(2,w/240);ctx.strokeStyle="#54dce9";ctx.fillStyle="#ff626a";for(const line of links){ctx.beginPath();line.forEach((idx,i)=>{const p=lm[idx];const x=(1-p.x)*w,y=p.y*h;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke()}for(const p of lm){ctx.beginPath();ctx.arc((1-p.x)*w,p.y*h,Math.max(2,w/180),0,Math.PI*2);ctx.fill()}}
async function startCamera(){
  const btn=$("startBtn");btn.disabled=true;btn.textContent="Starting…";message("Requesting camera permission…");
  try{
    if(!navigator.mediaDevices?.getUserMedia)throw new Error("Camera access requires HTTPS or localhost in a supported browser.");
    stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:{ideal:1280},height:{ideal:720}},audio:false});video.srcObject=stream;await video.play();
    $("cameraPlaceholder").classList.add("hidden");$("cameraStatus").textContent="Loading model";$("connectionText").textContent="Loading hand tracker";$("liveDot").style.background="#f1a94c";
    if(!landmarker){const vision=await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm");landmarker=await HandLandmarker.createFromOptions(vision,{baseOptions:{modelAssetPath:"https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",delegate:"GPU"},runningMode:"VIDEO",numHands:1,minHandDetectionConfidence:.55,minHandPresenceConfidence:.5,minTrackingConfidence:.5});}
    running=true;$("cameraStatus").textContent="Live";$("modelStatus").textContent="Tracking";$("connectionText").textContent="Camera connected";$("liveDot").style.background="#4de0a0";message("Show thumbs up, peace sign, or open palm and hold it briefly to select a device.");btn.textContent="Camera active";raf=requestAnimationFrame(loop);
  }catch(e){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}btn.disabled=false;btn.textContent="Try camera again";$("cameraStatus").textContent="Unavailable";$("modelStatus").textContent="Not started";$("connectionText").textContent="Camera unavailable";message(e?.name==="NotAllowedError"?"Camera permission was blocked. Allow camera access in your browser and try again.":"Could not start camera/model: "+(e?.message||e));toast("Camera could not start");}
}
function loop(now){if(!running)return;raf=requestAnimationFrame(loop);if(video.readyState<2||now-lastDetect<35)return;lastDetect=now;canvas.width=video.videoWidth||640;canvas.height=video.videoHeight||480;try{const result=landmarker.detectForVideo(video,now);const lm=result.landmarks?.[0];if(lm){drawLandmarks(lm);const g=classify(lm);$("gestureText").textContent=gestureLabel(g);handleGesture(g,lm,now);if(g==="unknown")message(activeDevice?"Hand tracked. Keep your hand visible to control the selected device.":"Gesture not recognized. Try the examples below.");}else{ctx.clearRect(0,0,canvas.width,canvas.height);lastGesture="";$("gestureText").textContent="Waiting for hand";if(!activeDevice)message("Show your hand clearly in the camera view.")}}catch(e){console.error(e);message("Hand tracking paused. Try restarting the camera.")}}
function stopCamera(){running=false;cancelAnimationFrame(raf);if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}video.srcObject=null;ctx.clearRect(0,0,canvas.width,canvas.height);$("cameraPlaceholder").classList.remove("hidden");$("cameraStatus").textContent="Standby";$("modelStatus").textContent="Not started";$("connectionText").textContent="Camera not started";$("liveDot").style.background="#f1a94c";$("startBtn").disabled=false;$("startBtn").textContent="Start camera";$("gestureText").textContent="Waiting for hand";message("Camera stopped. Start it again when ready.")}
$("startBtn").addEventListener("click",startCamera);
$("resetBtn").addEventListener("click",()=>{state.bulb=20;state.fan=0;state.volume=20;state.channel=1;selectDevice(null);renderDevices();toast("Simulation reset")});
window.addEventListener("pagehide",()=>{stopCamera();landmarker?.close()});renderDevices();
