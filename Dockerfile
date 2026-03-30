FROM ubuntu:22.04

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    gpg \
    ffmpeg \
    python3.11 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install transformers==4.57.1 && \
    pip install faster-whisper==1.2.0 && \
    pip install pydub && \
    pip install f5-tts && \
    pip install moviepy==2.0.0 && \
    pip install firebase_admin && \
    pip install imagekitio && \
    pip install python-dotenv && \
    pip install pandas

RUN chmod +x tools/decrypt_firebase_cred.sh

RUN ./tools/decrypt_firebase_cred.sh

CMD ["python3", "src/main.py"]  