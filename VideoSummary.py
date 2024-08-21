import streamlit as st
from pydub import AudioSegment
import tempfile
import os
import google.generativeai as genai

# Configure the Google API key using st.secrets
GOOGLE_API_KEY = "AIzaSyBikV0v1ltCUIsVoLProMqJgx88fXNr6T0"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

def summarize_segment(audio_file_path, start_time, end_time):
    """Summarize a specific segment of the podcast."""
    try:
        # Load the audio file and extract the segment
        audio = AudioSegment.from_file(audio_file_path)
        segment = audio[start_time:end_time]
        
        # Save the segment to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            segment.export(tmp_file.name, format="mp3")
            segment_path = tmp_file.name

        # Use the Google Generative AI to summarize the audio segment
        model = genai.GenerativeModel("gemini-1.5-flash")
        audio_file = genai.upload_file(path=segment_path)
        response = model.generate_content([
            "Please summarize the following podcast segment.",
            audio_file
        ])
        return response.text

    except Exception as e:
        st.error(f"Error during summarization: {e}")
        return None

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary file and return the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None

# Streamlit app interface
st.title('Podcast Highlights Extractor')

with st.expander("About this app"):
    st.write("""
        This app processes podcast episodes and extracts key highlights or summaries from the audio.
        Upload your podcast file in WAV or MP3 format and get concise summaries of each segment.
    """)

audio_file = st.file_uploader("Upload Podcast File", type=['wav', 'mp3'])
if audio_file is not None:
    audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
    st.audio(audio_path)

    # Assume a fixed segment duration (e.g., 5 minutes) for simplicity
    segment_duration_ms = 5 * 60 * 1000  # 5 minutes in milliseconds
    audio = AudioSegment.from_file(audio_path)
    total_duration_ms = len(audio)

    segment_start = 0
    summaries = []
    
    if st.button('Extract Highlights'):
        with st.spinner('Processing...'):
            while segment_start < total_duration_ms:
                segment_end = min(segment_start + segment_duration_ms, total_duration_ms)
                summary = summarize_segment(audio_path, segment_start, segment_end)
                if summary:
                    summaries.append((segment_start, segment_end, summary))
                segment_start += segment_duration_ms

        for i, (start, end, summary) in enumerate(summaries):
            st.subheader(f"Segment {i + 1}: {start // 1000 // 60}:{start // 1000 % 60:02d} - {end // 1000 // 60}:{end // 1000 % 60:02d}")
            st.info(summary)