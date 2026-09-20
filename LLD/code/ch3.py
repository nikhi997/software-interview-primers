import json
import random
import string

class URLShortener:

    def __init__(self,storage):
        self.storage=storage

        data=self.storage.load()
        self.urls=data.get("urls",{})
        self.clicks=data.get("clicks",{})

    def _generate_code(self):
        return ''.join(random.choices(string.ascii_letters,k=6))

    def shorten(self,long_url, custom_code=None):
        if custom_code:
            if custom_code in self.urls :
                raise ValueError(f"{custom_code} is already used")
            code =custom_code
        else:
            code = self._generate_code()
            while code in self.urls:
                code=self._generate_code()
        self.urls[code]=long_url
        self.storage.save({"urls":self.urls, "clicks":self.clicks})
        return code


    def get_long_url(self,short_url):
        if short_url in self.urls:
            self.clicks[short_url]=self.clicks.get(short_url,0)+1
            self.storage.save({"urls":self.urls, "clicks":self.clicks})
        return self.urls.get(short_url,None)

    def get_click_count(self,short_url):
        return self.clicks.get(short_url,0)


class FileStorage:
    def __init__(self,file_name="urls.json"):
        self.file_name= file_name

    def save(self,data):
        with open(self.file_name,"w") as f:
            json.dump(data,f)

    def load(self):
        try:
            with open(self.file_name,"r") as f:
                data=json.load(f)
                urls= data.get("urls",{})
                clicks= data.get("clicks",{})
                return {"urls": urls, "clicks": clicks}
        except FileNotFoundError:
            return {"urls": {}, "clicks": {}}

class MemoryStorage:
    def __init__(self):
        self.data = {"urls": {}, "clicks": {}}
    def save(self,data):
        self.data=data

    def load(self):
        urls=self.data.get("urls",{})
        clicks=self.data.get("clicks",{})
        return {"urls": urls, "clicks": clicks}

class RedisStorage:
    def __init__(self,redis_client):
        self.redis_client=redis_client

    def save(self,data):
        self.redis_client.set("urls_data", json.dumps(data))

    def load(self):
        data=self.redis_client.get("urls_data")
        if data:
            data=json.loads(data)
            urls=data.get("urls",{})
            clicks=data.get("clicks",{})
        return {"urls": urls, "clicks": clicks}
