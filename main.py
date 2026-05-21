from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 අලුත්ම වැඩ කරන Groq API Key එක සහ වැඩ කරන මොඩල් එක දාලා තියෙන්නේ
GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.3-70b-versatile" 

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

    video_search_url = f"https://pixabay.com/api/videos/?key=43936413-5a04ba3b6107bdbe8b7b252df&q={requests.utils.quote(english_prompt)}&per_page=5"
    
    # 🌟 කැඩෙන්නේ නැති, හැමවෙලේම වැඩ කරන සිරාම Backup HD වීඩියෝ එකක් (Nature)
    actual_video_url = "https://assets.mixkit.co/videos/preview/mixkit-beautiful-aerial-view-of-a-forest-and-river-42823-large.mp4"
    
    try:
        video_resp = requests.get(video_search_url).json()
        if video_resp.get('hits') and len(video_resp['hits']) > 0:
            for hit in video_resp['hits']:
                videos_dict = hit.get('videos', {})
                # කරදරකාරී vimeo සහ කැඩෙන ලින්ක් අයින් කරලා හොඳම ලින්ක් එක ගන්නවා
                for size in ['medium', 'small', 'large']:
                    if size in videos_dict and videos_dict[size].get('url'):
                        video_url_test = videos_dict[size]['url']
                        if "vimeo" not in video_url_test.lower() and "cdn.pixabay.com" not in video_url_test.lower():
                            actual_video_url = video_url_test
                            break
                if "vimeo" not in actual_video_url.lower():
                    break
    except Exception as e:
        print(f"Error fetching video: {e}")

    return {
        "status": "success",
        "video_url": actual_video_url
    }