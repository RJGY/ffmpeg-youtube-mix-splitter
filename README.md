# YouTube Mix Splitter

A powerful Python tool that automatically downloads YouTube music mixes and intelligently splits them into individual tracks, complete with metadata, album art, and original audio quality when possible.

## Overview

This application solves the common problem of wanting to save individual tracks from YouTube DJ mixes or music compilations. It identifies and extracts all chapters from a YouTube video, then processes each segment as a separate song with proper artist attribution and album art.

## Features

- **Intelligent Track Splitting**: Uses YouTube chapter markers to identify and split individual tracks
- **Smart Audio Selection**: Attempts to find and download original high-quality versions of each track
- **Metadata Enrichment**: Automatically extracts and embeds artist and title information
- **Thumbnail Processing**: Downloads, crops, and embeds album art for each track
- **Redis Integration**: Works as a microservice that can be controlled via Redis pub/sub
- **Duplicate Detection**: Prevents re-downloading tracks already in your library
- **Format Support**: Handles various title formats (Artist - Title, Artist | Title)
- **Custom Output Locations**: Supports saving to specified directories

## Architecture

The application consists of several key components:

- **Main Processor**: Orchestrates the downloading and splitting process
- **Downloader**: Handles YouTube video and metadata retrieval
- **Track Splitter**: Splits audio files and adds metadata
- **Redis Communication**: Enables integration with other services

## Prerequisites

- Python 3.11+ (may work with other versions)
- FFmpeg installed and available in your system PATH
- Redis (for pub/sub communication with other services)
- Required Python packages (install via `pip install -r requirements.txt`):
  - pytubefix
  - Pillow
  - requests
  - redis
  - python-dotenv

## Installation

1. Clone this repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Ensure FFmpeg is installed and in your PATH
4. Set up Redis if you plan to use the microservice functionality
5. Configure environment variables (optional)

## Usage

### As a Microservice

The application can run as a microservice that listens for Redis messages:

```python
python main.py
```

This will start the application in listener mode, processing YouTube URLs received through Redis. Currently, the redis application listens on the 'mix_processing' channel.

### Manual Usage

You can also use the application directly from Python:

```python
from main import manual_download

# Download and split a YouTube mix
manual_download('https://www.youtube.com/watch?v=YOUTUBE_ID', 'optional_output_folder')
```

## Configuration

The application can be configured using environment variables in a `.env` file:

- `THUMBNAIL_FOLDER`: Directory for temporary thumbnail storage
- `OUTPUT_FOLDER`: Base directory for saving output files
- `REDIS_PUBLISH_CHANNEL`: Redis channel for publishing completion messages

## How It Works

1. The service receives a YouTube URL via Redis or direct function call
2. It downloads the video and extracts chapter information
3. For each track:
   - It attempts to find the original song on YouTube
   - If found, it downloads the high-quality version
   - Otherwise, it extracts the segment from the mix
   - It adds metadata and album art
4. Processed tracks are saved to the output directory
5. A completion message is published to Redis (in microservice mode)

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Upcoming Features

[ ] Configurable subscriber channel for redis microservice input. Currently, the redis application listens on the 'mix_processing' channel.