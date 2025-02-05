# streamlit_app.py
import streamlit as st
import os
import uuid
import glob
import json
from datetime import datetime

from main import process_text_to_music

def get_available_styles():
    # Get all JSON files from track_data directory
    json_files = glob.glob(os.path.join('track_data', '*.json'))
    
    # Extract style names from filenames (remove path and extension)
    styles = [os.path.splitext(os.path.basename(f))[0] for f in json_files]
    
    # Create a dictionary with style names
    return {style.replace('_', ' ').title(): style for style in styles}

def list_generated_songs():
    songs = []
    songs_dir = 'songs'
    
    if not os.path.exists(songs_dir):
        return []
        
    # Get all subdirectories (each represents a generation)
    for generation_id in os.listdir(songs_dir):
        generation_path = os.path.join(songs_dir, generation_id)
        if not os.path.isdir(generation_path):
            continue
            
        # Find wav and json files
        wav_files = glob.glob(os.path.join(generation_path, '*.wav'))
        json_files = glob.glob(os.path.join(generation_path, '*.json'))
        
        if not wav_files or not json_files:
            continue
            
        # Get metadata from json
        try:
            with open(json_files[0], 'r') as f:
                metadata = json.load(f)
            
            songs.append({
                'id': generation_id,
                'wav_path': wav_files[0],
                'metadata': metadata,
                'created_at': datetime.fromtimestamp(os.path.getctime(wav_files[0]))
            })
        except Exception as e:
            print(f"Error reading metadata for {generation_id}: {e}")
            
    # Sort by creation date, newest first
    return sorted(songs, key=lambda x: x['created_at'], reverse=True)

def main():
    st.title("MusicGen Web App")
    
    # Tabs for generate and history
    tab1, tab2 = st.tabs(["Generate Music", "Generated Songs"])
    
    with tab1:
        st.write("Select a music style, provide an optional description, and generate a new track!")

        # Generation type selector
        generation_type = st.radio(
            "Generation Type",
            ["Description-Only Generation", "Melody-based Generation"],
            help="Description-Only: Generate music from description only\nMelody-based: Use a reference melody from selected style"
        )

        # Optional text description
        description = st.text_input(
            "Music Description", 
            placeholder="E.g. 'fast-paced melodic rock with heavy drums'"
        )

        # Duration input
        duration = st.number_input("Duration (seconds)", min_value=5, max_value=30, value=30)

        # Style selection only for melody-based generation
        style_id = None
        if generation_type == "Melody-based Generation":
            # Get available styles from track_data folder
            style_options = get_available_styles()
            
            if not style_options:
                st.error("No music styles found. Please make sure there are JSON files in the track_data directory.")
                return

            # User picks one of the available styles
            chosen_style = st.selectbox("Choose a music style:", list(style_options.keys()))
            style_id = style_options[chosen_style]

        # Generate button
        if st.button("Generate Music"):
            if description or generation_type == "Melody-based Generation":
                with st.spinner("Generating music..."):
                    # Generate a unique ID for this generation
                    generation_id = str(uuid.uuid4())
                    
                    # Process the generation
                    process_text_to_music(
                        _id=generation_id,
                        descriptions=[description] if description else [],
                        duration=duration,
                        genre=style_id
                    )

                    st.success("Music generated successfully!")
                    st.rerun()
            else:
                st.warning("Please provide a description or select melody-based generation.")
    
    with tab2:
        st.write("Previously generated songs:")
        
        songs = list_generated_songs()
        
        if not songs:
            st.info("No generated songs found. Generate some music first!")
            return
            
        for song in songs:
            with st.expander(f"Generated on {song['created_at'].strftime('%Y-%m-%d %H:%M:%S')}"):
                # Display metadata
                st.json(song['metadata'])
                
                # Create two columns for the audio players
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Reference Track")
                    if 'asset_path' in song['metadata'] and song['metadata']['asset_path'] is not None and os.path.exists(song['metadata']['asset_path']):
                        st.audio(song['metadata']['asset_path'])
                        # Download button for reference track
                        with open(song['metadata']['asset_path'], "rb") as f:
                            st.download_button(
                                label="Download Reference MP3",
                                data=f,
                                file_name=f"reference_{song['id']}.mp3",
                                mime="audio/mp3"
                            )
                    else:
                        st.info("No reference track available")
                
                with col2:
                    st.subheader("Generated Track")
                    # Audio player for generated track
                    st.audio(song['wav_path'])
                    # Download button for generated track
                    with open(song['wav_path'], "rb") as f:
                        st.download_button(
                            label="Download Generated WAV",
                            data=f,
                            file_name=f"generated_{song['id']}.wav",
                            mime="audio/wav"
                        )
                
                # Display additional information
                st.write("**Generation Details:**")
                if 'descriptions' in song['metadata']:
                    st.write("Description:", song['metadata']['descriptions'][0] if song['metadata']['descriptions'] else "No description")
                if 'genre' in song['metadata'] and song['metadata']['genre'] is not None:
                    st.write("Genre:", song['metadata']['genre'].title())

if __name__ == "__main__":
    main()