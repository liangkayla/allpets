import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from fastapi.requests import Request
# from transformers import AutoTokenizer, AutoModelForCausalLM
# from pydantic import BaseModel
# from transformers import CLIPProcessor, CLIPModel
# from PIL import Image
# from io import BytesIO
# from duckduckgo_search import DDGS
# from duckduckgo_search.exceptions import RatelimitException
# from langchain_community.document_loaders import AsyncChromiumLoader
# from langchain_community.document_transformers import BeautifulSoupTransformer
# import asyncio
# import time
# import traceback
# import re
# import requests
# import httpx
# from bs4 import BeautifulSoup

app = FastAPI()

templates = Jinja2Templates(directory="../ui/build")
app.mount('/static', StaticFiles(directory="../ui/build/static"), 'static')

# phi text generation model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'content/my_phi_model')
DEVICE = 'cpu'
phi = None
tokenizer = None

class Query(BaseModel):
    prompt: str

# clip zero-classification model
CLASSES = ['dog', 'cat', 'rabbit', 'hamster', 'guinea pig', 'parakeet', 'parrot', 'rat', 'mouse', 'chinchilla', 'ferret', 'horse', 'pony', 'goldfish', 'turtle', 'lizard', 'snake', 'frog', 'crab', 'gerbil', 'hedgehog', 'canary', 'finch', 'cockatiel', 'macaw', 'dove', 'sugar glider', 'goat', 'sheep', 'pig', 'donkey', 'betta fish', 'koi fish', 'axolotl', 'newt', 'iguana', 'gecko', 'tarantula', 'scorpion']
clip = None
processor = None

@app.get('/api/health')
async def health():
    return { 'status': 'healthy' }

# @app.get("/{rest_of_path:path}")
# async def react_app(req: Request, rest_of_path: str):
#     print(f'Rest of path: {rest_of_path}')
#     return templates.TemplateResponse('index.html', { 'request': req })

# @app.on_event('startup')
# def load_model():
#     global phi, tokenizer, clip, processor
    
#     # phi model
#     # error handling
#     if not os.path.isdir(MODEL_PATH) and not os.path.exists(MODEL_PATH + ".zip"):
#         raise RuntimeError(f"Phi model path not found: {MODEL_PATH}")
    
#     phi = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True)
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
#     phi.to('cpu')
#     phi.eval()
#     print('Phi model has been loaded and ready.', DEVICE)
#     clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
#     processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
#     clip.to('cpu')
#     clip.eval()
#     print('Clip model has been loaded and ready.')

# @app.post('/api/generate')
# async def generate(query: Query):
#     inputs = tokenizer(f'Context: Pets require all different types of care, such as feeding, enclosure, exercise, and stimulation. Question: {query.prompt}', return_tensors='pt')
#     input_len = inputs['input_ids'].shape[1]
#     outputs = phi.generate(**inputs, max_new_tokens=100, do_sample=False, repetition_penalty=1.2, no_repeat_ngram_size=3)
#     answer = outputs[0][input_len:]
#     text = tokenizer.decode(answer, skip_special_tokens=True).lstrip()
#     print('Complete text output', text)
#     for prefix in ["answer:", "answer :", "answer -", "answer —", "answer–", "answer– "]:
#         if text.lower().startswith(prefix):
#             text = text[len(prefix):].strip()
#             break
#     return {'response': text}

# @app.post('/api/classify')
# async def classify(file: UploadFile = File(...)):
    
#     # error handling
#     if file.content_type.split('/')[0] != 'image':
#         raise HTTPException(status_code=400, detail='Uploaded file is not an image.')
#     x
#     contents = await file.read()
#     try:
#         image = Image.open(BytesIO(contents)).convert("RGB")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f'Failed to open image: {e}. Please try uploading a JPEG, PNG, or BMP image.')
    
#     inputs = processor(text=CLASSES, images=[image], return_tensors="pt", padding=True)

#     outputs = clip(**inputs)
#     logits_per_image = outputs.logits_per_image
#     probs = logits_per_image.softmax(dim=1)
    
#     row = probs[0].tolist()
#     max_index = row.index(max(row))
#     prediction = CLASSES[max_index]
    
#     return {'response': prediction}