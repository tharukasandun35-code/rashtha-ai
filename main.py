import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
GROQ_MODEL = "llama-3.3-70b-versatile" 
PEXELS_API_KEY = "563492ad6f91700001000001bc49045330364e0a96996d99efeb97e2"

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def read_root():
    return FileResponse("index.html")

# 🌟 මේක තමයි මැජික් එක: බ්‍රවුසර් එකට කෙලින්ම වීඩියෝ එක සර්වර් එක හරහා stream කරනවා (CORS එන්නේ නෑ)
@app.get("/stream-video")
async def stream_video(url: str):
    try:
        res = requests.get(url, stream=True)
        return StreamingResponse(res.iter_content(chunk_size=1024*1024), media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-video")
async def generate_video(request: PromptRequest):
    sinhala_prompt = request.prompt
    
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
    except Exception as e:
        print(f"Error with Groq: {e}")

    video_search_url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(english_prompt)}&per_page=5"
    pexels_headers = {"Authorization": PEXELS_API_KEY}
    
    # සුපිරි Backup වීඩියෝවක්
    raw_video_url = "https://assets.mixkit.co/videos/preview/mixkit-beautiful-aerial-view-of-a-forest-and-river-42823-large.mp4"
    
    try:
        video_resp = requests.get(video_search_url, headers=pexels_headers).json()
        if video_resp.get('videos') and len(video_resp['videos']) > 0:
            first_video = video_resp['videos'][0]
            video_files = first_video.get('video_files', [])
            
            for video_file in video_files:
                if video_file.get('file_type') == "video/mp4" or ".mp4" in video_file.get('link', ''):
                    raw_video_url = video_file.get('link')
                    break
    except Exception as e:
        print(f"Error fetching from Pexels: {e}")

    # 🔗 බ්‍රවුසර් එකට කෙලින්ම යවන්නේ අපේ සර්වර් එකේ stream ලින්ක් එක!
    safe_proxy_url = f"https://tharukasandun35-rashtha-ai-backend.hf.space/stream-video?url={requests.utils.quote(raw_video_url)}"

    return {
        "status": "success",
        "video_url": safe_proxy_url
    }
