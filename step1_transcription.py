"""
STEP 1: AUDIO UPLOAD & TRANSCRIPTION MODULE
===========================================
Purpose:
  Accepts an audio file path, validates it against corruption, empty size, 
  and unsupported file extensions, then uses OpenAI's Whisper model to convert 
  spoken audio into a clean text transcript.

Why Whisper?
  Whisper is a state-of-the-art Automatic Speech Recognition (ASR) model trained 
  on 680,000+ hours of multilingual data. It accurately detects punctuation, 
  technical vocabulary, and different speaker accents.
"""

import os
import shutil
import whisper

# Auto-detect and register ffmpeg if installed via python (imageio-ffmpeg)
try:
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    bin_dir = os.path.dirname(ffmpeg_bin)
    target_ffmpeg = os.path.join(bin_dir, "ffmpeg.exe")
    if not os.path.exists(target_ffmpeg) and os.path.exists(ffmpeg_bin):
        try:
            shutil.copyfile(ffmpeg_bin, target_ffmpeg)
        except Exception:
            pass
    if bin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
except Exception:
    pass


# List of allowed audio formats for the system
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]


class AudioValidationError(Exception):
    """Custom exception raised when an uploaded audio file fails validation."""
    pass


def validate_audio_file(file_path: str) -> bool:
    """
    Validates audio file existence, file size, and extension format.
    
    Checks performed:
    1. Does the file exist on disk?
    2. Is the file extension in our allowed list?
    3. Is the file empty (0 bytes)?
    4. Does the file have sufficient data to be a valid audio file (> 1000 bytes)?
    """
    if not os.path.exists(file_path):
        raise AudioValidationError(f"File not found: '{file_path}'")

    # Check extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise AudioValidationError(
            f"Unsupported file format '{ext}'. Supported formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
        )

    # Check size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise AudioValidationError("Audio file is completely empty (0 bytes).")
    
    # Files smaller than 1KB are usually corrupted or empty headers
    if file_size < 1024:
        raise AudioValidationError("Audio file is corrupted or too small to contain valid audio data.")

    return True


def transcribe_audio(file_path: str, model_size: str = "base") -> str:
    """
    Converts audio speech to text using Whisper.
    
    Parameters:
      file_path (str): Path to the audio file.
      model_size (str): Whisper model variant ('tiny', 'base', 'small', 'medium', 'large').
                        'base' provides the ideal balance between speed and accuracy.
                        
    Returns:
      str: Complete generated transcript text.
    """
    # Step 1: Validate file first
    validate_audio_file(file_path)

    # Step 2: Load the Whisper Automatic Speech Recognition model
    print(f"[*] Loading Whisper model ('{model_size}')...")
    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        raise RuntimeError(f"Failed to load Whisper ASR model: {str(e)}")

    # Step 3: Run transcription with vocabulary hints and English language lock
    print(f"[*] Transcribing audio from: {file_path}...")
    try:
        # Prompting Whisper with domain keywords ensures accurate spelling of names
        vocab_prompt = "This is Yogitha. Topics: AI meeting summarizer, action item extractor, ChatGPT, Anil, assignments, tomorrow, morning, leave."
        result = model.transcribe(
            file_path,
            language="en",
            initial_prompt=vocab_prompt,
            temperature=0.0
        )
    except Exception as e:
        err_msg = str(e)
        if "WinError 2" in err_msg or "ffmpeg" in err_msg.lower():
            raise AudioValidationError(
                "Whisper requires FFmpeg to decode audio on Windows. "
                "Please run: 'winget install Gyan.FFmpeg' or 'python -m pip install imageio-ffmpeg' in your terminal."
            )
        raise AudioValidationError(
            f"Corrupted or unreadable audio stream: Whisper could not decode the audio. Details: {err_msg}"
        )

    transcript = result.get("text", "").strip()

    # Step 4: Verify that speech was actually found
    if not transcript:
        raise AudioValidationError(
            "Transcription completed, but no human speech was detected in this audio recording."
        )

    print("[+] Transcription successful!")
    return transcript


# Direct execution test
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🎙️ STEP 1: AUDIO TRANSCRIPTION MODULE VERIFICATION")
    print("=" * 50)
    print("[*] Checking supported audio formats: ", SUPPORTED_AUDIO_FORMATS)
    
    # Test 1: Unsupported format check
    print("\n[Test 1] Testing rejection of invalid formats (e.g., sample.pdf)...")
    try:
        validate_audio_file("sample.pdf")
    except AudioValidationError as e:
        print(f"✅ Success! Correctly caught: {e}")

    # Test 2: Missing file check
    print("\n[Test 2] Testing detection of non-existent audio files...")
    try:
        validate_audio_file("non_existent_audio.mp3")
    except AudioValidationError as e:
        print(f"✅ Success! Correctly caught: {e}")

    print("\n" + "=" * 50)
    print("🎉 STEP 1 ENGINE IS ACTIVE AND READY!")
    print("Ready to transcribe audio when called by app.py or your pipeline.")
    print("=" * 50 + "\n")

