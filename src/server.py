from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import redis
import base64
import time
from starlette.requests import Request
from starlette.responses import RedirectResponse

app = FastAPI()

r = redis.Redis(host='localhost', port = 6379, db=0)

DOMAIN = "http://bit.ly/"
NEW_URL_LENGTH = 7

class LongUrl(BaseModel):
    url: str

class UrlShortener:
    def __init__(self):
        print("Class initiated")
        pass

    def shorten(self, long_url: str, user_ip: str):
        """
        TODO: Shorten the URL
        """
        short_url = DOMAIN + self.generate_encoded_url(long_url, user_ip).decode()
        if r.exists(short_url):
            short_url = DOMAIN + self.generate_encoded_url(long_url, user_ip).decode()
        r.set(short_url, long_url)
        return short_url

    def generate_encoded_url(self, long_url, user_ip):
        ts = int(round(time.time() * 1000))
        md5_hash = hashlib.md5((long_url + user_ip + str(ts)).encode('utf-8')).hexdigest()
        short_url = self.base_64_encode(md5_hash)[:NEW_URL_LENGTH]
        return short_url
        
    def base_64_encode(self, hash: str):
        """
        Base 64 encoding for the generated hash
        """
        return base64.b64encode(hash.encode())
        

    def get_original_url(self, short_url: str):
        """
        Return the original URL from the short URL
        """
        if r.exists(short_url):
            return r.get(short_url)
        

shortener = UrlShortener()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/shorten/url")
def shorten_url(long_url: LongUrl, request: Request):
    client_host = request.client.host
    return {"new_url": shortener.shorten(long_url.url, client_host)}

@app.post("/get_long_url")
def redirect_from_short_url(short_url: LongUrl):
    original_url = shortener.get_original_url(short_url.url)
    print("original url {}".format(original_url)) 
    return original_url

