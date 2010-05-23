from xml.dom import minidom

import html5lib
import xpath
import mimeparse

from google.appengine.api import urlfetch

def parse_html(content):
    return html5lib.parse(content, treebuilder='dom')

def parse_xml(content):
    return minidom.parseString(content)

def match_xpath(pattern, root):
    return xpath.find(pattern, root, default_namespace='http://www.w3.org/1999/xhtml')

handlers = {
    'text/html':       (parse_html, match_xpath),
    'text/xml':        (parse_xml,  match_xpath),
    'application/xml': (parse_xml,  match_xpath),
}


rpc = urlfetch.create_rpc()


def process(uri, pattern):
    urlfetch.make_fetch_call(rpc, uri)

    try:
        result = rpc.get_result()
        if result.content:
            mimetype = mimeparse.best_match(
                handlers.keys(), result.headers.get('content-type', 'text/html')
            )
            parser, matcher = handlers[mimetype]

            root = parser(result.content)

            matched = matcher(pattern, root)

            return result.content, [m.toxml() for m in matched]
    except urlfetch.DownloadError:
        pass
