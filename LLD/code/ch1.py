import json
import random
import string


urls={}
clicks={}

def shorten(long_url, custom_code=None):
    if custom_code:
        if custom_code in urls :
            raise ValueError(f"{custom_code} is already used")
        code =custom_code
    else:
        code = generate_code()
        while code in urls:
            code=generate_code()
    urls[code]=long_url
    save()
    return code

def generate_code():
    return ''.join(random.choices(string.ascii_letters,k=6))

def get_long_url(short_url):
    if short_url in urls:
        clicks[short_url]=clicks.get(short_url,0)+1
        save()
    return urls.get(short_url,None)

def get_click_count(short_url):
    return clicks.get(short_url,0)

def save():
    with open("urls.json","w") as f:
        json.dump({"urls":urls, "clicks":clicks},f)

def load():
    global urls, clicks
    try:
        with open("urls.json","r") as f:
            data=json.load(f)
            urls=data.get("urls",{})
            clicks=data.get("clicks",{})
    except FileNotFoundError:
        urls={}
        clicks={}
