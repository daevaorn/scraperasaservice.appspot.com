from app import utils

from datetime import datetime
from urlparse import urljoin
from Cookie import BaseCookie

from google.appengine.ext import db

from app import fields, scraper

class Session(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True)
    host = db.LinkProperty()

    reuqest_count = db.IntegerProperty(default=0)
    last_request_at = db.DateTimeProperty()

    headers = fields.ObjectProperty(dict)
    cookies = fields.ObjectProperty(BaseCookie)

    def scrape(self, url, match):
        return scraper.process(urljoin(self.host, url), match)
