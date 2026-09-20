
import json
import random
import string


class URLShortner:

    def __init__(self):
        self.urls= {}
        self.clicks = {}
        self._load()

    def shorten_url(self,long_url, custom_code=None):
        if custom_code and custom_code in self.urls:
            raise ValueError("already used custom code")
        self.short_url = custom_code if custom_code else self._generate_code()
        self.urls[self.short_url] = long_url
        self._save()
        return self.short_url

    def long_url(self,short_url):
        self.clicks[short_url] = (self.clicks.get(short_url, 0)) + 1
        self._save()

        return self.urls.get(short_url, None)

    def _generate_code(self):
        return ''.join(random.choices(string.ascii_letters , k=6))

    def get_click_count(self, short_url):
        return self.clicks.get(short_url, 0)

    def _save(self):
        with open("urls.json", "w") as f:
            json.dump({"urls": self.urls, "clicks": self.clicks}, f)

    def _load(self):
        try:
            with open("urls.json", "r") as f:
                data = json.load(f)
                self.urls = data.get("urls",{})
                self.clicks = data.get("clicks",{})
        except FileNotFoundError:
            self.urls = {}
            self.clicks = {}
