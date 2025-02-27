import os
import subprocess
import wave
import struct

from PIL import Image
from track import Track

def check_ffmpeg() -> bool:
    """Checks if ffmpeg is available on the system.
    
    Returns:
        bool: True if ffmpeg is available, False otherwise
    """
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False
    

def merge_duplicate_tracks(tracks: list[Track]) -> list[Track]:
    """Merges tracks with duplicate titles, keeping the earlier start time.
    
    Args:
        tracks (list[Track]): List of Track objects to process
        
    Returns:
        list[Track]: New list with duplicate titles merged
    """
    # Dictionary to store unique tracks by title
    merged = {}
    
    for track in tracks:
        if track.title in merged:
            # If we've seen this title before, keep earlier start time
            existing = merged[track.title]
            merged[track.title] = Track(
                track.title,
                min(existing.start, track.start),
                track.duration
            )
        else:
            # First time seeing this title
            merged[track.title] = track
            
    # Convert dictionary values back to list
    return list(merged.values())

def split_track(audio: str, track: Track, thumbnail: str, output_folder = os.getcwd() + "\\temp_download\\") -> str:
    """Split an audio file into a single track with metadata.
    
    Args:
        audio (str): Path to the input audio file
        track (Track): Track object containing title, start time and duration
        thumbnail (str): Path to the album art image file
        output_folder (str, optional): Directory to save output file. Defaults to current directory + "\\temp_download\\"
        
    Returns:
        str: Path to the output mp3 file
        
    Raises:
        Exception: If ffmpeg command fails
    """
    # Create output filename from track title
    if " - " in track.title:
        track_name = track.title.split(" - ", 1)[1].strip()
        artist = track.title.split(" - ", 1)[0].strip()
    elif " | " in track.title:
        track_name = track.title.split(" | ", 1)[1].strip()
        artist = track.title.split(" | ", 1)[0].strip()
    else:
        track_name = track.title.strip()
        artist = track_name
    output_file = f"{output_folder}{track.title.strip()}.mp3"
    
    # Build ffmpeg command to extract the segment and add metadata
    command = [
        'ffmpeg',
        '-y', # Always overwrite
        '-i', audio,  # Input file
        '-i', thumbnail,  # Album art file
        '-ss', str(track.start),  # Start time
        '-t', str(track.duration),  # Duration
        '-c:a', 'libmp3lame',  # Copy without re-encoding
        '-map', '0:a:0',  # Map the first audio stream
        '-map', '1:0',  # Map the album art
        '-map_metadata', '-1',  # Remove existing metadata
        '-metadata', f'title={track_name}',  # Add title metadata
        '-metadata', f'artist={artist}',  # Add artist metadata
        '-id3v2_version', '3',  # Use ID3v2.3 format
        '-f', 'mp3', # Specify mp3
        output_file
    ]
    
    # Execute ffmpeg command
    try:
        subprocess.run(command, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to split track '{track.title}': ffmpeg command failed with return code {e.returncode}")
    except Exception as e:
        raise Exception(f"Failed to split track '{track.title}': {str(e)}")
    
    return output_file

def crop_thumbnail(thumbnail: str, output_folder = os.getcwd() + "\\temp_download\\"):
    """Crops the thumbnail from the YouTube video to a 16:9 aspect ratio.
    
    Args:
        thumbnail (str): Path to the input thumbnail image file
        output_folder (str, optional): Directory to save cropped thumbnail. Defaults to current directory + "\\temp_download\\"
        
    Returns:
        str: Path to the cropped thumbnail file
        
    Raises:
        Exception: If image cannot be opened or ffmpeg command fails
    """
    img = Image.open(thumbnail)
    
    width, height = img.width, img.height
    
    ratio = width / height

    output_file = output_folder + "new_cover.jpeg"
    
    if ratio > 1:
        # Image is wider than 16:9
        unit = width / 16
        new_height = 9 * unit
        diff = (height - new_height) / 2
        
        # Crop to 16:9 from center
        crop_params = f"crop={int(width)}:{int(new_height)}:0:{int(diff)}"
        try:
            subprocess.run([
                "ffmpeg",
                '-y', # Always overwrite
                "-i", thumbnail,
                "-vf", crop_params,
                "-c:a", "copy",
                output_file
            ], capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cropping thumbnail: {e.stderr.decode()}")
            raise
    else:
        # Image is taller than 16:9
        unit = height / 9
        new_width = 16 * unit
        diff = (width - new_width) / 2
        
        # Crop to 16:9 from center
        crop_params = f"crop={int(new_width)}:{int(height)}:{int(diff)}:0"
        try:
            subprocess.run([
                "ffmpeg",
                '-y', # Always overwrite
                "-i", thumbnail,
                "-vf", crop_params,
                "-c:a", "copy",
                output_file
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cropping thumbnail: {e.stderr.decode()}")
            raise

    return output_file
    
def split(audio: str, thumbnail: str, tracks: list[Track], thumbnail_folder = os.getcwd() +"\\temp_download\\", output_folder = os.getcwd() +"\\temp_download\\") -> str:
    """Split an audio file into multiple tracks with metadata.
    
    Args:
        audio (str): Path to the input audio file
        thumbnail (str): Path to the album art image file
        tracks (list[Track]): List of Track objects containing title, start time and duration
        thumbnail_folder (str, optional): Directory to save the cropped thumbnail. Defaults to current directory + "\\temp_download\\"
        output_folder (str, optional): Directory to save output files. Defaults to current directory + "\\temp_download\\"
        
    Returns:
        list[str]: List of paths to the output mp3 files
        
    Raises:
        Exception: If ffmpeg is not available on the system
    """
    if not check_ffmpeg():
        raise Exception("ffmpeg is not available on the system")
    
    tracks = merge_duplicate_tracks(tracks)
    thumbnail = crop_thumbnail(thumbnail, thumbnail_folder)

    songs = []

    for track in tracks:
        song = split_track(audio, track, thumbnail, output_folder)
        songs.append(song)

    return songs
        
    

def test_check_ffmpeg():
    """Test the check_ffmpeg function."""
    try:
        # Test when ffmpeg is available
        result = check_ffmpeg()
        assert isinstance(result, bool), "check_ffmpeg should return a boolean"
        assert result is True, "ffmpeg should be available on the system"
        print("check_ffmpeg test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

def test_merge_duplicate_tracks():
    """Test the merge_duplicate_tracks function."""
    try:
        # Test case 1: No duplicates
        tracks1 = [
            Track("Song 1", 0, 60),
            Track("Song 2", 60, 60)
        ]
        result1 = merge_duplicate_tracks(tracks1)
        assert len(result1) == 2, "Should keep all unique tracks"
        
        # Test case 2: With duplicates
        tracks2 = [
            Track("Song 1", 0, 60),
            Track("Song 2", 60, 60),
            Track("Song 1", 120, 60)  # Duplicate title
        ]
        result2 = merge_duplicate_tracks(tracks2)
        assert len(result2) == 2, "Should merge duplicates"
        
        # Verify merged track kept earlier start time
        for track in result2:
            if track.title == "Song 1":
                assert track.start == 0, "Should keep earlier start time"
                assert track.duration == 60, "Should stay the same duration"
        
        print("merge_duplicate_tracks test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise


def test_split_track():
    """Test the split_track function."""
    try:
        # Create test files and directories
        test_dir = os.getcwd() + "\\test\\"
        input_file = test_dir + "audio.mp3"
        output_dir = test_dir + "output\\"
        thumbnail = test_dir + "cover.jpeg"
        
        # Ensure test directories exist
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a test audio file with proper mp3 data
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=5',
            '-c:a', 'mp3', '-b:a', '192k', input_file
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        # Create a test thumbnail
        test_image = Image.new('RGB', (100, 100), color='red')
        test_image.save(thumbnail)
        
        # Create test track
        track = Track("Test Artist - Test Song", 0, 30)
            
        # Test split
        output_file = split_track(input_file, track, thumbnail, output_dir)
        
        # Verify output file exists
        assert os.path.exists(output_file), "Output file was not created"
        assert os.path.getsize(output_file) > 0, "Output file is empty"
        
        # Clean up
        os.remove(input_file)
        os.remove(thumbnail)
        os.remove(output_file)
        
        print("split_track test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

def test_crop_thumbnail():
    """Test the crop_thumbnail function."""
    try:
        # Test case 1: Basic crop
        input_file = os.getcwd() + "\\test\\cover_test.jpeg"
        output_dir = os.getcwd() + "\\test\\output\\"
        
        # Ensure test directories exist
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a test image
        test_image = Image.new('RGB', (1200, 800), color='red')
        test_image.save(input_file)
        
        # Test crop
        output_file = crop_thumbnail(input_file, output_dir)
        
        # Verify output file exists and is correct size
        assert os.path.exists(output_file), "Output file was not created"
        assert os.path.getsize(output_file) > 0, "Output file is empty"
        
        # Verify dimensions are square
        with Image.open(output_file) as img:
            width, height = img.size
            assert width == 1200, "Output image width should be same"
            assert height == 674, "Output image height should be shorter, was " + str(height)
        
        # Clean up
        os.remove(input_file)
        os.remove(output_file)
        
        print("crop_thumbnail test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

def test_split():
    """Test the split function."""
    try:
        # Test case 1: Basic split
        input_file = os.getcwd() + "\\test\\test_audio.wav"
        thumbnail = os.getcwd() + "\\test\\test_thumb.jpg"
        new_thumbnail = os.getcwd() + "\\test\\output\\new_cover.jpeg"
        output_dir = os.getcwd() + "\\test\\output\\"
        tracks1 = [
            Track("Song 1", 0, 60),
            Track("Song 2", 60, 60)
        ]
        
        # Ensure test directories exist
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create test audio file
        with wave.open(input_file, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(44100)
            for i in range(44100):  # 1 second of audio
                value = struct.pack('h', int(32767.0*0.5))
                f.writeframes(value)
        
        # Create test thumbnail
        test_image = Image.new('RGB', (1200, 800), color='red')
        test_image.save(thumbnail)
        
        # Test split
        output_files = split(input_file, thumbnail, tracks1, output_dir, output_dir)
        
        # Verify output files exist
        assert len(output_files) == 2, f"Expected 2 files, found {len(output_files)} instead"

        for file in output_files:
            assert os.path.exists(file), f"Output file {file} was not created"
            assert os.path.getsize(file) > 0, f"Output file {file} is empty"
        
        assert os.path.exists(new_thumbnail), "Thumbnail wasnt converted"
        
        # Clean up
        os.remove(input_file)
        os.remove(thumbnail)
        os.remove(new_thumbnail)
        for file in output_files:
            os.remove(file)
        
        print("split test passed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

def main():
    pass

if __name__ == "__main__":
    test_check_ffmpeg()
    test_merge_duplicate_tracks()
    test_split_track()
    test_crop_thumbnail()
    test_split()
