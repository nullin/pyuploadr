#!/usr/bin/python

from settings import API_KEY, API_SECRET, PERMS
import sys
import os
from optparse import OptionParser
import urllib
from xml.dom.minidom import parseString
import ConfigParser
import flickrapi
from xml.etree import ElementTree

APP_NAME = 'pyUploadr'

options = None
flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET)

def getbloglist():
    blogs = flickr.blogs_getList()
    print ElementTree.tostring(blogs)

def deluser():
    print 'ERROR: NOT IMPLEMENTED'

def uploadprogress(progress, done):
    if done:
        print " Done"
    else:
        sys.stdout.write(".")

def uploadphotoset():
    dirpath = raw_input("Path to photos folder: ")
    
    if not os.path.isdir(dirpath):
        print '%s is not a valid directory' % dirpath
        return
    
    setname = raw_input("Name of Photoset: ")
    if not setname:
        print 'No photoset name specified'
        return
        
    photoset_id = None
    created = False
    # sets = flickr.photosets_getList()
    #     sets = sets.find('photosets').findall('photoset')
    #     for photoset in sets:
    #         if photoset.find('title').text == setname:
    #             photoset_id = photoset['id']
    #             break

    if not photoset_id:
        #print "Didn't find photoset named %s." % setname    
        print "Will create a new photoset named %s." % setname    

    # photoid_list = []
    for root, dirs, files in os.walk(dirpath):
        for photo in files:
            filename = os.path.join(root, photo)
            if not filename.find('.DS_Store') == -1 or not filename.find('Thumbs.db') == -1:
                continue
            sys.stdout.write('Uploading ' + filename + ' ')
            xmlresp = flickr.upload(filename=filename, callback=uploadprogress, format='etree')
            #print ElementTree.tostring(xmlresp)
            print "Uploaded"
            photo_id = xmlresp.find('photoid').text
            # photoid_list.append(photo_id)
            
            #create photoset if needed
            if not photoset_id:
                print "Didn't find %s named photoset. Creating one." % setname
                photoset_id = createPhotoSet(setname, photo_id)
                created = True
            else:
                #add photo to photoset
                addPhotoToSet(photo_id, photoset_id)

    # if not photoset_id:
    #         print "Didn't find %s named photoset. Creating one." % setname
    #         photoset = flickr.photosets_create(title=setname, primary_photo_id=photoid_list[0])
    #         print ElementTree.tostring(photoset)
    #         photoset_id = photoset.find('photoset').attrib['id']
    #         created = True
    #         
    #     for photo_id in photoid_list[1 if created else 0 : ]:
    #         print 'Adding %s to set' % photo_id
    #         xmlresp = flickr.photosets_addPhoto(photoset_id=photoset_id, photo_id=photo_id)
    #         print ElementTree.tostring(xmlresp)
def createPhotoSet(setname, photo_id):
    photoset = flickr.photosets_create(title=setname, primary_photo_id=photo_id)
    print "Photoset created"
    #print ElementTree.tostring(photoset)
    return photoset.find('photoset').attrib['id']

def addPhotoToSet(photo_id, photoset_id):
    print 'Adding %s to set' % photo_id
    xmlresp = flickr.photosets_addPhoto(photoset_id=photoset_id, photo_id=photo_id)
    #print ElementTree.tostring(xmlresp)
    print 'Added to photoset'

def listphotosets():
    sets = flickr.photosets_getList()
    #print sets.attrib['stat']
    #print sets.find('photosets').attrib['cancreate']
    #set0 = sets.find('photosets').findall('photoset')[0]
    print ElementTree.tostring(sets)
    

def parse_options(args):
    #from RBTools. update to handle our options
    parser = OptionParser(usage="%prog -[a|d|l|u]",
                          version=APP_NAME)

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
    #TODO: show current user, if one is already added

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

