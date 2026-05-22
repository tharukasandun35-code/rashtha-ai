import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 API Keys සහ Model එක
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_MODEL = "llama-3.3-70b-versatile" 

# 🌟 කැඩෙන්නේ නැති සුපිරිම HD වීඩියෝ සපයන Pexels API Key එක
PEXELS_API_KEY = "563492ad6f91700001000001bc49045330364e0a96996d99efeb97e2"

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.post("/generate-video")
async def generate_video(request: PromptRequest):
    sinhala_prompt = request.prompt
    print(f"🔮 Rashtha AI received Sinhala prompt: {sinhala_prompt}")
    
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    groq_data = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "Translate the Sinhala video prompt into 1 or 2 simple English keywords for video searching. RESPOND ONLY WITH THE KEYWORDS. Example: 'හරකෙක් තණකොළ කනවා' -> 'cow grass'. No punctuation, no extra text."
            },
            {"role": "user", "content": sinhala_prompt}
        ]
    }
    
    english_prompt = "nature"
    try:
        response = requests.post(groq_url, json=groq_data, headers=headers)
        result = response.json()
        if 'choices' in result:
            english_prompt = result['choices'][0]['message']['content'].strip().lower()
            print(f"✨ Groq AI Optimized Keywords: {english_prompt}")
    except Exception as e:
        print(f"Error with Groq: {e}")

    # 🎬 Pexels API එක හරහා සිරාම වීඩියෝ සෙවීම
    video_search_url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(english_prompt)}&per_page=5"
    pexels_headers = {"Authorization": PEXELS_API_KEY}
    
    # 🌟 කිසිම වෙලාවක කළු පාට නොවී ප්ලේ වෙන්න දාපු සිරාම Backup HD වීඩියෝ එකක්
    actual_video_url = "https://assets.mixkit.co/videos/preview/mixkit-beautiful-aerial-view-of-a-forest-and-river-42823-large.mp4"
    
    try:
        video_resp = requests.get(video_search_url, headers=pexels_headers).json()
        if video_resp.get('videos') and len(video_resp['videos']) > 0:
            # පළමු වීඩියෝව තෝරාගෙන එහි වැඩ කරන mp4 ලින්ක් එකක් ගන්නවා
            first_video = video_resp['videos'][0]
            video_files = first_video.get('video_files', [])
            
            for video_file in video_files:
                # හොඳම HD හෝ SD mp4 ලින්ක් එකක් තෝරාගැනීම
                if video_file.get('file_type') == "video/mp4" or ".mp4" in video_file.get('link', ''):
                    actual_video_url = video_file.get('link')
                    print(f"✅ Successfully found working Pexels URL: {actual_video_url}")
                    break
    except Exception as e:
        print(f"Error fetching video from Pexels: {e}")

    return {
        "status": "success",
        "video_url": actual_video_url
    }
