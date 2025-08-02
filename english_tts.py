import os
import asyncio
import edge_tts

async def speak_english_async(text):
    # Use a male English neural voice with fast, expressive tone
    voice = "en-US-GuyNeural"  # Male voice for better character representation
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate="+0%",      # Faster speed for energetic delivery
        pitch="+0Hz"      # Neutral pitch
    )
    filename = "english_output.mp3"
    try:
        await communicate.save(filename)
        os.system(f"mpg123 {filename} || ffplay -nodisp -autoexit {filename} || afplay {filename}")
    except edge_tts.exceptions.NoAudioReceived:
        print(f"No audio received from edge-tts for voice '{voice}'. Try updating edge-tts or using a different voice.")

def speak_english(text):
    asyncio.run(speak_english_async(text))