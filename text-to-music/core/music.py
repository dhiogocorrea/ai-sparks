import music21
import pretty_midi
import soundfile as sf
from pydub import AudioSegment

# Define the drum MIDI mapping
DRUM_MIDI_MAP = {
    "BassDrum": 36,     # Kick Drum
    "SnareDrum": 38,    # Snare Drum
    "HiHat": 42,        # Closed Hi-Hat
    "Cymbals": 49,      # Crash Cymbal
    "Handbell": 53,     # Handbell
    # Add more mappings as needed
}

def dynamic_to_velocity(dynamic_mark):
    """
    Convert a textual dynamic marking (e.g., 'pp', 'p', 'mp', 'mf', 'f', 'ff')
    into a MIDI velocity value (0-127).
    """
    dynamic_map = {
        "pp": 30,
        "p": 45,
        "mp": 60,
        "mf": 75,
        "f": 90,
        "ff": 110
    }
    return dynamic_map.get(dynamic_mark.lower(), 64)  # default to 64

def generate_midi(music_xml: str):
    score = music21.converter.parse(music_xml)
    return score


def midi_to_mp3(midi_file: str, output_mp3_file: str, sf2_file: str = 'FluidR3_GM.sf2'):
    """
    Convert a MIDI file to an MP3 using a SoundFont for high-quality sample-based synthesis.

    :param midi_file: Path to the input MIDI file (e.g., 'input.mid').
    :param sf2_file:  Path to the SoundFont file (e.g., 'FluidR3_GM.sf2').
    :param output_mp3_file: Path for the output MP3 (default: 'output.mp3').
    """

    # 1. Load MIDI as a PrettyMIDI object
    midi_data = pretty_midi.PrettyMIDI(midi_file)

    # 2. Synthesize the MIDI to raw audio with your chosen SoundFont
    #    Returns a NumPy array of shape (n_samples,) in float32
    audio_wave = midi_data.fluidsynth(sf2_path=sf2_file)
    sample_rate = 44100  # fluidsynth default sample rate

    # 3. Save this audio to a temporary WAV file
    temp_wav_file = "temp_output.wav"
    sf.write(temp_wav_file, audio_wave, samplerate=sample_rate)

    # 4. Convert the temporary WAV file to MP3 using pydub
    audio_segment = AudioSegment.from_wav(temp_wav_file)
    audio_segment.export(output_mp3_file, format="mp3")

    print(f"Conversion complete! MP3 saved to: {output_mp3_file}")
