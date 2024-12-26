import ffmpeg

def mp4_to_wav(
    input_file: str,
    output_file: str,
    sample_rate: int = 16000,
    channels: int = 1
):
    """
    Converts the MP4 file (input_file) to a WAV file (output_file)
    using ffmpeg-python. By default, converts to mono (1 channel) 
    at 16kHz for speech processing.
    """
    stream = (
        ffmpeg
        .input(input_file)
        # Configure audio parameters with output(...)
        .output(
            output_file,
            ar=sample_rate,  # Audio sample rate (Hz)
            ac=channels,     # Number of audio channels
            format='wav'     # Output format = WAV
        )
        .overwrite_output()  # Overwrite existing files
    )

    ffmpeg.run(stream)

def cut_video(input_file: str,
              output_file: str,
              start_time: float, 
              end_time: float
):
    duration = end_time - start_time
    (
        ffmpeg
        .input(input_file, ss=start_time, t=duration)
        .output(output_file, c="copy")
        .overwrite_output()
        .run()
    )