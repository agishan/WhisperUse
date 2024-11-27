import os
import whisper
from moviepy.editor import VideoFileClip


def extract_audio_from_video(video_path, audio_path):
    """Extract audio from a video file."""
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec="pcm_s16le")
    video.close()


def transcribe_audio(file_path, model):
    """Transcribe audio using Whisper."""
    return model.transcribe(file_path)["text"]


def create_transcripts(input_folder, output_folder):
    """Transcribe all MP4 and MP3 files in the folder, skipping already transcribed files."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    model = whisper.load_model("base")  # Use the Whisper model

    files_to_process = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".mp4", ".mp3"))
    ]

    print(f"Found {len(files_to_process)} audio/video files in '{input_folder}'.")

    total_files = len(files_to_process)
    for i, file_name in enumerate(files_to_process, start=1):
        file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.txt")

        # Skip transcription if the text file already exists
        if os.path.exists(output_file_path):
            print(f"[{i}/{total_files}] Skipping: {file_name} (already transcribed)")
            continue

        # Handle MP4: Extract audio
        if file_name.lower().endswith(".mp4"):
            audio_path = os.path.join(input_folder, f"{os.path.splitext(file_name)[0]}.wav")
            print(f"[{i}/{total_files}] Extracting audio from video: {file_name}")
            extract_audio_from_video(file_path, audio_path)
            file_to_transcribe = audio_path
        else:
            file_to_transcribe = file_path

        # Transcribe the file
        print(f"[{i}/{total_files}] Transcribing: {file_name}...")
        try:
            transcript = transcribe_audio(file_to_transcribe, model)
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"[{i}/{total_files}] Transcript saved: {output_file_path}")
        except Exception as e:
            print(f"[{i}/{total_files}] Error transcribing {file_name}: {e}")

        # Clean up temporary WAV file if created
        if file_name.lower().endswith(".mp4"):
            os.remove(audio_path)

    print("Transcription process completed!")


if __name__ == "__main__":
    input_folder = input("Enter the path to the folder containing MP4/MP3 files: ").strip()
    output_folder = input("Enter the path to the output folder for transcripts: ").strip()
    create_transcripts(input_folder, output_folder)
