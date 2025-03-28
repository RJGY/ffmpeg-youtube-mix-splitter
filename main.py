import os
import json
import asyncio
from dotenv import load_dotenv

from splitter import split
from download import download
from redis_pub_sub import RedisSubscriber, RedisPublisher


# Load environment variables from .env file
load_dotenv()

thumbnail_folder = os.getenv('THUMBNAIL_FOLDER', os.path.join(os.getcwd(), 'temp_download'))
output_folder = os.getenv('OUTPUT_FOLDER', os.path.join(os.getcwd(), 'output'))
publisher = RedisPublisher(channel=os.getenv('REDIS_PUBLISH_CHANNEL', 'mix_processing_finished'))

def process_message(message: dict) -> None:
    """Handle incoming Redis messages."""
    if message['type'] != 'message':
        return

    try:
        data = json.loads(message['data'])
        video_url = data.get('video_url')
        location = data.get('location')
        
        if not video_url:
            print("Error: No video URL provided in message")
            return

        print(f"Processing video: {video_url}")
        print(f"Location: {location}")
        asyncio.to_thread(process_video(video_url, location))

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON message received: {message['data']}")
    except Exception as e:
        print(f"Error processing message: {str(e)}")

def process_video(video_url: str, location: str) -> None:
    """Download and split the video."""
    try:
        # Download the video and get necessary data
        audio, thumbnail, tracks = download(video_url)

        # Extra thing so we can download to other folders
        new_location = output_folder
        print(f"Old Location: {output_folder}")
        if location:
            base_folder = os.path.abspath(os.path.join(output_folder, os.pardir))
            print(f"Base Folder: {base_folder}")
            new_location = os.path.join(base_folder, location)

        print(f"New Location: {new_location}")

        # Ensure the output directory exists
        os.makedirs(new_location, exist_ok=True)

        # Split the audio
        songs = split(audio, thumbnail, tracks, thumbnail_folder, new_location)
        
        print(f"Successfully processed video. Output songs: {songs}")
        publisher.publish({
            "video_url": video_url,
            "songs" : songs
        })
        
    except Exception as e:
        print(f"Error processing video {video_url}: {str(e)}")

def main():
    # Ensure directories exist
    os.makedirs(thumbnail_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Initialize Redis subscriber
    subscriber = RedisSubscriber(channel='mix_processing')
    print(f"Starting audio processor. Listening on channel: {subscriber.channel}")
    
    # Start listening for messages
    subscriber.subscribe(callback=process_message)

def manual_download(video_url, location = None):
    # Download the video and get necessary data
    audio, thumbnail, tracks = download(video_url)

    # Extra thing so we can download to other folders
    new_location = output_folder
    if location:
        base_folder = os.path.dirname(new_location)
        new_location = os.path.join(base_folder, location)
    
    # Ensure the output directory exists
    os.makedirs(new_location, exist_ok=True)
    
    # Split the audio
    songs = split(audio, thumbnail, tracks, thumbnail_folder, new_location)

if __name__ == '__main__':
    # main()
    manual_download('https://www.youtube.com/watch?v=FOxIFxW_-a4', 'balls')