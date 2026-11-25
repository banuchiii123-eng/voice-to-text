
import streamlit as st
from groq import Groq
import os

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="SAAD/AI Voice to Text",
    page_icon="🎙️",
    layout="wide"
)

# --------------------------------
# CUSTOM CSS
# --------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #00d4ff;
}

.subtitle {
    text-align: center;
    color: #aaaaaa;
    font-size: 17px;
}

.stButton>button {
    background-color: #00a8cc;
    color: white;
    border-radius: 10px;
    border: none;
    height: 45px;
    font-weight: bold;
    width: 100%;
}

.stButton>button:hover {
    background-color: #007f99;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------
# HEADER
# --------------------------------

st.markdown(
    '<div class="main-title">🎙️ SAAD/AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI Voice to Text Converter</div>',
    unsafe_allow_html=True
)

st.write("")
st.divider()

st.markdown(
    "### 🎧 Convert Your Voice Into Text"
)

st.write(
    "Upload your audio file, select its language "
    "and convert your voice into text using AI."
)

# --------------------------------
# GROQ API CONNECTION
# --------------------------------

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error(
        "Groq API Key not found! "
        "Please add GROQ_API_KEY in Streamlit Secrets."
    )
    st.stop()

client = Groq(api_key=api_key)

# --------------------------------
# LANGUAGE SELECTION
# --------------------------------

languages = {
    "Auto Detect": None,
    "English": "en",
    "Urdu": "ur",
    "Hindi": "hi",
    "Arabic": "ar",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Turkish": "tr",
    "Chinese": "zh",
    "Japanese": "ja"
}

selected_language = st.selectbox(
    "🌍 Select Audio Language",
    list(languages.keys())
)

# --------------------------------
# AUDIO UPLOAD
# --------------------------------

uploaded_file = st.file_uploader(
    "📁 Upload Your Audio File",
    type=[
        "mp3",
        "wav",
        "m4a",
        "ogg",
        "flac",
        "mp4",
        "mpeg",
        "webm"
    ]
)

if uploaded_file:

    st.audio(
        uploaded_file,
        format=uploaded_file.type
    )

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

# --------------------------------
# TRANSCRIPTION SETTINGS
# --------------------------------

st.markdown("### ⚙️ Transcription Settings")

model = st.selectbox(
    "Choose Whisper Model",
    [
        "whisper-large-v3",
        "whisper-large-v3-turbo"
    ]
)

improve_text = st.checkbox(
    "✨ Improve transcript using GPT-OSS 20B",
    value=True
)

# --------------------------------
# CONVERT AUDIO TO TEXT
# --------------------------------

if st.button("🚀 Convert Voice to Text"):

    if uploaded_file is None:
        st.warning("Please upload an audio file first.")

    else:

        try:
            with st.spinner(
                "🎙️ Converting your voice into text..."
            ):

                audio_bytes = uploaded_file.getvalue()

                transcription_args = {
                    "file": (
                        uploaded_file.name,
                        audio_bytes
                    ),
                    "model": model,
                    "response_format": "json",
                    "temperature": 0.0
                }

                language_code = languages[selected_language]

                if language_code:
                    transcription_args["language"] = language_code

                transcription = client.audio.transcriptions.create(
                    **transcription_args
                )

                transcript = transcription.text

                # --------------------------------
                # AI TEXT IMPROVEMENT
                # --------------------------------

                if improve_text and transcript.strip():

                    with st.spinner(
                        "✨ Improving your transcript..."
                    ):

                        completion = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are an expert transcription editor. "
                                        "Correct grammar, punctuation and formatting. "
                                        "Preserve the original language, meaning "
                                        "and important details. Do not translate "
                                        "or add information."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        "Improve this voice transcript:\n\n"
                                        + transcript
                                    )
                                }
                            ],
                            temperature=0.2
                        )

                        transcript = (
                            completion.choices[0].message.content
                        )

            # --------------------------------
            # DISPLAY RESULTS
            # --------------------------------

            st.success("🎉 Voice Successfully Converted!")

            st.markdown("### 📝 Your Converted Text")

            st.text_area(
                "Transcription Result",
                value=transcript,
                height=300
            )

            st.download_button(
                label="⬇️ Download Transcript",
                data=transcript,
                file_name="saad_voice_transcript.txt",
                mime="text/plain"
            )

            st.info(
                "Your audio has been successfully converted into text!"
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )

# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#888;">
        <h4>SAAD/AI Voice to Text Converter</h4>
        <p>Powered by Groq AI | Built with Streamlit</p>
        <p>Created by Saad ❤️</p>
    </div>
    """,
    unsafe_allow_html=True
)
