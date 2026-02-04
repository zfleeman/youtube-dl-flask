# yt-dlp-flask

A simple Flask application to assist in downloading videos and audio from YouTube for A/V projects on iOS.

## Features

- Download video and audio from YouTube
- Choose between different formats: Video and Audio, Audio only, Video only, or all three
- Select the video/audio format that you need
- Simple web interface

## Setup

Surprise! It's a Docker image!

```bash
docker run -p 5111:5111 zachfleeman/yt-dlp-flask
```

## Usage

1. Enter the YouTube link in the provided input field.
2. Choose the desired format:
    - Video and Audio
    - Audio only
    - Video only
    - Three Files (Video, Audio, and both combined)
3. Uncheck the "Instant Download" checkbox if you want to browse the available formats.
4. Click the "Submit" button to start the download process.
5. Once the download is complete, you will be redirected to a download link for the file.

## Environment Variables

- `VIDEO_FILTER`: Filter for video format (default: `bv[ext=mp4][vcodec^=avc]`)
- `AUDIO_FILTER`: Filter for audio format (default: `ba[ext=m4a][acodec^=mp4a]`)
