# OmniHand Software Simulation

A static, Vercel-ready browser demo of OmniHand. Hand tracking and gesture recognition run in the visitor's browser using MediaPipe Tasks Vision; the bulb, fan, and TV are simulated UI devices. No Flask server or physical hardware is required.

## Deploy to Vercel

1. Extract this ZIP.
2. Open https://vercel.com and sign in with GitHub.
3. Create a new **public or private GitHub repository** named `omnihand-software-simulation` and upload the extracted files. Keep `index.html`, `vercel.json`, and the `static` folder at the repository root.
4. In Vercel, select **Add New → Project**, import that repository, and click **Deploy**. No build command or environment variables are needed; this is a static site.
5. Open the generated HTTPS URL. Click **Start camera** and allow camera access.

You can also use the Vercel CLI from this folder: install Node.js, run `npx vercel`, follow the prompts, then run `npx vercel --prod`.

## Gestures

- Hold thumbs up: connect Smart Bulb; move hand up/down to change brightness.
- Hold peace sign: connect Smart Fan; move hand left/right to change speed.
- Hold open palm: connect Smart TV; move up/down for volume and left/right for channel.
- Hold fist: disconnect the active device.
- Reset selection restores simulation values.

## Notes

- Camera access requires HTTPS (Vercel provides it) or `localhost` and explicit browser permission.
- The page downloads the MediaPipe vision runtime and hand-landmarker model from public CDNs on first use; internet access is required.
- Device states are visual simulations only; no real appliance is controlled.
- For best results, use a Chromium-based browser and keep your hand fully visible, well lit, and centered. The gesture classifier is a lightweight demo heuristic and may need tuning for different hands/camera angles.
