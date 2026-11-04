from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import edge_tts
import base64
import requests
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API Key របស់អ្នក
client = OpenAI(api_key="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")

class VideoProcessRequest(BaseModel):
    url: str
    voice_type: str = "male"

VOICE_MAP = {
    "male": "km-KH-SamnangNeural",     # សំឡេងប្រុស
    "female": "km-KH-SreymomNeural"   # សំឡេងស្រី
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

        # ប្រើប្រាស់ Public API ឥតគិតថ្លៃដើម្បីទាញយក Direct Audio Link ពីវីដេអូ
        api_url = f"https://apis.davidcyriltech.name/tools/downloader?url={data.url}"
        response = requests.get(api_url)
        res_data = response.json()

        audio_download_url = None
        if res_data and "success" in res_data:
            # ទាញយក Link សម្លេងពី API មកប្រើប្រាស់
            audio_download_url = res_data.get("audio") or res_data.get("dl_url")

        if not audio_download_url:
            raise HTTPException(status_code=400, detail="មិនអាចទាញយកសម្លេងពីលីងនេះបានទេ សូមព្យាយាមលីងផ្សេង!")

        # ទាញយកไฟล์សម្លេង MP3 មកទុកក្នុង Server
        audio_response = requests.get(audio_download_url)
        with open(audio_file_path, "wb") as f:
            f.write(audio_response.content)

        # ១. ផ្ញើ ፋይልសម្លេងទៅកាន់ OpenAI Whisper API
        with open(audio_file_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        original_text = transcript_response.text

        # ២. ប្រើ GPT បកប្រែជាភាសាខ្មែរ
        chat_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the following transcribed video text into natural, fluent Khmer language suitable for voiceover."},
                {"role": "user", "content": original_text}
            ]
        )
        khmer_translation = chat_response.choices[0].message.content

        # ៣. ប្រើ Edge TTS បំលែងជាសំឡេង AI
        voice_name = VOICE_MAP.get(data.voice_type, VOICE_MAP["male"])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_bytes = loop.run_until_complete(generate_edge_tts(khmer_translation, voice_name))
        loop.close()

        if not audio_bytes:
            raise HTTPException(status_code=500, detail="មិនអាចបង្កើតសំឡេង AI ได้ទេ")

        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        return {
            "success": True,
            "original_text": original_text,
            "translated_text": khmer_translation,
            "audio_base64": audio_base64,
            "message": "បកប្រែនិងបង្កើតសំឡេង AI ได้ជោគជ័យ!"
        }

    except Exception as e:
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
        print("Server Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
