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

        # Initialize Google Generative AI model
        model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure this model is valid
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
st.set_page_config(page_title="Podcast Highlights Extractor by Manyike", page_icon=":microphone:", layout="wide")

# Header
st.title('Podcast Highlights Extractor')
st.markdown("""
    <style>
    .main { 
        background-color: #f0f2f6; 
        padding: 2rem; 
    }
    .sidebar { 
        background-color: #ffffff; 
    }
    .stButton > button { 
        background-color: #4CAF50; 
        color: white; 
    }
    .stButton > button:hover { 
        background-color: #45a049; 
    }
    </style>
    """, unsafe_allow_html=True)

with st.expander("About this app", expanded=True):
    st.write("""
        This app processes podcast episodes and extracts key highlights or summaries from the audio.
        Upload your podcast file in WAV or MP3 format, select the duration of each segment, and click
        'Extract Highlights' to get concise summaries of each segment.
    """)

col1, col2 = st.columns([2, 1])
with col1:
    audio_file = st.file_uploader("Upload Your Podcast File", type=['wav', 'mp3'])
    if audio_file is not None:
        audio_path = save_uploaded_file(audio_file)  # Save the uploaded file and get the path
        if audio_path:
            st.audio(audio_path)
        else:
            st.error("Failed to save the uploaded file. Please try again.")

with col2:
    st.sidebar.header("Segment Settings")
    segment_duration_min = st.sidebar.slider("Segment Duration (minutes)", 1, 10, 5)
    segment_duration_ms = segment_duration_min * 60 * 1000  # Convert to milliseconds

    if st.sidebar.button('Extract Highlights'):
        if audio_file is not None and audio_path:
            with st.spinner('Processing...'):
                try:
                    audio = AudioSegment.from_file(audio_path)
                    total_duration_ms = len(audio)
                    segment_start = 0
                    summaries = []

                    while segment_start < total_duration_ms:
                        segment_end = min(segment_start + segment_duration_ms, total_duration_ms)
                        summary = summarize_segment(audio_path, segment_start, segment_end)
                        if summary:
                            summaries.append((segment_start, segment_end, summary))
                        segment_start += segment_duration_ms

                    for i, (start, end, summary) in enumerate(summaries):
                        st.subheader(f"Segment {i + 1}: {start // 1000 // 60}:{start // 1000 % 60:02d} - {end // 1000 // 60}:{end // 1000 % 60:02d}")
                        st.info(summary)
                except Exception as e:
                    st.error(f"Error during processing: {e}")
        else:
            st.warning("Please upload a podcast file and ensure it is saved correctly before extracting highlights.")
