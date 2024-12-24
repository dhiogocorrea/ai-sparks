import streamlit as st
import os
import uuid
import pickle
from pipeline import get_meeting
from details_page import show_details  # Import the details page function
import io
import contextlib
import threading
import queue
import time

# Set the directory for pickle files
PICKLE_DIR = 'meetings/'
if not os.path.exists(PICKLE_DIR):
    os.makedirs(PICKLE_DIR)

def list_pickle_files():
    return [f for f in os.listdir(PICKLE_DIR) if f.endswith('.pkl')]

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

class StdoutRedirector:
    def __init__(self, q):
        self.queue = q

    def write(self, message):
        if message.strip() != "":
            self.queue.put(message)

    def flush(self):
        pass  # No action needed

# Initialize session state for tasks and results
if "background_tasks" not in st.session_state:
    st.session_state.background_tasks = {}
if "task_results" not in st.session_state:
    st.session_state.task_results = {}

def process_file(file_path, language, task_id):
    try:
        q = queue.Queue()
        with contextlib.redirect_stdout(StdoutRedirector(q)):
            generated_pickle = get_meeting(file_path, language)
        st.session_state.task_results[task_id] = generated_pickle
    except Exception as e:
        if "task_results" in st.session_state and st.session_state.task_results:
            st.session_state.task_results[task_id] = f"ERROR: {e}"
        st.rerun()
    finally:
        if "background_tasks" in st.session_state and st.session_state.background_tasks:
            st.session_state.background_tasks.pop(task_id, None)

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'English'

# Sidebar Navigation
st.sidebar.title("👫 Meet Buddy")
if st.sidebar.button("🏠 Home"):
    st.session_state.page = 'home'
    st.rerun()

st.title("👫 Meet Buddy")

if st.session_state.page == 'home':
    st.header("📂 Available Meetings")
    pickle_files = list_pickle_files()
    
    if pickle_files:
        selected_pickle = st.selectbox("🔍 Select a meeting:", pickle_files)
        if st.button("🔎 View Details"):
            st.session_state.selected_pickle = selected_pickle
            st.session_state.page = 'details'
            st.rerun()
    else:
        st.info("No pickle files found in the 'meetings/' directory.")
    
    st.markdown("---")
    
    st.header("📤 Upload MP4 File")
    uploaded_file = st.file_uploader("Choose an MP4 file", type="mp4")
    
    # Language Selection Dropdown
    language = st.selectbox(
        "🌐 Select Language",
        options=["English", "Portuguese"],
        index=["English", "Portuguese"].index(st.session_state.selected_language)
    )
    st.session_state.selected_language = language
    
    if uploaded_file is not None:
        temp_dir = "videos/"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Uploaded `{uploaded_file.name}` successfully!")
        
        if st.button("⚙️ Process File"):
            task_id = str(uuid.uuid4())
            thread = threading.Thread(target=process_file, args=(file_path, language, task_id))
            st.session_state.background_tasks[task_id] = thread
            thread.start()
            st.success(f"✅ Processing started with Task ID: {task_id}")
            st.rerun()
    
    st.markdown("---")
    
    st.header("🕒 Ongoing Processes")
    if st.session_state.background_tasks:
        for task_id, thread in st.session_state.background_tasks.items():
            status = "Running" if thread.is_alive() else "Completed"
            st.write(f"**Task ID:** {task_id} - **Status:** {status}")
    else:
        st.info("No ongoing processes.")

elif st.session_state.page == 'details':
    if 'selected_pickle' in st.session_state:
        show_details(st.session_state.selected_pickle)
    else:
        st.error("No pickle file selected.")
        if st.button("🔙 Back to Home"):
            st.session_state.page = 'home'
            st.rerun()

# Background Task Results
st.sidebar.header("🔔 Notifications")
if st.session_state.task_results:
    for task_id, result in list(st.session_state.task_results.items()):
        if isinstance(result, str) and result.startswith("ERROR:"):
            st.sidebar.error(f"Task {task_id} failed: {result}")
        else:
            st.sidebar.success(f"Task {task_id} completed! Generated pickle: `{result}`")
        # Remove the result once displayed
        del st.session_state.task_results[task_id]
