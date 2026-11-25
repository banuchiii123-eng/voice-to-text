
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
    '<div class="subtitle">Multilingual Voice to Text Converter</div>',
    unsafe_allow_html=True
)

st.divider()

st.markdown("### 🎧 Convert Your Voice Into Text")

st.write(
    "Upload your audio, select the input and output languages, "
    "and convert your voice into text using AI."
)

# --------------------------------
# GROQ API
# --------------------------------

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Groq API key not found. Add GROQ_API_KEY in Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# --------------------------------
# LANGUAGE OPTIONS
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
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru",
    "Portuguese": "pt",
    "Italian": "it",
    "Dutch": "nl",
    "Bengali": "bn",
    "Punjabi": "pa",
    "Persian": "fa",
    "Indonesian": "id",
    "Thai": "th",
    "Vietnamese": "vi",
    "Polish": "pl",
    "Swahili": "sw"
}

# --------------------------------
# LANGUAGE SELECTION
# --------------------------------

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎤 Input Language")

    input_language = st.selectbox(
        "Select audio language",
        list(languages.keys()),
        index=0
    )

with col2:
    st.markdown("### 🌍 Output Language")

    output_options = ["Same as Audio"] + [
        lang for lang in languages.keys()
        if lang != "Auto Detect"
    ]

    output_language = st.selectbox(
        "Select text language",
        output_options,
        index=1
    )

# --------------------------------
# AUDIO UPLOAD
# --------------------------------

st.divider()

st.markdown("### 📁 Upload Audio")

uploaded_file = st.file_uploader(
    "Choose your audio file",
    type=[
        "mp3", "wav", "m4a", "ogg",
        "flac", "mp4", "mpeg", "webm"
    ]
)

if uploaded_file:
    st.audio(uploaded_file)

    st.success(
        f"Audio uploaded successfully: {uploaded_file.name}"
    )

# --------------------------------
# SETTINGS
# --------------------------------

st.markdown("### ⚙️ Settings")

whisper_model = st.selectbox(
    "Speech Recognition Model",
    [
        "whisper-large-v3",
        "whisper-large-v3-turbo"
    ]
)

# --------------------------------
# CONVERSION
# --------------------------------

if st.button("🚀 Convert Voice to Text"):

    if uploaded_file is None:

        st.warning("Please upload an audio file first.")

    else:

        try:
            # STEP 1: AUDIO TRANSCRIPTION

            with st.spinner("🎧 Listening to your audio..."):

                audio_data = uploaded_file.getvalue()

                transcription_args = {
                    "file": (
                        uploaded_file.name,
                        audio_data
                    ),
                    "model": whisper_model,
                    "response_format": "json",
                    "temperature": 0.0
                }

                selected_code = languages[input_language]

                if selected_code:
                    transcription_args["language"] = selected_code

                transcription = client.audio.transcriptions.create(
                    **transcription_args
                )

                original_text = transcription.text

            if not original_text.strip():
                st.warning("No speech was detected in this audio.")
                st.stop()

            # STEP 2: LANGUAGE TRANSLATION

            final_text = original_text

            if output_language != "Same as Audio":

                with st.spinner(
                    f"🌍 Translating into {output_language}..."
                ):

                    prompt = f"""
You are a professional multilingual translator.

Translate the following speech transcript into {output_language}.

IMPORTANT RULES:
1. Translate the entire transcript.
2. Use natural and grammatically correct {output_language}.
3. Preserve the original meaning and details.
4. Do not summarize or shorten the transcript.
5. Do not add extra information.
6. Return only the translated text.
7. Use the correct writing system of the target language.

Transcript:

{original_text}
"""

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are an expert multilingual "
                                    "translator. Follow the user's "
                                    "translation instructions accurately."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.2
                    )

                    final_text = (
                        response.choices[0].message.content
                    )

            # STEP 3: DISPLAY RESULT

            st.success("🎉 Conversion Completed Successfully!")

            st.divider()

            st.markdown("### 📝 Original Transcript")

            st.text_area(
                "Original Audio Text",
                value=original_text,
                height=180
            )

            if output_language != "Same as Audio":

                st.markdown(
                    f"### 🌍 Translated Text ({output_language})"
                )

            else:

                st.markdown("### 🌍 Final Transcript")

            st.text_area(
                "Final Converted Text",
                value=final_text,
                height=250
            )

            # DOWNLOAD BUTTON

            st.download_button(
                label="⬇️ Download Final Transcript",
                data=final_text,
                file_name="saad_ai_transcript.txt",
                mime="text/plain"
            )

            st.download_button(
                label="⬇️ Download Original Transcript",
                data=original_text,
                file_name="saad_ai_original.txt",
                mime="text/plain"
            )

            st.info(
                "Your voice has been successfully converted!"
            )

        except Exception as e:

            st.error(f"Error: {str(e)}")

# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#888;">
        <h3>SAAD/AI Voice to Text Converter</h3>
        <p>Powered by Groq AI and GPT-OSS 20B</p>
        <p>Created by Saad ❤️</p>
    </div>
    """,
    unsafe_allow_html=True
)
