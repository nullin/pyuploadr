#!/usr/bin/python

from settings import API_KEY, API_SECRET, PERMS, TOKEN_PROP_PATH
import sys
import os
from optparse import OptionParser
import utils
import urllib
from xml.dom.minidom import parseString
import ConfigParser
import flickrapi
from xml.etree import ElementTree

URL_SVC = 'http://api.flickr.com/services/'
URL_REST = URL_SVC + 'rest/'
URL_AUTH = URL_SVC + 'auth/'
URL_UPLOAD = URL_SVC + 'upload/'
APP_NAME = 'pyUploadr'

options = None
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET)

def getbloglist():
    blogs = flickr.blogs_getList()
    print ElementTree.tostring(blogs)

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

def deluser():
    print 'ERROR: NOT IMPLEMENTED'

def uploadprogress(progress, done):
    if done:
        print "Done uploading"
    else:
        print "At %s%%" % progress

def uploadphotoset():
    dirpath = raw_input("Path to photos folder: ")
    
    if not os.path.isdir(dirpath):
        print '%s is not a valid directory' % dirpath
        return
    
    setname = raw_input("Name of Photoset:")
    if not setname:
        print 'No photoset name specified'
        return
    
    photoid_list = []
    for root, dirs, files in os.walk(dirpath):
        for photo in files:
            filename = os.path.join(root, photo)
            print 'Working on %s' % filename
            if not filename.find('.DS_Store') == -1 or not filename.find('Thumbs.db') == -1:
                continue
            xmlresp = flickr.upload(filename=filename, callback=uploadprogress, format='etree')
            print ElementTree.tostring(xmlresp)
            photoid_list.append(xmlresp.find('photoid').text)
    
    photoset_id = None
    created = False
    sets = flickr.photosets_getList()
    sets = sets.find('photosets').findall('photoset')
    for photoset in sets:
        if photoset.find('title').text == setname:
            photoset_id = photoset['id']
            break

    if not photoset_id:
        print "Didn't find %s named photoset. Creating one." % setname
        photoset = flickr.photosets_create(title=setname, primary_photo_id=photoid_list[0])
        print ElementTree.tostring(xmlresp)
        photoset_id = photoset.find('photoset')['id']
        created = True
        
    for photo_id in photoid_list[1 if created else 0 : ]:
        print 'Adding %s to set' % photo_id
        xmlresp = flickr.photosets_addPhoto(photoset_id=photoset_id, photo_id=photo_id)
        print ElementTree.tostring(xmlresp)

def listphotosets():
    sets = flickr.photosets_getList()
    #print sets.attrib['stat']
    #print sets.find('photosets').attrib['cancreate']
    #set0 = sets.find('photosets').findall('photoset')[0]
    print ElementTree.tostring(sets)
    

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

    return args

def adduser():
    (token, frob) = flickr.get_token_part_one(perms=PERMS)
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))

def main():
    args = parse_options(sys.argv[1:])
    
    if options.adduser:
        adduser()
    elif options.deluser:
        deluser()

    #Following section should only contain of operations that need 
    #a token to be present or the application to have a user
    if options.listsets:
        listphotosets()
        getbloglist()
    
    if options.upload:
        uploadphotoset()

    sys.exit(0)

if __name__ == '__main__':
    main()

