import os
import torchaudio
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from agent import MelodyAgent
from jamendo_crawler import JamendoCrawler
import json

def process_text_to_music(
    _id: str,
    descriptions: list[str],
    duration: int = 30,
    genre: str = None
):
    output_dir = f'songs/{_id}'
    if os.path.exists(output_dir) is False:
        os.makedirs(output_dir)

    metadata = {
        'descriptions': descriptions,
        'duration': duration,
        'genre': genre,
        'asset_path': None
    }

    if genre:
        # Melody-based generation
        model = MusicGen.get_pretrained('facebook/musicgen-melody')
        model.set_generation_params(duration=duration)

        agent = MelodyAgent()
        track = agent.invoke(genre=genre, description=' '.join(descriptions))
        
        # Download reference track
        asset_path = JamendoCrawler().download_mp3(track['url'], 'assets')
        metadata['asset_path'] = asset_path
        
        # Load reference track
        melody, sr = torchaudio.load(asset_path)
        
        # Generate with melody guidance
        wav = model.generate_with_chroma(
            descriptions=descriptions,
            melody_wavs=melody.unsqueeze(0),
            melody_sample_rate=sr,
            progress=True
        )
    else:
        # Basic generation
        model = MusicGen.get_pretrained('facebook/musicgen-small')
        model.set_generation_params(duration=duration)
        wav = model.generate(descriptions=descriptions)

    # Save generated audio
    output_path = os.path.join(output_dir, 'generated.wav')
    audio_write(
        output_path,
        wav.cpu()[0],
        model.sample_rate,
        strategy="loudness",
        loudness_compressor=True
    )

    # Save metadata
    metadata_path = os.path.join(output_dir, '0.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return output_path


if __name__ == '__main__':
    _id = str(uuid.uuid4())
    descriptions = ["metal progressive song with odd time signature, like dream theater"]
    process_text_to_music(_id=_id, descriptions=descriptions, asset_path='assets/prog_metal.mp3')