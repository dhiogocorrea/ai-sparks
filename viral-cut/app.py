import streamlit as st
import os
import json

from pipeline import process

# -----------------------------------------------------------------------
# Pages / Views
# -----------------------------------------------------------------------
def show_home():
    st.title("Video Upload & Available Cuts")

    # 1) Upload Section
    st.header("Upload a new MP4")
    uploaded_file = st.file_uploader("Choose a .mp4 file", type=["mp4"])
    if uploaded_file is not None:
        # Save the uploaded file to the 'videos/' folder (create if needed)
        videos_folder = "videos"
        os.makedirs(videos_folder, exist_ok=True)

        file_path = os.path.join(videos_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File saved to {file_path}")

        # Process button
        if st.button("Process this video"):
            with st.spinner("Processing..."):
                # Call your pipeline
                process(file_path)
            st.success("Video processed! Cuts created in 'video_cuts/' folder.")

    # 2) List Existing JSON Files
    st.header("Available Cuts for Processed Videos")

    video_cuts_folder = "video_cuts"
    if not os.path.exists(video_cuts_folder):
        st.info("No 'video_cuts' folder yet. Process a video first.")
        return

    # Collect all JSON files
    json_files = [f for f in os.listdir(video_cuts_folder) if f.endswith(".json")]
    if not json_files:
        st.info("No JSON files found in 'video_cuts' folder.")
        return

    # Display each JSON file with a "Details" button
    for json_file in json_files:
        st.write(f"**File**: `{json_file}`")
        details_key = f"details_{json_file}"

        if st.button("Details", key=details_key):
            # Store selected JSON in session_state, then go to the details page
            st.session_state.selected_json = json_file
            st.session_state.page = "details"
            st.rerun()


def show_details():
    st.title("Cut Details")

    # If user arrived here without a selected JSON, show warning
    if "selected_json" not in st.session_state:
        st.warning("No JSON selected. Go back to the Home Page.")
        return

    # Load the JSON data (list of cuts)
    json_file = st.session_state.selected_json
    json_path = os.path.join("video_cuts", json_file)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            cuts = json.load(f)
    except Exception as e:
        st.error(f"Failed to load {json_path}: {e}")
        return

    # Let user pick which cut to view
    cut_index = st.selectbox(
        "Select a cut index:",
        range(len(cuts)),
        format_func=lambda i: f"Cut #{i}"
    )

    cut_data = cuts[cut_index]

    # Display information about the selected cut
    st.subheader(cut_data.get("title", "Untitled"))
    st.write("**Explanation:**", cut_data.get("explanation", ""))
    st.write(
        f"**Time Range**: {cut_data.get('start_time')}s "
        f"to {cut_data.get('end_time')}s"
    )

    # The original video name is (JSON name minus ".json"), e.g. "myvideo.mp4"
    base_filename = json_file.replace(".json", "")  # e.g. "myvideo.mp4"
    # Each cut is named "myvideo.mp4_{index}.mp4"
    mp4_filename = f"{base_filename}_{cut_index}.mp4"
    mp4_path = os.path.join("video_cuts", mp4_filename)

    # If found, display the cut
    if os.path.exists(mp4_path):
        st.video(mp4_path)
    else:
        st.warning(f"No matching MP4 found: {mp4_filename}")

    # Button to go back to home
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()

# -----------------------------------------------------------------------
# Routing Logic
# -----------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    show_home()
elif st.session_state.page == "details":
    show_details()
