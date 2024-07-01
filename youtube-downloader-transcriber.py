import os
import time
import ffmpeg
import whisper
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# Supported video file extensions
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')

def download_video(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"Downloaded: {info['title']}")
            return filename
        except Exception as e:
            print(f"Error downloading {video_url}: {str(e)}")
            return None

def get_channel_videos(channel_url):
    ydl_opts = {
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if 'entries' in result:
            return [entry['url'] for entry in result['entries']]
    return []

def video_to_audio(video_path, audio_path):
    try:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, acodec='libmp3lame')
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        return audio_path
    except ffmpeg.Error as e:
        print(f"FFmpeg error converting video to audio {video_path}:")
        print(f"FFmpeg stdout: {e.stdout.decode('utf8')}")
        print(f"FFmpeg stderr: {e.stderr.decode('utf8')}")
        return None
    except Exception as e:
        print(f"Error converting video to audio {video_path}: {e}")
        return None

def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio {audio_path}: {e}")
        return None

def process_video(video_url, output_folder):
    download_folder = os.path.join(output_folder, "downloads")
    audio_folder = os.path.join(output_folder, "audios")
    transcript_folder = os.path.join(output_folder, "transcripts")

    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(audio_folder, exist_ok=True)
    os.makedirs(transcript_folder, exist_ok=True)

    # Download video
    video_path = download_video(video_url, download_folder)
    if not video_path:
        return

    # Convert to audio
    audio_path = os.path.join(audio_folder, os.path.splitext(os.path.basename(video_path))[0] + ".mp3")
    audio_path = video_to_audio(video_path, audio_path)
    if not audio_path:
        return

    # Transcribe audio
    transcript = transcribe_audio(audio_path)
    if transcript:
        transcript_path = os.path.join(transcript_folder, os.path.splitext(os.path.basename(video_path))[0] + ".txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Processed: {video_path}")
    else:
        print(f"Failed to process: {video_path}")

    # Optionally, remove the original video file to save space
    os.remove(video_path)

def estimate_time(num_videos, avg_time_per_video=300):  # Assuming an average of 5 minutes per video
    total_seconds = num_videos * avg_time_per_video
    return timedelta(seconds=total_seconds)

def main(channel_url, output_folder, batch_size=5, max_workers=4):
    video_urls = get_channel_videos(channel_url)
    total_videos = len(video_urls)
    print(f"Found {total_videos} videos in the channel")
    
    estimated_time = estimate_time(total_videos)
    print(f"Estimated total processing time: {estimated_time}")

    start_time = time.time()
    processed_videos = 0
    batches = [video_urls[i:i + batch_size] for i in range(0, len(video_urls), batch_size)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"\nProcessing batch {batch_num}/{len(batches)}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_video, video_url, output_folder) for video_url in batch]
            for future in as_completed(futures):
                future.result()
                processed_videos += 1
                
                # Update progress
                elapsed_time = time.time() - start_time
                videos_per_second = processed_videos / elapsed_time
                estimated_remaining = (total_videos - processed_videos) / videos_per_second
                print(f"Progress: {processed_videos}/{total_videos} videos processed")
                print(f"Estimated time remaining: {timedelta(seconds=int(estimated_remaining))}")

        # Cooling periods
        if batch_num % 2 == 0:  # Every 2 batches
            print("Taking a 5-minute break for cooling...")
            time.sleep(300)  # 5 minutes
        if batch_num % 6 == 0:  # Every 6 batches
            print("Taking a 30-minute break for extended cooling...")
            time.sleep(1800)  # 30 minutes

    total_time = time.time() - start_time
    print(f"\nAll videos processed. Total time taken: {timedelta(seconds=int(total_time))}")

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/channel/CHANNEL_ID_HERE/videos"  # Replace with the actual channel URL
    output_folder = "output"  # Replace with your desired output directory
    main(channel_url, output_folder)
