from TTS.api import TTS

def generate_audio(description: str, speaker_wav_path: str, output_wav_path: str):
    api = TTS("tts_models/pt/cv/vits")
    api.tts_with_vc_to_file(
        description,
        speaker_wav=speaker_wav_path,
        file_path=output_wav_path
    )


if __name__ == '__main__':
    generate_audio('hey mom, what is the meaning of life?', 'speakers/aline.wav', 'test.wav')