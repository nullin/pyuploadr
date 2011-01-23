#!/usr/bin/python

from settings import API_KEY, PERMS, TOKEN_PROP_PATH
import sys
import os
from optparse import OptionParser
import utils
import urllib
from xml.dom.minidom import parseString
import ConfigParser

URL_SVC = 'http://api.flickr.com/services/'
URL_REST = URL_SVC + 'rest/'
URL_AUTH = URL_SVC + 'auth/'
URL_UPLOAD = URL_SVC + 'upload/'
APP_NAME = 'pyUploadr'

options = None

def getfrob():
    parameters = { 'method':'flickr.auth.getFrob', 'api_key':API_KEY }
    frobxml = utils.get(URL_REST, parameters)['data']
    xmldoc = parseString(frobxml)
    
    result = {}
    if not xmldoc.getElementsByTagName('frob') == []:
        result['frob'] = xmldoc.getElementsByTagName('frob')[0].firstChild.nodeValue
    if not xmldoc.getElementsByTagName('err') == []:
        result['err'] = xmldoc.getElementsByTagName('err')[0].getAttribute('code')
    return result

def gettoken(frob):
    parameters = { 'api_key':API_KEY, 'frob':frob, 'perms':PERMS }
    url = utils.getsignedurl(URL_AUTH, parameters)
    
    print 'Please go to the following URL to allow Flickr to give access to this application:'
    print url
    raw_input('Once done, hit any key:')
    
    parameters = { 'method':'flickr.auth.getToken', 'api_key':API_KEY, 'frob':frob }
    frobxml = utils.get(URL_REST, parameters)['data']
    xmldoc = parseString(frobxml)
    
    result = {}
    error = False
    if not xmldoc.getElementsByTagName('err') == []:
        result['code'] = xmldoc.getElementsByTagName('err')[0].getAttribute('code')
        error = True

    if not xmldoc.getElementsByTagName('token') == []:
        result['token'] = xmldoc.getElementsByTagName('token')[0].firstChild.nodeValue
    else:
        error = True
    if not xmldoc.getElementsByTagName('perms') == []:
        result['perms'] = xmldoc.getElementsByTagName('perms')[0].firstChild.nodeValue
    else:
        error = True
    if not xmldoc.getElementsByTagName('user') == []:
        usertag = xmldoc.getElementsByTagName('user')[0]
        result['nsid'] = usertag.getAttribute('nsid')
        result['username'] = usertag.getAttribute('username')
        result['fullname'] = usertag.getAttribute('fullname')
    else:
        error = True

    if error:
        if result['code']:
            code = result['code']
            print 'Flickr returned error code ' + code
            if code == '108':
                print 'Did you go to Flickr and authorize ' + APP_NAME + '?'
            else:
                print 'Not sure what went wrong. Can you file a bug or ping me?'
        else:
            print 'Something went wrong. Flickr returned incomplete information.'
            print 'Got back following XML from Flickr:\n'
            print xmldoc.toxml()
    else:
        tokenfile = open(TOKEN_PROP_PATH, 'w')
        tokenfile.write('token=' + result['token'] + '\n')
        tokenfile.write('perms=' + result['perms'] + '\n')
        tokenfile.write('nsid=' + result['nsid'] + '\n')
        tokenfile.write('username=' + result['username'] + '\n')
        tokenfile.write('fullname=' + result['fullname'] + '\n')
        tokenfile.close()
        print APP_NAME + ' has been setup for user ' + result['username']

def getbloglist(token):
    parameters = { 'method':'flickr.blogs.getList', 'api_key':API_KEY, 'auth_token':token }
    frobxml = utils.get(URL_REST, parameters)['data']
    xmldoc = parseString(frobxml)

    result = {}
    if not xmldoc.getElementsByTagName('token') == []:
        result['token'] = xmldoc.getElementsByTagName('token')[0].firstChild.nodeValue
    if not xmldoc.getElementsByTagName('err') == []:
        result['err'] = xmldoc.getElementsByTagName('err')[0].getAttribute('code')
    return result

