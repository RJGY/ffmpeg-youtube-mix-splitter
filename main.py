import os

from splitter import split
from download import download
from track import Track

video_url = 'https://www.youtube.com/watch?v=KVmtUWJmbNs'
thumbnail_folder = os.getcwd() + '\\temp_download\\'
output_folder = os.getcwd() + '\\output\\'

def main():
    audio, thumbnail, tracks = download(video_url)
    songs = split(audio, thumbnail, tracks, thumbnail_folder, output_folder)
    print(songs)

if __name__ == '__main__':
    main()

