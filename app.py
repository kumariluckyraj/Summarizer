import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt template for Gemini
prompt_template = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points
within 250 words. Please provide the summary of the text given here: """

# Function to extract video ID from YouTube URL
def get_video_id(url):
    query = urlparse(url).query
    params = parse_qs(query)
    return params.get("v", [None])[0]

# Function to get transcript
def extract_transcript(youtube_video_url):
    try:
        from urllib.parse import urlparse, parse_qs
        query = urlparse(youtube_video_url).query
        video_id = parse_qs(query).get("v", [None])[0]

        if not video_id:
            st.error("Invalid YouTube URL!")
            return None

        # Fetch transcript (old version)
        transcript_snippets = YouTubeTranscriptApi().fetch(video_id)

        # Combine all text
        transcript = " ".join([snippet.text for snippet in transcript_snippets])
        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Function to generate summary using Google Gemini
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit app UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

# Show thumbnail if URL is valid
if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

# Button to fetch transcript and generate summary
if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.warning("Please enter a YouTube video link!")
    else:
        with st.spinner("Fetching transcript..."):
            transcript_text = extract_transcript(youtube_link)

        if transcript_text:
            with st.spinner("Generating summary..."):
                summary = generate_gemini_content(transcript_text, prompt_template)

            if summary:
                st.markdown("### Detailed Notes:")
                st.write(summary)
        else:
            st.error("Transcript not available or could not be fetched.")
