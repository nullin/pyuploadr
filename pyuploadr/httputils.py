#!/usr/bin/python

import urllib2, urlparse, gzip
from StringIO import StringIO

__version__ = '0.1'
USER_AGENT = 'pyUploadr/%s' % __version__

def request(url, data=None, user_agent=USER_AGENT):
    request = urllib2.Request(url) if not data else urllib2.Request(url, data)
    request.add_header('User-Agent', user_agent)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)
    result = {}
    result['data'] = response.read()
    if hasattr(response, 'headers'):
        if response.headers.get('content-encoding') == 'gzip':
            # data came back gzip-compressed, decompress it
            result['data'] = gzip.GzipFile(fileobj=StringIO(result['data'])).read()
    if hasattr(response, 'url'):
        result['url'] = response.url
        result['status'] = 200
    if hasattr(response, 'status'):
        result['status'] = response.status
    response.close()
    return result
