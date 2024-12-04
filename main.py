from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import random
import string
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
mongo_uri = os.getenv('MONGO_URI')
client = pymongo.MongoClient(mongo_uri)
db = client['url_shortener']

# Custom character set excluding similar characters
CHARACTER_SET = string.ascii_letters + '123456789'  # A-Z, a-z, 1-9

class URLRequest(BaseModel):
    url: str
    vip_url: str | None = None

def generate_short_hash(length=5):
    return ''.join(random.choice(CHARACTER_SET) for _ in range(length))

def is_hash_unique(hash):
    return db.url_hashes.find_one({'hash': hash}) is None

def is_valid(vip_url):
    return vip_url.isalnum()

@app.post("/shorten")
async def shorten_url(url_request: URLRequest, request: Request):
    url = url_request.url
    vip_url = url_request.vip_url

    if vip_url:
        if not is_valid(vip_url):
            raise HTTPException(status_code=400, detail="VIP URL must be alphanumeric")
        elif not is_hash_unique(vip_url):
            raise HTTPException(status_code=400, detail="VIP URL already exists")
        else:
            url_hash = vip_url
    else:
        # Generate a unique hash
        while True:
            url_hash = generate_short_hash()
            if is_hash_unique(url_hash):
                break

    # Store the mapping in the database
    db.url_hashes.insert_one({'url': url, 'hash': url_hash})
    current_host = request.url.scheme + "://" + request.url.netloc
    short_url = f"{current_host}/{url_hash}"
    return {"short_url": short_url}

@app.get("/{hash}")
async def redirect_url(hash: str):
    url_hash_doc = db.url_hashes.find_one({'hash': hash})
    if url_hash_doc:
        return RedirectResponse(url_hash_doc['url'])
    raise HTTPException(status_code=404, detail="URL not found")