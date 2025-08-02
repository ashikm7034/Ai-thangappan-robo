import os
import asyncio
import edge_tts

async def speak_malayalam_async(text):
    # Use a male Malayalam neural voice with fast, expressive tone
    voice = "ml-IN-MidhunNeural"
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate="+25%",      # Faster speed for energetic delivery
        pitch="+0Hz"      # Neutral pitch
    )
    filename = "malayalam_output.mp3"
    try:
        await communicate.save(filename)
        os.system(f"mpg123 {filename} || ffplay -nodisp -autoexit {filename} || afplay {filename}")
    except edge_tts.exceptions.NoAudioReceived:
        print(f"No audio received from edge-tts for voice '{voice}'. Try updating edge-tts or using a different voice.")

def speak_malayalam(text):
    asyncio.run(speak_malayalam_async(text))
