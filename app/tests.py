from app import utils

import urllib
from cStringIO import StringIO
from Cookie import BaseCookie

import webob
import simplejson as json

from app import views


class Response(webob.Response):
    def __repr__(self):
        return u"%s c=%s h=%s" % (self.status_int, self.body,
                                  self.headers.dict_of_lists())


class Request(webob.Request):
    ResponseClass = Response


class ClientMetaclass(type):
    def __new__(cls, name, bases, attrs):
        for method in attrs['methods']:
            def requester(method, content_type=None, converter=lambda v: v):
                return lambda self, url, body='', **kwargs:\
                        self._gen_request(method, content_type=content_type,
                                          body=converter(body), url=url, **kwargs)

            method_name = method.lower()
            attrs[method_name] = requester(method)

            for ct_name, options in attrs['content_types'].iteritems():
                attrs['%s_%s' % (method_name, ct_name)] = requester(method, *options)

        return super(ClientMetaclass, cls).__new__(cls, name, bases, attrs)


class Client(object):
    __metaclass__ = ClientMetaclass

    methods = ('GET', 'POST', 'PUT', 'DELETE')

    content_types = {
        'form': ('application/x-www-form-urlencoded', urllib.urlencode),
        'json': ('application/json', json.dumps),
    }

    def __init__(self, headers=None):
        self.headers = headers or None
        self.cookies = None

        self.application = views.application

    def _gen_request(self, method, url, body='', headers=None, content_type=None):
        environ = {}

        if '?' in url:
            url, environ['QUERY_STRING'] = url.split('?', 1)
        else:
            environ['QUERY_STRING'] = ''

        if content_type is not None:
            environ['CONTENT_TYPE'] = content_type

        environ['CONTENT_LENGTH'] = str(len(body))
        environ['REQUEST_METHOD'] = method
        environ['wsgi.input'] = StringIO(body)

        req = Request.blank(url, environ)

        for h in (self.headers, headers):
            if h:
                req.headers.update(self.headers)

        return self.do_request(req)

    def do_request(self, req):
        errors = StringIO()
        req.environ['wsgi.errors'] = errors

        if self.cookies:
            cookie_header = ''.join([
                '%s="%s"; ' % (name, cookie_quote(value))
                for name, value in self.cookies.items()])
            req.environ['HTTP_COOKIE'] = cookie_header

        res = req.get_response(self.application, catch_exc_info=True)

        # We do this to make sure the app_iter is exausted:
        res.body
        res.errors = errors.getvalue()

        res.cookies_set = {}
        for header in res.headers.getall('set-cookie'):
            try:
                c = BaseCookie(header)
            except CookieError, e:
                raise CookieError(
                    "Could not parse cookie header %r: %s" % (header, e))
            for key, morsel in c.items():
                self.cookies[key] = morsel.value
                res.cookies_set[key] = morsel.value
        return res


def test():
    r"""
        >>> c = Client(headers={})

        Session creation with automatic name generation
        >>> c.post_json('/session', {'host': 'http://example.com/'}) #doctest: +ELLIPSIS
        201 c= h={... 'location': [u'/session/.../']}

        Session creation with explicit name
        >>> c.put_json('/session/abcd1234/', {'host': 'http://example.com/'}) #doctest: +ELLIPSIS
        200 c= h=...

        Trying to grab page
        >>> c.post_json(
        ...     '/session/abcd1234/',
        ...     {'url': 'http://ya.ru/', 'match': '//html/head/title'}) #doctest: +ELLIPSIS
        200 c={"content": "<html>...</html>", "matched": ["<title>...</title>"]} h={... 'content-type': ['application/json']}

        #Trying to login with credentials
        #>>> c.post('/session/abcd1234/', {'url': 'http://ya.ru/login/', 'method': 'POST', data': {login': 'foo', 'password': 'bar'}})
        #301 c={'headers': 'Location': 'http://ya.ru/login/success'} h=...
        #
        #>>> c.post('/session/abcd1234/', {'url': 'http://ya.ru/'})
        #200 c={'content': '<html>...</html>', 'headers': ..., 'status': 200} h=...
        #
        #>>> c.post('/session/abcd1234/', {'url': 'http://ya.ru/', 'pattern': '//html/body/div[@class="first"]'})
        #200 c={'match': [{'div': {'@class': 'first', None: 'foo'}}, {'div': {'@class': 'first', None: 'bar'}}]} h=...
        #
        #>>> c.post('/session/abcd1234/', {'url': 'http://ya.ru/', 'pattern': '//html/body/div[@class="first"]', 'raw': 'true'})
        #200 c={'match': ['<div class="first">foo</div>', '<div class="first">bar</div>']} h=...

        Quering session status
        >>> c.get('/session/abcd1234/') #doctest: +ELLIPSIS
        200 c={"created_at": ...} h=...

        Deleting session
        >>> c.delete('/session/abcd1234/') #doctest: +ELLIPSIS
        200 c= h=...
    """
    pass
