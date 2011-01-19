#!/usr/bin/python

import settings
import hashlib
import openanything
from xml.dom.minidom import parseString

URL_SVC = 'http://api.flickr.com/services/'
URL_REST = URL_SVC + 'rest/'
URL_AUTH = URL_SVC + 'auth/'

PERMS = 'read'

def get(url):
    result = openanything.fetch(url)
    print result['status']
    print result['url']
    print result['data']
    return result

def getfrob():
    method = 'flickr.auth.getFrob'
    sig_str = API_SECRET + 'api_key' + API_KEY + 'method' + method
    api_sig = hashlib.md5(sig_str).hexdigest()
    url = URL_REST + '?method=' + method + '&api_key=' + API_KEY + '&api_sig=' \
    + api_sig
    frobxml = get(url)['data']
    xmldoc = parseString(frobxml)
    
    result = {}
    if not xmldoc.getElementsByTagName('frob') == []:
        result['frob'] = xmldoc.getElementsByTagName('frob')[0].firstChild.nodeValue
    if not xmldoc.getElementsByTagName('err') == []:
        result['err'] = xmldoc.getElementsByTagName('err')[0].getAttribute('code')
    return result

def login(frob):
    sig_str = API_SECRET + 'api_key' + API_KEY + 'frob' + frob + 'perms' \
    + PERMS
    api_sig = hashlib.md5(sig_str).hexdigest()
    url = URL_AUTH + '?api_key=' + API_KEY + '&perms=' + PERMS + '&frob=' \
    + frob + '&api_sig=' + api_sig
    
    print 'Please goto the following URL:'
    print url
    raw_input('Once done, hit enter:')
    
    method = 'flickr.auth.getToken'
    sig_str = API_SECRET + 'api_key' + API_KEY + 'frob' + frob + 'method' \
    + method
    api_sig = hashlib.md5(sig_str).hexdigest()
    url = URL_REST + '?api_key=' + API_KEY + '&frob=' + frob + '&api_sig=' \
    + api_sig + '&method=' + method
    frobxml = get(url)['data']
    xmldoc = parseString(frobxml)
    
    tokenfile = open('token.xml', 'w')
    tokenfile.write(frobxml)
    tokenfile.close()
    
    result = {}
    if not xmldoc.getElementsByTagName('token') == []:
        result['token'] = xmldoc.getElementsByTagName('token')[0].firstChild.nodeValue
    if not xmldoc.getElementsByTagName('err') == []:
        result['err'] = xmldoc.getElementsByTagName('err')[0].getAttribute('code')
    return result

def doOperation(token):
    method = 'flickr.blogs.getList'
    sig_str = API_SECRET + 'api_key' + API_KEY + 'auth_token' + token \
    + 'method' + method
    api_sig = hashlib.md5(sig_str).hexdigest()
    url = URL_REST + '?api_key=' + API_KEY + '&auth_token=' + token \
    + '&api_sig=' + api_sig + '&method=' + method
    frobxml = get(url)['data']
    xmldoc = parseString(frobxml)

    result = {}
    if not xmldoc.getElementsByTagName('token') == []:
        result['token'] = xmldoc.getElementsByTagName('token')[0].firstChild.nodeValue
    if not xmldoc.getElementsByTagName('err') == []:
        result['err'] = xmldoc.getElementsByTagName('err')[0].getAttribute('code')
    return result

def setup():
    result = getfrob()
    result = login(result['frob'])
    print result
    doOperation(result['token'])

def listsets():
    method = 'flickr.photosets.getList'
    user_id = '86813154@N00'
    sig_str = API_SECRET + 'api_key' + API_KEY + 'method' + method + 'user_id' \
    + user_id
    api_sig = hashlib.md5(sig_str).hexdigest()
    url = URL_REST + '?api_key=' + API_KEY + '&user_id=' + user_id \
    + '&api_sig=' + api_sig + '&method=' + method
    frobxml = get(url)['data']
    xmldoc = parseString(frobxml)
    
def main():
    #setup()
    listsets()
if __name__ == '__main__':
    main()

