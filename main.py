from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import asyncio
import edge_tts
import base64
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ដាក់ OpenAI API Key របស់អ្នកនៅទីនេះ (ជំនួសកន្លែង "YOUR_OPENAI_API_KEY")
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

class VideoProcessRequest(BaseModel):
    url: str
    voice_type: str = "male"  # "male" (សំឡេងប្រុស) ឬ "female" (សំឡេងស្រី)

VOICE_MAP = {
    "male": "km-KH-SamnangNeural",     # សំឡេងប្រុស ក្រាស់ ធម្មជាតិ
    "female": "km-KH-SreymomNeural"   # សំឡេងស្រី ស្រទន់ ធម្មជាតិ
}

async def generate_edge_tts(text: str, voice_name: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice_name)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

@app.post("/api/process-video-voice")
def process_video_voice(data: VideoProcessRequest):
    audio_file_path = "temp_audio.mp3"
    try:
        if not data.url.strip():
            raise HTTPException(status_code=400, detail="សូមបញ្ចូលលីងវីដេអូជាមុនសិន!")

        # ១. ប្រើ yt-dlp ទាញយកសម្លេងពីគ្រប់លីងវីដេអូ (YouTube, TikTok, Facebook, etc.)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'temp_audio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([data.url])

        actual_audio_path = "temp_audio.mp3"
        if not os.path.exists(actual_audio_path):
            for f in os.listdir("."):
                if f.startswith("temp_audio"):
                    actual_audio_path = f
                    break

        # ២. ផ្ញើ ፋይልសម្លេងទៅកាន់ OpenAI Whisper API ដើម្បីដកស្រង់ជាអក្សរដើម
        with open(actual_audio_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        original_text = transcript_response.text

        # ៣. ប្រើ GPT បកប្រែអត្ថបទនោះជាភាសាខ្មែរយ៉ាងរលូន
        chat_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the following transcribed video text into natural, fluent Khmer language suitable for voiceover."},
                {"role": "user", "content": original_text}
            ]
        )
        khmer_translation = chat_response.choices[0].message.content

        # ៤. បំលែងអត្ថបទខ្មែរទៅជាសំឡេង AI (Edge TTS)
        voice_name = VOICE_MAP.get(data.voice_type, VOICE_MAP["male"])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(generate_edge_tts(khmer_translation, voice_name))
        loop.close()

        if not audio_bytes:
            raise HTTPException(status_code=500, detail="មិនអាចបង្កើតសំឡេង AI បានទេ")

        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        # លុបไฟล์ชั่วคราวចេញដើម្បីសន្សំសំចៃទំហំ Server
        if os.path.exists(actual_audio_path):
            os.remove(actual_audio_path)

        return {
            "success": True,
            "original_text": original_text,
            "translated_text": khmer_translation,
            "audio_base64": audio_base64,
            "message": "ដំណើរការបកប្រែនិងបង្កើតសំឡេង AI បានជោគជ័យ!"
        }

    except Exception as e:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        print("Server Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
