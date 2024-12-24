import streamlit as st
import streamlit.components.v1 as components
import json
import base64

def get_audio_data_url(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    b64_encoded = base64.b64encode(audio_data).decode("utf-8")
    return f"data:audio/wav;base64,{b64_encoded}"

def audio_sync_player(audio_file, transcript):
    """
    transcript is expected to be a list of dicts like:
    [
       {
         "speaker": "Alice",
         "start_time": 0.0,
         "end_time": 5.2,
         "text": "Hello, everyone!"
       },
       ...
    ]
    Each dict must have 'start_time' and 'end_time' in seconds (float).
    """
    
    # Convert transcript to JSON string
    transcript_json = json.dumps(transcript)

    audio_data_url = get_audio_data_url(audio_file)

    # HTML/JS code
    html_code = f"""
<style>
    .transcript {{
        max-height: 300px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
    }}
    .highlight {{
        background-color: yellow;
    }}
    .speaker {{
        font-weight: bold;
    }}
</style>

<audio id="audioPlayer" controls>
    <source src="{audio_data_url}" type="audio/wav">
    Your browser does not support the audio element.
</audio>

<div class="transcript" id="transcript"></div>

<script>
    const transcript = {transcript_json};
    const audio = document.getElementById('audioPlayer');
    const transcriptDiv = document.getElementById('transcript');

    // Helper function: convert float seconds to "hh:mm:ss"
    function formatTime(seconds) {{
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return String(h).padStart(2, '0') + ':' +
               String(m).padStart(2, '0') + ':' +
               String(s).padStart(2, '0');
    }}

    // Populate transcript
    transcript.forEach((item, index) => {{
        const p = document.createElement('p');
        p.id = 'transcript-' + index;

        // fallback for missing speaker
        const speaker = item.speaker ? item.speaker : "Unknown Speaker";

        // Convert start_time and end_time to hh:mm
        const startTimeStr = formatTime(item.start_time);
        const endTimeStr = formatTime(item.end_time);

        // Include start/end time in the transcript line
        p.innerHTML = `<span class="speaker">${{speaker}}</span> [${{startTimeStr}} - ${{endTimeStr}}]: ${{item.text}}`;
        transcriptDiv.appendChild(p);
    }});

    // Highlight current transcript
    audio.ontimeupdate = function() {{
        const currentTime = audio.currentTime;
        transcript.forEach((item, index) => {{
            const p = document.getElementById('transcript-' + index);
            if (currentTime >= item.start_time && currentTime <= item.end_time) {{
                p.classList.add('highlight');
                p.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
            }} else {{
                p.classList.remove('highlight');
            }}
        }});
    }};
</script>
"""

    components.html(html_code, height=500)
