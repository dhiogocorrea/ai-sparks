import os
from core.agent import MusicalAgent
from core.music import generate_midi, midi_to_mp3

def process(description: str, name: str):
    name = f'songs/{name}'

    if os.path.exists(f'{name}.xml'):
        with open(f'{name}.xml', 'r', encoding='utf-8') as f:
            response = f.read()
    else:
        agent = MusicalAgent()
        response = agent.invoke(description)

        with open(f'{name}.xml', 'w', encoding='utf-8') as f:
            f.write(response)

    if os.path.exists(f'{name}.midi') == False:
        score = generate_midi(music_xml=response)
        score.write('midi', fp=f'{name}.midi')

    midi_to_mp3(f'{name}.midi', f'{name}.mp3')


def process_audiogen():
    import torchaudio
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write

    model = MusicGen.get_pretrained('facebook/musicgen-melody')
    model.set_generation_params(duration=8)  # generate 8 seconds.
    wav = model.generate_unconditional(4)    # generates 4 unconditional audio samples
    descriptions = ['happy rock', 'energetic EDM', 'sad jazz']
    wav = model.generate(descriptions)  # generates 3 samples.

    melody, sr = torchaudio.load('assets/rock-progressif-239253.mp3')
    # generates using the melody from the given audio and the provided descriptions.
    wav = model.generate_with_chroma(descriptions, melody[None].expand(3, -1, -1), sr)

    for idx, one_wav in enumerate(wav):
        # Will save under {idx}.wav, with loudness normalization at -14 db LUFS.
        audio_write(f'songs/{idx}', one_wav.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)

if __name__ == '__main__':
    process_audiogen()