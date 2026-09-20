import json
import random
import string

class URLShortner:

    def __init__(self):
        self.urls={}
        self.clicks={}
        self._load()

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
        self._save()
        return code


    def get_long_url(self,short_url):
        if short_url in self.urls:
            self.clicks[short_url]=self.clicks.get(short_url,0)+1
            self._save()
        return self.urls.get(short_url,None)

    def get_click_count(self,short_url):
        return self.clicks.get(short_url,0)

    def _save(self):
        with open("urls.json","w") as f:
            json.dump({"urls":self.urls, "clicks":self.clicks},f)

    def _load(self):
        try:
            with open("urls.json","r") as f:
                data=json.load(f)
                self.urls=data.get("urls",{})
                self.clicks=data.get("clicks",{})
        except FileNotFoundError:
            self.urls={}
            self.clicks={}
