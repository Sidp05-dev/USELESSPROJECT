import gradio as gr
import whisper
import tempfile
import os
import threading
import time

# Load Whisper model
model = whisper.load_model("base")

# ASCII frames
DANCE_FRAMES = [
    r"""
     o/
    /|
    / \
    """,
    r"""
    \o
     |\
    / \
    """,
    r"""
     o/
    <| 
    / \
    """,
    r"""
    \o
     |>
    / \
    """
]

IDLE_FRAME = r"""
     o
    /|\
    / \
"""

# State variables
current_frame = IDLE_FRAME
dancing = False
stop_flag = False

# Background animation loop
def animate():
    global current_frame, dancing, stop_flag
    frame_index = 0
    while not stop_flag:
        if dancing:
            current_frame = DANCE_FRAMES[frame_index % len(DANCE_FRAMES)]
            frame_index += 1
        else:
            current_frame = IDLE_FRAME
        time.sleep(0.3)

threading.Thread(target=animate, daemon=True).start()

# Handle speech input
def transcribe(audio_file):
    global dancing
    if audio_file is None:
        dancing = False
        return "No audio detected"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        os.rename(audio_file, tmp.name)
        result = model.transcribe(tmp.name)
    text = result["text"].strip()
    dancing = bool(text)
    return text if text else "No speech detected"

# Stop button
def stop_dancing():
    global dancing
    dancing = False
    return "Dance stopped"

# Provide current frame
def get_ascii_frame():
    return current_frame

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("## 🎤 talk2text — ASCII Dancing Man")
    with gr.Row():
        audio_in = gr.Audio(sources=["microphone"], type="filepath", label="🎙 Speak")
        transcript = gr.Textbox(label="📝 Transcription", value="")
        dancer = gr.Textbox(label="💃 ASCII Dancer", value=IDLE_FRAME)

    with gr.Row():
        stop_btn = gr.Button("🛑 Stop Dancing")

    audio_in.change(transcribe, inputs=audio_in, outputs=transcript)
    stop_btn.click(stop_dancing, inputs=None, outputs=transcript)

    # ASCII refresh loop
    gr.Timer(0.3).tick(get_ascii_frame, inputs=None, outputs=dancer)

app.launch()
