# Hosting PeakCut on Hugging Face Spaces

You can host PeakCut for free (or on GPU) using a **Docker Space** on Hugging Face.

---

## 1. What Hugging Face Spaces Provides

* **Free CPU Tier**: 2 vCPU, 16 GB RAM, 50 GB disk (plenty of RAM for the speech model and ffmpeg).
* **Optional GPU Upgrades**: T4 ($0.60/hr) or A10G ($1.05/hr) for real-time speech transcription and faster rendering.
* **Free Public URL with HTTPS**: `https://<your-username>-<space-name>.hf.space`
* **Zero Server Maintenance**: Hugging Face automatically builds the Docker container and keeps it running.

---

## 2. Step-by-Step Setup

### Step 1: Create a New Space
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Enter a **Space name** (e.g., `peakcut` or `shinecut`).
3. Select **Docker** under **Space SDK** (choose "Blank" template).
4. Choose Visibility:
   * **Private** *(Recommended for personal use)*: Only you can open your Space, so you can leave sign-in disabled (`PEAKCUT_ACCOUNTS=0`).
   * **Public**: Anyone on the internet can visit it. If public, make sure to enable accounts (`PEAKCUT_ACCOUNTS=1`) so strangers cannot consume your AI tokens.
5. Click **Create Space**.

---

### Step 2: Push Your Code to the Space

In your local PeakCut folder, run:

```bash
# Add Hugging Face Space git remote (replace YOUR_USERNAME and YOUR_SPACE_NAME)
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME

# Push code to your Space
git push space main
```

*(If prompted for a password, generate an Access Token with **Write** permission at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) and use it as your password).*

---

### Step 3: Configure Environment Secrets

In your Space on Hugging Face:
1. Go to **Settings** $\rightarrow$ **Variables and secrets**.
2. Under **Secrets** (or **Variables**), add:
   * `PEAKCUT_AI_PROVIDER`: e.g. `gemini`, `openai`, `groq`, or `openrouter`
   * `PEAKCUT_AI_KEY`: your API key
   * `PEAKCUT_ACCOUNTS`: `0` (if Space is Private) or `1` (if Space is Public)

---

## 3. Important Tips for Free Spaces

1. **Cold Starts**: Free Spaces enter sleep mode after 48 hours of inactivity. When you visit the link again, it wakes up and takes about 30–60 seconds to boot.
2. **Persistence**: On the free tier, files inside the container reset if the Space rebuilds. Setting your AI key and settings in **Space Secrets** ensures they survive reboots. For permanent video storage, you can attach a persistent disk under **Settings** $\rightarrow$ **Persistent Storage**.
3. **Port**: Hugging Face automatically routes traffic to port **7860**, which the Dockerfile is already configured to expose.
