import streamlit as st
import os
from main import generate_audio


def main():
    st.title("Voice Conversion Demo")
    st.write("""
    This app lets you upload a speaker audio (a short .wav clip),
    then generate TTS based on that speaker's voice.
    """)

    st.header("1. Create a New Speaker")

    speaker_name = st.text_input("Speaker name:")
    speaker_wav = st.file_uploader("Upload a WAV file for the speaker:", type=["wav"])

    if st.button("Save Speaker"):
        if speaker_name and speaker_wav is not None:
            # Save the uploaded file as <speaker_name>.wav in speakers/ folder
            speaker_file_path = os.path.join("speakers", f"{speaker_name}.wav")

            with open(speaker_file_path, "wb") as f:
                f.write(speaker_wav.getvalue())

            st.success(f"Speaker '{speaker_name}' saved successfully!")
        else:
            st.error("Please provide both a speaker name and a WAV file.")


    st.header("2. Generate Audio from an Existing Speaker")

    # Gather list of existing speakers (i.e., .wav files in 'speakers/' directory)
    if not os.path.exists("speakers"):
        os.makedirs("speakers")

    speaker_files = [f for f in os.listdir("speakers") if f.endswith(".wav")]
    speaker_options = [os.path.splitext(f)[0] for f in speaker_files]  # remove ".wav"

    if speaker_options:
        selected_speaker = st.selectbox("Select a speaker", speaker_options)
    else:
        st.warning("No saved speakers yet. Please create a new speaker first.")
        selected_speaker = None

    user_text = st.text_area("Enter text to synthesize")

    # Generate button
    if st.button("Generate Audio"):
        if selected_speaker and user_text.strip():
            # Ensure results/ folder exists
            if not os.path.exists("results"):
                os.makedirs("results")

            # Build file paths
            speaker_wav_path = os.path.join("speakers", f"{selected_speaker}.wav")
            output_wav_path = os.path.join("results", f"{selected_speaker}_output.wav")

            try:
                # Generate the audio
                generate_audio(user_text, speaker_wav_path, output_wav_path)

                st.success(f"Generated audio saved to {output_wav_path}!")
                # Display a player for the generated audio
                st.audio(output_wav_path, format="audio/wav")
            except Exception as e:
                st.error(f"Error generating audio: {e}")
        else:
            st.error("Please select a speaker and enter some text.")

if __name__ == "__main__":
    main()