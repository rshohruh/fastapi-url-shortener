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
mongo_db_url = os.getenv('MONGO_DB_URL')
client = pymongo.MongoClient(mongo_db_url)
db = client['url_shortener']

# Custom character set excluding similar characters
CHARACTER_SET = string.ascii_letters + '123456789'  # A-Z, a-z, 1-9

class URLRequest(BaseModel):
    url: str

def generate_short_hash(length=5):
    return ''.join(random.choice(CHARACTER_SET) for _ in range(length))

def is_hash_unique(hash):
    return db.url_hashes.find_one({'hash': hash}) is None

@app.post("/shorten")
async def shorten_url(url_request: URLRequest, request: Request):
    url = url_request.url
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