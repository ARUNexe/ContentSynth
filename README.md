# Content Creator

This project automates the creation of short-form videos from text conversations. It converts text into speech using voice cloning, overlays the generated audio onto a pre-uploaded base video, adds synchronized subtitles, and produces a final MP4. The output video is then uploaded directly to Instagram using the Graph API.

The system is designed as a pipeline that handles text processing, speech synthesis, video composition, and publishing with minimal manual intervention.

## Quick Start

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd content_creator
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Fill in your credentials in .env
   ```

## Environment Variables

Copy `.env.example` to `.env` and populate with your credentials:

```
# Firebase Configuration (encrypted with GPG)
FIREBASE_SECRET_PASSPHRASE=your_gpg_passphrase_here
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/

# Instagram Configuration
INSTAGRAM_LONG_LIVED_TOKEN=your_instagram_long_lived_token_here
IG_USER_ID=your_instagram_user_id_here

# Image API Configuration
FREEIMAGE_API_KEY=your_freeimage_api_key_here

# File Upload Configuration
CATBOX_USERHASH=your_catbox_userhash_here
```

### Firebase Credentials Encryption

The Firebase credentials file is encrypted using GPG for security. To decrypt:

1. Ensure your encrypted credentials file exists at `resources/creds/firebase_cred.json.gpg`

2. Set the `FIREBASE_SECRET_PASSPHRASE` in your `.env` file (the GPG passphrase used to encrypt the credentials)

3. The decryption script will automatically decrypt the credentials:
   ```bash
   ./tools/decrypt_firebase_cred.sh
   ```
   This script uses `FIREBASE_SECRET_PASSPHRASE` from your `.env` to decrypt `firebase_cred.json.gpg`

4. The decrypted credentials are loaded automatically by the application

**⚠️ Security Notes:**
- Never commit `.env` file to version control
- `FIREBASE_SECRET_PASSPHRASE` is required for decryption - keep it confidential
- The decrypted `firebase_cred.json` file is gitignored and never committed
- Ensure all tokens and keys are kept secure

## Project Structure

```
content_creator/
├── src/                          # Application source code
│   ├── main.py                   # Entry point
│   ├── audio_engine.py           # Speech synthesis
│   ├── video_engine.py           # Video composition
│   ├── subtitle_engine.py        # Subtitle generation
│   └── instagram_api_handler.py  # Instagram integration
├── resources/                    # Assets and data
├── tools/                        # Utility scripts
├── outputs/                      # Generated videos
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── Dockerfile                    # Container config
```

## System Design & Architecture

### Component Overview

The Content Creator system is composed of several interconnected modules that work together to automate video generation:

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **main.py** | Orchestrator - coordinates entire workflow | Python |
| **audio_engine.py** | Converts dialogue text to speech | F5-TTS |
| **subtitle_engine.py** | Generates synchronized subtitle files | MoviePy |
| **video_engine.py** | Composes video with audio and subtitles | MoviePy 2.0.0 |
| **instagram_api_handler.py** | Handles content publishing to Instagram | Meta Graph API |
| **Firebase** | Stores dialogue scripts and metadata | Realtime Database |
| **upload_quotes.py** | Imports dialogue data from CSV to Firebase | Firebase Admin SDK |

### End-to-End Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DATA INITIALIZATION (One-time)                           │
│                                                              │
│  CSV File (quotes.csv)                                       │
│      ↓                                                        │
│  python tools/upload_quotes.py                               │
│      ↓                                                        │
│  Firebase Realtime Database                                  │
│  - Stores dialogue pairs (character1 & character2)           │
│  - Tracks current_index (which quote to process next)        │
│  - Tracks total_quotes (total available dialogues)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. CONTENT GENERATION (Per Run)                             │
│                                                              │
│  python src/main.py                                          │
│      ↓                                                        │
│  ① FETCH QUOTE FROM FIREBASE                                │
│     main.py → Firebase DB                                    │
│     Retrieves: character1_dialogue, character2_dialogue      │
│      ↓                                                        │
│  ② GENERATE AUDIO (Parallel)                                │
│     audio_engine.py (uses F5-TTS)                           │
│     - Generate character1.wav                                │
│     - Generate character2.wav                                │
│      ↓                                                        │
│  ③ CREATE SUBTITLES                                         │
│     subtitle_engine.py                                       │
│     - Parse dialogue text                                    │
│     - Create .srt subtitle file                              │
│     - Synchronize with audio timing                          │
│      ↓                                                        │
│  ④ COMPOSE VIDEO                                            │
│     video_engine.py (uses MoviePy)                          │
│     - Load background video/images                           │
│     - Embed audio tracks (character voices)                  │
│     - Overlay synchronized subtitles                         │
│     - Export final video → outputs/video_name.mp4            │
│      ↓                                                        │
│  ⑤ PUBLISH TO INSTAGRAM                                     │
│     instagram_api_handler.py (uses Meta Graph API)          │
│     - Upload video to Instagram Business Account             │
│     - Add caption and hashtags                               │
│     - Post goes live                                         │
│      ↓                                                        │
│  ⑥ UPDATE FIREBASE                                          │
│     main.py → Firebase DB                                    │
│     - Increment current_index                                │
│     - Mark quote as processed                                │
│                                                              │
│  Result: One complete short-form video published             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. CONTINUOUS PROCESSING                                    │
│                                                              │
│  Repeat Step 2 on schedule (e.g., every 6 hours)            │
│  - GitHub Actions Cron: "15 3,12 * * *"                     │
│  - Each run processes next unprocessed quote                 │
│  - System continues until all quotes are processed           │
│  - Can be restarted with new quotes in Firebase              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Details

**Step 1: Data Input (CSV → Firebase)**
- Source: [resources/csv/quotes.csv](resources/csv/quotes.csv)
- Script: [tools/upload_quotes.py](tools/upload_quotes.py)
- Reads CSV with columns: `s.no`, `person1`, `person2` (dialogue text)
- Creates Firebase structure:
  ```
  /conversations/
  ├── source/
  │   ├── 1/ → {dialogue1: "...", dialogue2: "..."}
  │   ├── 2/ → {dialogue1: "...", dialogue2: "..."}
  │   └── n/ → {...}
  └── control/
      ├── current_index: 0
      └── total_quotes: n
  ```

**Step 2: Quote Processing (Main Application)**
- Fetch quote at `current_index` from Firebase
- Generate WAV files for both character voices
- Create subtitle timeline (.srt format)
- Composite video with audio/subtitles using moviepy
- Upload to Instagram via Graph API
- Increment `current_index`

**Step 3: Output Storage**
- Generated videos: [outputs/](outputs/) directory
- Format: `{character1}_{character2}_{timestamp}.mp4`
- Subtitles: Embedded in video file
- Metadata: Stored in Firebase

### Component Interactions

```
main.py (Orchestrator)
├─► firebase_admin → Firebase DB (read quotes, update index)
├─► audio_engine.py → Generate character audio files
├─► subtitle_engine.py → Create subtitle synchronization
├─► video_engine.py → Compose final video
└─► instagram_api_handler.py → Upload to Instagram
```

### Security & Data Flow

```
Environment Variables (.env)
├─► FIREBASE_SECRET_PASSPHRASE
│   └─► decrypt_firebase_cred.sh → secrets/firebase_cred_secret.json
├─► FIREBASE_DATABASE_URL
├─► INSTAGRAM_LONG_LIVED_TOKEN
├─► IG_USER_ID
├─► FREEIMAGE_API_KEY
└─► CATBOX_USERHASH
```

All sensitive data flows through encrypted credentials (GPG) and environment variables, never hardcoded.

## Usage

### Step 1: Upload Quotes to Firebase (One-time setup)

Before running the application for the first time, import your dialogue content into Firebase:

```bash
python tools/upload_quotes.py
```

This uploads all quotes from your CSV file to the Firebase Realtime Database. **This step only needs to be done once** - it populates Firebase with multiple dialogue entries that will be processed by the application.

### Step 2: Run the Application

Run the main application to process quotes:

```bash
python src/main.py
```

**How it works:**
- Each time you run `main.py`, it retrieves ONE quote from Firebase
- The application processes that quote by:
  1. Generating audio for character dialogue using text-to-speech
  2. Creating a video with synchronized subtitles
  3. Publishing the final video to Instagram
- After completion, the system updates the quote index and marks it as processed
- The next run will process the next quote in the queue

**To process all quotes continuously**, schedule `main.py` to run periodically (e.g., via cron or GitHub Actions)

## Key Features

- Automated speech synthesis with character voices
- Dynamic subtitle synchronization
- Instagram Graph API integration
- Firebase Real-time Database support
- Batch processing capabilities

## Requirements

- Python 3.9+
- Dependencies listed in requirements.txt
- Active API credentials for Firebase, Instagram, and media services

## Docker

Build and run the container:
```bash
docker build -t content-creator .
docker run --env-file .env content-creator
```

## License

This project is provided as-is for authorized use only.
