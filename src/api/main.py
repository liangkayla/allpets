import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import AutoTokenizer, AutoModelForCausalLM, CLIPProcessor, CLIPModel
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
from peft import PeftModel
import torch
import logging

# initializing logging & app setup
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger('app')
app = FastAPI()
templates = Jinja2Templates(directory="../ui/build")
app.mount('/static', StaticFiles(directory="../ui/build/static"), name='static')

# defining phi model paths (base & fine-tuned weights)
ADAPTER_PATH = os.path.join(os.path.dirname(__file__), 'content/my_phi_model')
BASE_MODEL = "/mnt/models/phi-1_5_snapshot"
DEVICE = 'cpu'

# initializing phi & clip models, text queries, and image classes
base = None
phi = None
tokenizer = None
clip = None
processor = None

class Query(BaseModel):
    prompt: str

CLASSES = ['dog', 'cat', 'rabbit', 'hamster', 'guinea pig', 'parakeet', 'parrot',
           'rat', 'mouse', 'chinchilla', 'ferret', 'horse', 'pony', 'goldfish',
           'turtle', 'lizard', 'snake', 'frog', 'crab', 'gerbil', 'hedgehog',
           'canary', 'finch', 'cockatiel', 'macaw', 'dove', 'sugar glider', 'goat',
           'sheep', 'pig', 'donkey', 'betta fish', 'koi fish', 'axolotl', 'newt',
           'iguana', 'gecko', 'tarantula', 'scorpion', 'chicken', 'rooster']

# basic endpoints
@app.get('/api/health')
async def health():
    return {'status': 'healthy'}

@app.get("/{rest_of_path:path}")
async def react_app(req: Request, rest_of_path: str):
    return templates.TemplateResponse('index.html', {'request': req})

# web app functionality
@app.on_event('startup')
def load_model():
    global base, phi, tokenizer, clip, processor
    logger.info(f"Startup: loading models from base_modeL: {BASE_MODEL} and ADAPTER_PATH: {ADAPTER_PATH}")
    
    # load phi base model
    try:
        logger.info(f"Loading base model from: {BASE_MODEL}")
        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            trust_remote_code=True,
            local_files_only=True,
            low_cpu_mem_usage=True
        )
        base.to(DEVICE)
        base.eval()
        logger.info("Base model loaded.")
    except Exception:
        base = None
        logger.exception("Failed to load base model")

    # load tokenizer
    try:
        if os.path.isdir(ADAPTER_PATH) and any(fname.startswith("tokenizer") for fname in os.listdir(ADAPTER_PATH)):
            logger.info(f"Loading tokenizer from adapter: {ADAPTER_PATH}")
            tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH, trust_remote_code=True, use_fast=True, local_files_only=True)
            logger.info("Tokenizer loaded from adapter.")
        elif base is not None:
            logger.info(f"Loading tokenizer from base model: {BASE_MODEL}")
            tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True, use_fast=True, local_files_only=True)
            logger.info("Tokenizer loaded from base.")
        else:
            tokenizer = None
            logger.warning("No tokenizer available (no base & no adapter tokenizer).")
    except Exception:
        tokenizer = None
        logger.exception("Tokenizer load failed")

    # attach adapter (fine-tuned weights) to phi base model
    if base is not None and os.path.isdir(ADAPTER_PATH):
        try:
            logger.info(f"Loading adapter from {ADAPTER_PATH}")
            phi = PeftModel.from_pretrained(base, ADAPTER_PATH, is_trainable=False)
            phi.to(DEVICE)
            phi.eval()
            logger.info("Adapter loaded and attached.")
        except Exception:
            logger.exception("Failed to attach adapter; falling back to base")
            phi = base
    else:
        phi = base
        if base is None:
            logger.warning("No base model available; generate endpoint will return 503.")
        else:
            logger.info("No adapter found; using base only.")

    # load clip model & processor
    try:
        logger.info("Loading CLIP model.")
        clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        clip.to(DEVICE)
        clip.eval()
        logger.info("CLIP loaded.")
    except Exception:
        clip = None
        processor = None
        logger.exception("Failed to load CLIP; CLIP endpoints will be unavailable.")
        
# text generation - phi model
@app.post('/api/generate')
async def generate(query: Query):
    logger.info("Generate called.")
    if phi is None or tokenizer is None:
        logger.error("Generate called but model or tokenizer not loaded")
        raise HTTPException(status_code=503, detail="Model or tokenizer not loaded")
    if not query.prompt or len(query.prompt) > 2000:
        logger.warning("Invalid prompt length")
        raise HTTPException(status_code=400, detail="Invalid prompt length")
    
    try:
        inputs = tokenizer(
            f'Context: Pets require all different types of care, such as feeding, water, grooming, enclosure, exercise, outdoor time, and stimulation. Question: {query.prompt}',
            return_tensors='pt'
        ).to(DEVICE)
        input_len = inputs['input_ids'].shape[1]
        outputs = phi.generate(**inputs, max_new_tokens=150, do_sample=False, repetition_penalty=1.2, no_repeat_ngram_size=3)
        
        # formatting model response
        answer = outputs[0][input_len:]
        text = tokenizer.decode(answer, skip_special_tokens=True).lstrip()
        for prefix in ["answer:", "answer :", "answer -", "answer —"]:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
                break
        logger.info("Generate succeeded")
        return {'response': text}
    except Exception:
        logger.exception("Error during generation")
        raise HTTPException(status_code=500, detail="Generation failed")        

# image classification - clip model
@app.post('/api/classify')
async def classify(file: UploadFile = File(...)):
    logger.info("Classify called")
    if processor is None or clip is None:
        logger.error("CLIP not loaded")
        raise HTTPException(status_code=503, detail="CLIP not loaded")
    if file.content_type.split('/')[0] != 'image':
        logger.warning("Uploaded file is not an image")
        raise HTTPException(status_code=400, detail='Uploaded file is not an image.')
    contents = await file.read()
    try:
        image = Image.open(BytesIO(contents)).convert("RGB")
    except Exception:
        logger.exception("Failed to open uploaded image")
        raise HTTPException(status_code=400, detail=f'Failed to open image. Please try uploading a jpeg, png, or webp image.')
    try:
        inputs = processor(text=CLASSES, images=[image], return_tensors="pt", padding=True).to(DEVICE)
        outputs = clip(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)
        row = probs[0].tolist()
        max_index = row.index(max(row))
        prediction = CLASSES[max_index]
        return {'response': prediction}
    except Exception:
        logger.exception("Error during classification")
        raise HTTPException(status_code=500, detail="Classification failed")