# """
# Records the candidate's spoken answer and transcribes it via Groq's
# Whisper endpoint (api.groq.com/openai/v1/audio/transcriptions,
# model="whisper-large-v3" — confirmed current as of this build).

# Imports for sounddevice/numpy/scipy/groq happen lazily inside the
# functions below, not at module load time, so a machine with no working
# microphone (or these packages not installed) can still run every
# typed-answer path in the project without ever hitting an import error.

# Returns duration alongside the transcript because a later phase will
# add a second, independent communication-quality scorer (filler-word
# rate, pace) that needs timing — that scorer must never share inputs
# with the content-correctness Evaluator, so a rambly-but-correct answer
# and a smooth-but-wrong one don't get blended into one score.
# """

# import os
# import tempfile
# import time
# from pathlib import Path

# _SAMPLE_RATE = 16000


# def record_until_enter() -> tuple[str, float]:
#     """Records from the mic until the user presses Enter a second time.
#     Returns (wav_file_path, duration_seconds)."""
#     import sounddevice as sd
#     import numpy as np
#     from scipy.io.wavfile import write as write_wav

#     input("Press Enter to START recording your answer...")
#     frames = []

#     def _callback(indata, frame_count, time_info, status):
#         frames.append(indata.copy())

#     stream = sd.InputStream(samplerate=_SAMPLE_RATE, channels=1, dtype="int16", callback=_callback)
#     stream.start()
#     start = time.time()
#     print("Recording... Press Enter to STOP.")
#     input()
#     stream.stop()
#     stream.close()
#     duration = time.time() - start

#     if not frames:
#         raise RuntimeError("No audio captured — check your microphone")

#     audio = np.concatenate(frames, axis=0)
#     wav_path = Path(tempfile.gettempdir()) / "interview_agent_answer.wav"
#     write_wav(str(wav_path), _SAMPLE_RATE, audio)
#     return str(wav_path), duration


# def transcribe(wav_path: str) -> str:
#     from groq import Groq

#     client = Groq(api_key=os.environ["GROQ_API_KEY"])
#     with open(wav_path, "rb") as f:
#         result = client.audio.transcriptions.create(
#             file=(wav_path, f.read()),
#             model="whisper-large-v3",
#             response_format="json",
#         )
#     return result.text.strip()


# def record_and_transcribe() -> tuple[str, float]:
#     """Returns (raw_transcript, duration_seconds)."""
#     wav_path, duration = record_until_enter()
#     text = transcribe(wav_path)
#     return text, duration
import os
import tempfile
import time
import wave
from pathlib import Path

_SAMPLE_RATE = 16000


def record_until_enter() -> tuple[str, float]:
    """Records from the mic until the user presses Enter a second time.
    Returns (wav_file_path, duration_seconds)."""
    import sounddevice as sd
    import numpy as np
    from scipy.io.wavfile import write as write_wav

    input("Press Enter to START recording your answer...")
    frames = []

    def _callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    stream = sd.InputStream(
        samplerate=_SAMPLE_RATE,
        channels=1,
        dtype="int16",
        callback=_callback
    )

    stream.start()
    start = time.time()

    print("Recording... Press Enter to STOP.")
    input()

    stream.stop()
    stream.close()

    duration = time.time() - start

    if not frames:
        raise RuntimeError("No audio captured — check your microphone")

    audio = np.concatenate(frames, axis=0)

    wav_path = Path(tempfile.gettempdir()) / "interview_agent_answer.wav"
    write_wav(str(wav_path), _SAMPLE_RATE, audio)

    return str(wav_path), duration


def transcribe(wav_path: str) -> str:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    with open(wav_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=(wav_path, f.read()),
            model="whisper-large-v3",
            response_format="json",
        )

    return result.text.strip()


def record_and_transcribe() -> tuple[str, float]:
    """CLI path: records from the local microphone."""
    wav_path, duration = record_until_enter()
    text = transcribe(wav_path)
    return text, duration


def transcribe_audio_bytes(
    audio_bytes: bytes,
    filename: str = "answer.wav"
) -> tuple[str, float]:
    """Browser/Streamlit path: transcribes audio already recorded by st.audio_input()."""

    from groq import Groq

    if not audio_bytes:
        raise ValueError("No audio data received.")

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    suffix = Path(filename).suffix or ".wav"

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as f:
            f.write(audio_bytes)
            temp_path = f.name

        duration = 0.0

        # st.audio_input normally provides WAV audio.
        # Calculate duration from the WAV itself.
        if suffix.lower() == ".wav":
            try:
                with wave.open(temp_path, "rb") as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()

                    if rate > 0:
                        duration = frames / float(rate)
            except Exception:
                duration = 0.0

        with open(temp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=(filename, f.read()),
                model="whisper-large-v3",
                response_format="json",
            )

        transcript = result.text.strip()

        return transcript, duration

    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass