from app import utils

import hashlib
from time import time
from random import random
from google.appengine.ext.webapp import util
from restish import app, http, resource
import simplejson as json

from app import models


def create_session_from_request(request, name):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise http.BadRequestError([], 'Could not parse body')

    try:
        session = models.Session.get_or_insert(name, host=data['host'])
    except (TypeError, KeyError):
        raise http.BadRequestError([], 'Invalid params')

    session.put()

    return session


class SessionResource(resource.Resource):
    def __init__(self, name):
        self.name = name

    @resource.GET()
    def status(self, request):
        session = models.Session.get_by_key_name(self.name)
        if session is None:
            return http.not_found([], '')

        return http.ok(
            [('Content-Type', 'application/json')],
            json.dumps({'created_at': str(session.created_at)})
        )

    @resource.PUT()
    def create(self, request):
        session = create_session_from_request(request, self.name)

        return http.ok([], '')

    @resource.DELETE()
    def delete(self, request):
        session = models.Session.get_by_key_name(self.name)
        if session is not None:
            session.delete()
        return http.ok([], '')

    @resource.POST()
    def scrape(self, request):
        session = models.Session.get_by_key_name(self.name)
        if session is None:
            return http.not_found([], '')

        data = json.loads(request.body)

        content, matched = session.scrape(data['url'], data['match'])

        return http.ok(
            [('Content-Type', 'application/json')],
            json.dumps({'content': content, 'matched': matched})
        )

class SessionManagerResource(resource.Resource):
    @resource.POST()
    def create(self, request):
        session = create_session_from_request(
            request,
            hashlib.md5(''.join(map(str, [time(), random()]))).hexdigest()
        )

        return http.created('/session/%s/' % session.key().name(), [], '')

class Root(resource.Resource):
    @resource.GET()
    def index(self, request):
        return http.ok([], 'Screen-scraper with REST API')

    @resource.child('session')
    def session_manager(self, request, segments):
        return SessionManagerResource(), []

    @resource.child('session/{name}')
    def session(self, request, segments, name):
        return SessionResource(name), []

application = app.RestishApp(Root())

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
