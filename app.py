import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


prompt_template = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points
within 250 words. Please provide the summary of the text given here: """


def get_video_id(url):
    query = urlparse(url).query
    params = parse_qs(query)
    return params.get("v", [None])[0]


def extract_transcript(youtube_video_url):
    try:
        from urllib.parse import urlparse, parse_qs
        query = urlparse(youtube_video_url).query
        video_id = parse_qs(query).get("v", [None])[0]

        if not video_id:
            st.error("Invalid YouTube URL!")
            return None

      
        transcript_snippets = YouTubeTranscriptApi().fetch(video_id)

     
        transcript = " ".join([snippet.text for snippet in transcript_snippets])
        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None



st.markdown("""
    <style>
        /* Background gradient */
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Title */
        h1 {
            text-align: center;
            color: #ffcc70;
            font-size: 3rem !important;
            margin-bottom: 20px;
        }

        /* Input */
        .stTextInput>div>div>input {
            border-radius: 12px;
            border: 2px solid #ffcc70;
            padding: 12px;
            background-color: #1c1c1c;
            color: #ffffff;
        }

        div.stButton>button {
            background: linear-gradient(90deg, #ffcc70, #ff8c00);
            color: black;
            border-radius: 12px;
            padding: 12px 28px;
            font-size: 16px;
            border: none;
            font-weight: bold;
            transition: 0.3s;
        }
        div.stButton>button:hover {
            background: linear-gradient(90deg, #ff8c00, #ffcc70);
            transform: scale(1.05);
        }

        /* Notes Card */
        .notes-box {
            background: rgba(255,255,255,0.05);
            border-left: 5px solid #ffcc70;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            font-size: 1.1rem;
            line-height: 1.6;
        }

        /* Thumbnail centering */
        .thumb-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)



st.title(" YouTube Transcript →  Detailed Notes")

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

#  thumbnail if URL is valid
if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.markdown('<div class="thumb-container">', unsafe_allow_html=True)
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", width=450)
        st.markdown('</div>', unsafe_allow_html=True)

# Button to fetch transcript and generate summary
if st.button(" Get Detailed Notes"):
    if not youtube_link:
        st.warning("⚠️ Please enter a YouTube video link!")
    else:
        with st.spinner("⏳ Fetching transcript..."):
            transcript_text = extract_transcript(youtube_link)

        if transcript_text:
            with st.spinner("⚡ Generating summary..."):
                summary = generate_gemini_content(transcript_text, prompt_template)

            if summary:
                st.markdown("##  Detailed Notes:")
                st.markdown(f"<div class='notes-box'>{summary}</div>", unsafe_allow_html=True)
        else:
            st.error("❌ Transcript not available or could not be fetched.")
