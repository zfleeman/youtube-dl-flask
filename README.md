# youtube-dl-flask

A simple Flask application to assist in downloading videos and audio from YouTube for A/V projects on iOS.

## Features

- Download video and audio from YouTube
- Choose between different formats: Video and Audio, Audio only, Video only, or all three
- Option to download in lower quality
- Simple web interface

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/youtube-dl-flask.git
    cd youtube-dl-flask
    ```

2. Create a `.env` file in the project root with the following content:
    ```env
    VIDEO_FILTER=bv[ext=mp4][vcodec^=avc]
    AUDIO_FILTER=ba[ext=m4a][acodec^=mp4a]
    ```

3. Build and run the Docker container:
    ```sh
    docker-compose up --build
    ```

4. Open your web browser and navigate to `http://localhost:5111`.

## Usage

1. Enter the YouTube link in the provided input field.
2. Choose the desired format:
    - Video and Audio
    - Audio only
    - Video only
    - Three Files (Video, Audio, and both combined)
3. Optionally, check the "Lower Quality" checkbox to download in lower quality.
4. Click the "Submit" button to start the download process.
5. Once the download is complete, you will be redirected to a download link for the file.

## Environment Variables

- `VIDEO_FILTER`: Filter for video format (default: `bv[ext=mp4][vcodec^=avc]`)
- `AUDIO_FILTER`: Filter for audio format (default: `ba[ext=m4a][acodec^=mp4a]`)
