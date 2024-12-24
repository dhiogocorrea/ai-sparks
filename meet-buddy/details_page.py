# details_page.py

import streamlit as st
import os
import pickle
import pandas as pd
import math
import matplotlib.pyplot as plt
from audio_sync_component import audio_sync_player

def show_details(pickle_filename, pickle_dir='meetings/'):
    """
    Displays detailed information from a pickle file.

    Parameters:
    - pickle_filename (str): The name of the pickle file to display.
    - pickle_dir (str): Directory where pickle files are stored.
    """
    pickle_path = os.path.join(pickle_dir, pickle_filename)
    
    # Load pickle data
    try:
        with open(pickle_path, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        st.error(f"Failed to load pickle file: {e}")
        return
    
    knowledge = data.knowledge
    speaker_outputs = data.speakers_dialog
    
    # Ensure 'knowledge' is a dictionary
    if not isinstance(knowledge, dict):
        st.error("The 'knowledge' attribute is not a dictionary.")
        return
    
    # Page Title
    st.title(f"📄 Details for `{pickle_filename}`")
    
    # Summarization Section
    st.header("📝 Meeting Summary")
    summarization = knowledge.get('summarization', 'No summary available.')
    st.write(summarization)
    
    st.markdown("---")
    
    # Attendance Details Section
    st.header("👥 Attendance")
    attendance = knowledge.get('attendance', [])
    if attendance:
        attendance_df = pd.DataFrame(attendance)
        attendance_df = attendance_df.rename(columns={
            'name': '🧑 Speaker',
            'role': '💼 Role'
        })
        st.table(attendance_df)
    else:
        st.info("No attendance data available.")
    
    st.markdown("---")
    
    # Key Decisions Section
    st.header("✅ Key Decisions")
    key_decisions = knowledge.get('key_decisions', [])
    if key_decisions:
        decisions_df = pd.DataFrame(key_decisions)
        decisions_df = decisions_df.rename(columns={
            'decision_description': '📝 Decision Description',
            'responsible_party': '👤 Responsible Party'
        })
        st.table(decisions_df)
    else:
        st.info("No key decisions recorded.")
    
    st.markdown("---")
    
    # Topics Discussed Section
    st.header("📌 Topics Discussed")
    topics = knowledge.get('topics', [])
    if topics:
        for idx, topic in enumerate(topics, 1):
            with st.expander(f"🔹 Topic {idx}: {topic.get('topic_name', 'Unnamed Topic')}"):
                st.write(topic.get('brief_overview', 'No overview available.'))
    else:
        st.info("No topics available.")
    
    st.markdown("---")
    
    # Tasks per Speaker Section
    st.header("🗂️ Tasks Assigned")
    tasks = knowledge.get('tasks_per_speaker', [])
    if tasks:
        tasks_df = pd.DataFrame(tasks)
        tasks_df = tasks_df.rename(columns={
            'task_description': '📋 Task Description',
            'assigned_to': '👤 Assigned To',
            'deadline': '⏰ Deadline'
        })
        tasks_df['⏰ Deadline'] = tasks_df['⏰ Deadline'].fillna('Not Set')
        st.table(tasks_df)
    else:
        st.info("No tasks assigned.")
    
    st.markdown("---")
    
    # Key Questions and Answers Section
    st.header("❓ Questions and Answers")
    qa = knowledge.get('questions_answers', [])
    if qa:
        for idx, pair in enumerate(qa, 1):
            with st.expander(f"🔹 Q{idx}: {pair.get('question', 'No question provided')}"):
                st.write(f"**A:** {pair.get('answer', 'No answer provided.')}")
    else:
        st.info("No questions and answers recorded.")
    
    st.markdown("---")
    
    # Next Steps and Follow-Up Meetings Section
    st.header("📅 Next Steps and Follow-Up")
    
    # Next Steps
    next_steps = knowledge.get('next_steps', [])
    if next_steps:
        st.subheader("🔜 Next Steps")
        next_steps_df = pd.DataFrame(next_steps)
        next_steps_df = next_steps_df.rename(columns={
            'action': '📝 Action',
            'assigned_to': '👤 Assigned To',
            'deadline': '⏰ Deadline'
        })
        next_steps_df['⏰ Deadline'] = next_steps_df['⏰ Deadline'].fillna('Not Set')
        st.table(next_steps_df)
    else:
        st.info("No next steps recorded.")
    
    # Follow-Up Meeting
    follow_up = knowledge.get('follow_up_meeting', {})
    if follow_up:
        st.subheader("🔁 Follow-Up Meeting")
        follow_up_date = follow_up.get('date', 'No date specified.')
        follow_up_purpose = follow_up.get('purpose', 'No purpose specified.')
        st.markdown(f"**📅 Date:** {follow_up_date}")
        st.markdown(f"**📌 Purpose:** {follow_up_purpose}")
    else:
        st.info("No follow-up meeting scheduled.")
    
    st.markdown("---")
    
    # Overall Sentiment Section
    st.header("😊 Overall Sentiment")
    overall_sentiment = knowledge.get('overall_sentiment', 'N/A').capitalize()
    sentiment_color = {
        'Positive': '#4CAF50',   # Green
        'Neutral': '#9E9E9E',    # Gray
        'Negative': '#F44336'    # Red
    }.get(overall_sentiment, '#000000')  # Default to black
    
    st.markdown(f"""
    <div style="background-color:{sentiment_color}; padding: 10px; border-radius: 5px;">
        <h3 style="color:white; text-align:center;">{overall_sentiment}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sentiment per Speaker Section
    st.header("👥 Sentiment per Speaker")
    sentiments = knowledge.get('sentiment_per_speaker', [])
    if sentiments:
        sentiments_df = pd.DataFrame(sentiments)
        sentiments_df = sentiments_df.rename(columns={
            'speaker': '🗣️ Speaker',
            'sentiment': '😊 Sentiment'
        })
        st.table(sentiments_df)

    else:
        st.info("No sentiment data available.")
    
    st.markdown("---")

    talk_data = []
    for output in speaker_outputs:
        speaker = output.speaker if output.speaker else "Unknown Speaker"
        
        # start_time, end_time in seconds
        start_sec = output.start_time
        end_sec = output.end_time
        
        if start_sec is None or end_sec is None:
            continue
        
        # Total speaking duration in seconds
        total_speaking_time = end_sec - start_sec
        
        # Identify which minute bins are touched by this utterance
        start_minute = int(math.floor(start_sec / 60))
        end_minute = int(math.floor(end_sec / 60))
        
        # Distribute the utterance time across all minutes it spans
        for minute in range(start_minute, end_minute + 1):
            # Calculate the start and end (in seconds) for this minute bin
            bin_start_sec = minute * 60
            bin_end_sec = (minute + 1) * 60
            
            # The overlap between [start_sec, end_sec] and [bin_start_sec, bin_end_sec]
            overlap_start = max(start_sec, bin_start_sec)
            overlap_end = min(end_sec, bin_end_sec)
            
            # If there's overlap, calculate the duration
            if overlap_end > overlap_start:
                overlap_duration = overlap_end - overlap_start
                talk_data.append({
                    "minute": minute,
                    "speaker": speaker,
                    "talk_time_seconds": overlap_duration
                })
    
    # 2. Convert to a DataFrame
    if len(talk_data) > 0:
        df_talk = pd.DataFrame(talk_data)
        
        # 3. Aggregate talk times per speaker per minute
        df_agg = df_talk.groupby(["minute", "speaker"], as_index=False)["talk_time_seconds"].sum()
        
        # 4. Pivot so each speaker is a column, minutes are rows
        pivot_df = df_agg.pivot(index="minute", columns="speaker", values="talk_time_seconds").fillna(0)
        
        st.markdown("## 🗣️ Speaking Time per Minute")
        st.write(
            "Below is a line chart that shows how many seconds each speaker talks in each minute of the audio."
        )
        
        # 5. Plot with Streamlit's built-in line_chart
        st.line_chart(pivot_df)
        
        # If you prefer matplotlib, you could do:
        # fig, ax = plt.subplots()
        # pivot_df.plot(ax=ax)
        # ax.set_xlabel("Minute")
        # ax.set_ylabel("Speaking Time (seconds)")
        # ax.set_title("Speaker Speaking Time per Minute")
        # st.pyplot(fig)
    else:
        st.info("No speaking data available to plot.")

    st.markdown("---")
    
    # Risks or Issues Identification Section
    st.header("⚠️ Risks and Issues")
    risks_issues = knowledge.get('risks_issues', [])
    if risks_issues:
        for idx, risk in enumerate(risks_issues, 1):
            st.markdown(f"**{idx}.** {risk.get('risk_issue_description', 'No description provided.')}")
    else:
        st.info("No risks or issues identified.")
    
    st.markdown("---")
    
    # References to Documents or Resources Section
    st.header("📚 References")
    references = knowledge.get('references', [])
    if references:
        for idx, ref in enumerate(references, 1):
            st.markdown(f"**{idx}.** {ref.get('reference', 'No reference provided.')}")
    else:
        st.info("No references available.")
    
    st.markdown("---")

    st.markdown("---")
    
    # ### Audio Player with Synchronized Transcript ###
    st.header("🎧 Audio Playback with Transcript")
    
    # Path to the audio file
    audio_path = data.audio_path  # Ensure this path is accessible
    if not os.path.isfile(audio_path):
        st.error(f"Audio file not found at `{audio_path}`.")
    else:
        # Prepare transcript data
        speaker_outputs = data.speakers_dialog  # List[SpeakerOutput]
        transcript = [
            {
                "start_time": output.start_time,
                "end_time": output.end_time,
                "speaker": output.speaker if output.speaker else "Unknown Speaker",
                "text": output.text if output.text else ""
            }
            for output in speaker_outputs
        ]
        
        # Use the custom component
        audio_sync_player(data.audio_path, transcript)
    
    st.markdown("---")
    
    # Back Button
    if st.button("🔙 Back to Home"):
        st.session_state.page = 'home'
        st.rerun()