def gettokenproperties():
    try:
        tokenfile = open(TOKEN_PROP_PATH)
        props = {}
        for line in tokenfile.readlines():
            items = line.replace('\n','').split('=')
            props[items[0]] = items[1]
        return props
    except IOError:
        return None
    except IndexError:
        print 'ERROR: Token file is courrpt. Please reset ' + APP_NAME
        sys.exit(1)

def adduser():
    tokenprops = gettokenproperties()
    
    if tokenprops:
        print APP_NAME + ' is already cofigured for user ' + tokenprops['username']
        sys.exit(0)
    
    result = getfrob()
    result = gettoken(result['frob'])

def deluser():
    tokenprops = gettokenproperties()
    
    if tokenprops:
        print 'Are you sure you want to delete user ' + tokenprops['username'] + ' ?'
        input = raw_input('Enter Y/y to continue: ')
        if input.lower() == 'y':
            os.remove(TOKEN_PROP_PATH)
            print 'Deleted user'
        else:
            print 'User canceled operation. Not making any changes'
    else:
        print APP_NAME + ' is not configured with a user currently. No user to delete.'

def uploadphotoset():
    token = gettokenproperties()['token']
    parameters = { 'api_key':API_KEY, 'auth_token':token, 'safety_level':'3', 'content_type':'0', 'hidden':'1' }
    filename = '/Users/nullin/Desktop/dilbert.jpg'
    respxml = utils.post(URL_UPLOAD, parameters, filename)

def listphotosets(token=None, user_id=None):
    parameters = { 'method':'flickr.photosets.getList', 'api_key':API_KEY }
    if token:
        parameters['auth_token'] = token
    if user_id:
        parameters['user_id'] = user_id
    respxml = utils.get(URL_REST, parameters)['data']
    xmldoc = parseString(respxml) #should do something with the response

def parse_options(args):
    #from RBTools. update to handle our options
    parser = OptionParser(usage="%prog [-pond] [-r review_id] [changenum]",
                          version="RBTools ") #FIXME: + get_version_string())

    parser.add_option("-a", "--adduser",
                      dest="adduser", action="store_true", default=False,
                      help="Sets up a Flickr user")
    parser.add_option("-d", "--deleteuser",
                      dest="deluser", action="store_true", default=False,
                      help="Removes the current Flickr user")
    parser.add_option("-l", "--listsets",
                      dest="listsets", action="store_true",
                      default=False,
                      help="Lists the accessible photosets")
    parser.add_option("-u","--upload",
                      dest="upload", action="store_true", default=False,
                      help="Upload photos/videos to a new photoset")

    (globals()["options"], args) = parser.parse_args(args)

    #if options.description and options.description_file:
    #    sys.stderr.write("The --description and --description-file options "
    #                     "are mutually exclusive.\n")
    #    sys.exit(1)

    #if options.description_file:
    #    if os.path.exists(options.description_file):
    #        fp = open(options.description_file, "r")
    #        options.description = fp.read()
    #        fp.close()
    #    else:
    #        sys.stderr.write("The description file %s does not exist.\n" %
    #                         options.description_file)
    #        sys.exit(1)

    #if options.testing_done and options.testing_file:
    #    sys.stderr.write("The --testing-done and --testing-done-file options "
    #                     "are mutually exclusive.\n")
    #    sys.exit(1)

    #if options.testing_file:
    #    if os.path.exists(options.testing_file):
    #        fp = open(options.testing_file, "r")
    #        options.testing_done = fp.read()
    #        fp.close()
    #    else:
    #        sys.stderr.write("The testing file %s does not exist.\n" %
    #                         options.testing_file)
    #        sys.exit(1)

    #if options.reopen and not options.rid:
    #    sys.stderr.write("The --reopen option requires "
    #                     "--review-request-id option.\n")
    #    sys.exit(1)

    return args

def main():
    args = parse_options(sys.argv[1:])
    
    if options.adduser:
        adduser()
    elif options.deluser:
        deluser()

    #Following section should only contain of operations that need 
    #a token to be present or the application to have a user
    if options.listsets:
        listphotosets(gettokenproperties()['token'])
        #getbloglist(gettokenproperties()['token'])
    
    if options.upload:
        uploadphotoset()

    sys.exit(0)

if __name__ == '__main__':
    main()

