"""
STEP 1: AUDIO UPLOAD & TRANSCRIPTION MODULE
===========================================
- Validates audio format, size, and integrity.
- Uses Whisper Automatic Speech Recognition (ASR) to convert audio to text.
"""

import os
import whisper

# Supported audio formats for our app
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]


class AudioValidationError(Exception):
    """Custom error raised when an audio file is invalid, empty, or corrupted."""
    pass


def validate_audio_file(file_path: str) -> bool:
    """
    Checks if the audio file is safe and valid before processing.
    """
    # 1. Check if file exists on disk
    if not os.path.exists(file_path):
        raise AudioValidationError(f"File not found: '{file_path}'")

    # 2. Check file format / extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise AudioValidationError(
            f"Unsupported format '{ext}'. Allowed: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
        )

    # 3. Check for empty or corrupted files
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise AudioValidationError("Audio file is completely empty (0 bytes).")
    
    if file_size < 1024:  # Less than 1 KB is usually corrupted
        raise AudioValidationError("Audio file is corrupted or too small to contain valid speech.")

    return True


def transcribe_audio(file_path: str, model_size: str = "base") -> str:
    """
    Converts audio speech into written text using Whisper.
    """
    # Validate the file first
    validate_audio_file(file_path)

    print(f"[*] Loading Whisper model ('{model_size}')...")
    model = whisper.load_model(model_size)

    print(f"[*] Transcribing audio: {file_path}...")
    result = model.transcribe(file_path)
    transcript = result.get("text", "").strip()

    if not transcript:
        raise AudioValidationError("No human speech was detected in this recording.")

    print("[+] Transcription successful!")
    return transcript


if __name__ == "__main__":
    print("Step 1 module is ready!")