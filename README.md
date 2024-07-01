# YouTube Channel Downloader and Transcriber

This project downloads all videos from a YouTube channel, converts them to audio, and then transcribes the audio content. It's designed to handle large numbers of videos efficiently, with built-in cooling periods to prevent overheating of the system during long processing sessions.

## Features

- Downloads all videos from a specified YouTube channel
- Converts videos to MP3 format
- Transcribes audio content to text
- Multi-threading for faster processing
- Progress tracking and time estimation
- Automatic cooling periods to prevent system overheating

## Requirements

- Python 3.7+
- FFmpeg
- yt-dlp
- ffmpeg-python
- whisper

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/ekatraone/youtube_channel_transcription.git
   cd youtube-channel-downloader-transcriber
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg:
   - On macOS (using Homebrew):
     ```
     brew install ffmpeg
     ```
   - On Windows:
     Download from https://ffmpeg.org/download.html and add it to your system PATH.
   - On Linux (Ubuntu/Debian):
     ```
     sudo apt-get update
     sudo apt-get install ffmpeg
     ```

## Usage

1. Open `youtube_downloader_transcriber.py` and replace `CHANNEL_ID_HERE` with the actual YouTube channel ID or full channel URL.
2. Set the `output_folder` variable to your desired output directory.
3. Run the script:
   ```
   python youtube_downloader_transcriber.py
   ```

The script will create three subdirectories in the output folder:
- `downloads`: Contains the downloaded video files (these are deleted after processing to save space)
- `audios`: Contains the extracted audio files in MP3 format
- `transcripts`: Contains the transcribed text files

## Customization

You can adjust the following parameters in the `main()` function call:
- `batch_size`: Number of videos to process in each batch (default: 5)
- `max_workers`: Number of concurrent threads to use (default: 4)

## License

This project is open-source and available under the MIT License.
