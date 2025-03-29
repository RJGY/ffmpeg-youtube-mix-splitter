# YouTube Mix Splitter

A Python tool that downloads YouTube videos (typically music mixes) and automatically splits them into individual tracks based on the video chapters, while preserving metadata and thumbnails.

## Features

- Extracts chapter information to split tracks.
- Adds metadata (artist, title) to split tracks.
- Downloads audio from extracted metadata to find original audio.
- Downloads audio from YouTube videos if original audio does not exist.
- Downloads and crops video thumbnails for album art.
- Handles duplicate track names for repeat songs within mix.
- Handle duplicate tracks which may already exist in folder that we download to.
- Supports various title formats (Artist - Title, Artist | Title).

## Prerequisites

- Python 3.11.x (might work with other python versions, not sure)
- FFmpeg installed and available in system PATH
- Redis docker image (for communication with other services)
- Required Python packages (install via `pip install -r requirements.txt`):
  - pytubefix
  - Pillow
  - requests
  - redis

