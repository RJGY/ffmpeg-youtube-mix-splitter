# YouTube Mix Splitter

A Python tool that downloads YouTube videos (typically music mixes) and automatically splits them into individual tracks based on the video chapters, while preserving metadata and thumbnails.

## Features

- Downloads audio from YouTube videos
- Extracts chapter information to split tracks
- Adds metadata (artist, title) to split tracks
- Downloads and crops video thumbnails for album art
- Handles duplicate track names for repeat songs.
- Supports various title formats (Artist - Title, Artist | Title)

## Prerequisites

- Python 3.11.x (might work with other python versions, not sure)
- FFmpeg installed and available in system PATH
- Required Python packages (install via `pip install -r requirements.txt`):
  - pytubefix
  - Pillow
  - requests

## Todo

- Implement queue/messaging system for more robust processing
