# PeakCut: one image with the web server, the clip pipeline and ffmpeg.
# Fully compatible with standard Docker, Docker Compose, and Hugging Face Spaces (port 7860, user 1000).
FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg ca-certificates bzip2 fonts-noto-core fonts-noto-cjk \
 && rm -rf /var/lib/apt/lists/*

# yt-dlp needs a JavaScript runtime for YouTube
COPY --from=denoland/deno:bin /deno /usr/local/bin/deno

# Create non-root user (UID 1000) for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY studio studio
COPY web web
COPY GAMING.md .

# Setup /data writable by user 1000
RUN mkdir -p /data && chown -R 1000:1000 /data /app

ENV PEAKCUT_DATA=/data \
    PEAKCUT_HOST=0.0.0.0 \
    PEAKCUT_PORT=7860 \
    PORT=7860 \
    PEAKCUT_TRUST_PROXY=1 \
    PYTHONUNBUFFERED=1

USER user

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s CMD python -c "import urllib.request, os; p = os.environ.get('PORT') or os.environ.get('PEAKCUT_PORT') or '7860'; urllib.request.urlopen(f'http://127.0.0.1:{p}/healthz', timeout=4)"

CMD ["python", "-m", "studio.server"]
