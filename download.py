import pytubefix
import os
import requests

from track import Track


def download(video_url: str, download_audio_folder = os.path.join(os.getcwd(), "temp_download"), 
             download_thumbnail_folder = os.path.join(os.getcwd(), "temp_download")) -> tuple[str, str, list[Track]]:
    """Downloads a YouTube video's audio and thumbnail.
    
    Args:
        video_url (str): The URL of the YouTube video to download
        download_audio_folder (str, optional): Path where the audio file will be saved. Defaults to "temp_download"
        download_thumbnail_folder (str, optional): Path where the thumbnail will be saved. Defaults to "temp_download"
        
    Returns:
        tuple[str, str, list[track.Track]]: A tuple containing:
            - Path to the downloaded audio file
            - Path to the downloaded thumbnail image 
            - List of chapters as custom track object if available
            
    Raises:
        Exception: If the provided URL is invalid
    """
    try:
        video = pytubefix.YouTube(video_url)
    except pytubefix.exceptions.RegexMatchError:
        raise Exception("Invalid URL")
    
    os.makedirs(download_audio_folder, exist_ok=True)
    os.makedirs(download_thumbnail_folder, exist_ok=True)
    
    audio = download_audio(video, download_audio_folder)
    thumbnail = download_thumbnail(video.thumbnail_url, download_thumbnail_folder)
    video_chapters = video.chapters

    tracks = []
    for chapter in video_chapters:
        track = Track(chapter.title, chapter.start_seconds, chapter.duration)
        tracks.append(track)
    return (audio, thumbnail, tracks)


def download_audio(video: pytubefix.YouTube, download_folder = os.path.join(os.getcwd(), "temp_download")) -> str:
    """Downloads the audio stream from a YouTube video.
    
    Args:
        video (pytubefix.YouTube): The YouTube video object to download audio from
        download_folder (str, optional): Path where the audio file will be saved. Defaults to "\temp_download\"
        
    Returns:
        str: Path to the downloaded audio file
    """
    audio_stream = video.streams.get_audio_only()
    audio_stream.download(download_folder, "audio.mp3")
    return os.path.join(download_folder, "audio.mp3")


def download_thumbnail(thumbnail_url: str, download_folder = os.path.join(os.getcwd(), "temp_download")) -> str:
    """Downloads a thumbnail image from a YouTube video.
    
    Args:
        thumbnail_url (str): URL of the thumbnail image to download
        download_folder (str, optional): Path where the thumbnail will be saved. Defaults to "\temp_download\"
        
    Returns:
        str: Path to the downloaded thumbnail file
    """
    # Use requests to download the image.
    img_data = requests.get(thumbnail_url).content
    # Download it to a specific folder with a specific name.
    with open(os.path.join(download_folder, "cover.jpeg"), 'wb') as handler:
        handler.write(img_data)
    # Return download location.
    return os.path.join(download_folder, "cover.jpeg")

"""Tests"""

def test_download():
    """Test the download function."""
    # Test with a known video URL
    test_video_url = "https://www.youtube.com/watch?v=KVmtUWJmbNs"
    test_audio_path = os.getcwd() + "\\test_downloads\\"
    test_thumb_path = os.getcwd() + "\\test_downloads_thumbnail\\"
    
    try:
        # Ensure download directories exist
        os.makedirs(test_audio_path, exist_ok=True)
        os.makedirs(test_thumb_path, exist_ok=True)
        
        # Test download
        audio, thumbnail, tracks = download(test_video_url, test_audio_path, test_thumb_path)
        
        # Verify audio file exists and is not empty
        audio_file = test_audio_path + "audio.mp3"
        assert os.path.exists(audio_file), "Audio file was not downloaded"
        assert os.path.getsize(audio_file) > 0, "Audio file is empty"
        
        # Verify thumbnail file exists and is not empty
        thumb_file = test_thumb_path + "cover.jpeg"
        assert os.path.exists(thumb_file), "Thumbnail file was not downloaded"
        assert os.path.getsize(thumb_file) > 0, "Thumbnail file is empty"
        
        # Clean up
        os.remove(audio_file)
        os.remove(thumb_file)
        os.rmdir(test_audio_path)
        os.rmdir(test_thumb_path)
        
        print("Download test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise
    

def test_download_audio():
    """Test the download_audio function."""
    # Test with a known video URL
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    download_path = os.path.join(os.getcwd(), "temp_download")
    test_video = pytubefix.YouTube(test_video_url)
    
    try:
        # Ensure download directory exists
        os.makedirs(download_path, exist_ok=True)
        
        # Test download
        audio_file = download_audio(test_video, download_path)
        
        # Verify file exists
        assert os.path.exists(audio_file), "Audio file was not downloaded"
        
        # Verify file is not empty
        assert os.path.getsize(audio_file) > 0, "Audio file is empty"
        
        # Clean up
        os.remove(audio_file)
        os.rmdir(download_path)
        
        print("Download audio test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise


def test_download_thumbnail():
    """Test the download_thumbnail function."""
    # Test with a known thumbnail URL
    test_thumb_url = "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
    download_path = os.getcwd() + "\\test_downloads\\"
    
    try:
        # Ensure download directory exists
        os.makedirs(download_path, exist_ok=True)
        
        # Test download
        thumbnail_file = download_thumbnail(test_thumb_url, download_path)
        
        # Verify file exists
        assert os.path.exists(thumbnail_file), "Thumbnail file was not downloaded"
        
        # Verify file is not empty
        assert os.path.getsize(thumbnail_file) > 0, "Thumbnail file is empty"
        
        # Clean up
        os.remove(thumbnail_file)
        os.rmdir(download_path)
        
        print("Download thumbnail test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise


def main():
    download('https://www.youtube.com/watch?v=KVmtUWJmbNs')
    

if __name__ == '__main__':
    test_download()
    test_download_audio()
    test_download_thumbnail()

    # main()