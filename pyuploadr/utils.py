from settings import API_SECRET
import hashlib
import httputils
import urllib
import multipartpost

def getsignature(parameters):
   sig_str = API_SECRET
   if isinstance(parameters, list):
      for param in sorted(parameters, key=lambda parameter: parameter[0]):
        sig_str += param[0] + param[1]
   else:
       for key in sorted(parameters.keys()):
           sig_str += key + parameters[key]
   return hashlib.md5(sig_str).hexdigest()

def geturl(url, parameters):
    final_url = url + '?'
    for key, value in parameters.iteritems():
       final_url += key + '=' + value + '&'
    return final_url

def getsignedurl(url, parameters):
    final_url = geturl(url, parameters)
    api_sig = getsignature(parameters)
    return final_url + 'api_sig=' + api_sig

def printit(result):
    print '*********************************'
    print 'DEBUG: status=' + str(result['status'])
    print 'DEBUG: url=' + result['url']
    print 'DEBUG: data=' + result['data']
    print '*********************************'

def get(url, parameters):
    final_url = getsignedurl(url, parameters)
    result = httputils.request(final_url)
    printit(result)
    return result

def post(url, parameters, filename):
    sig = getsignature(parameters)
    #postdata = [phototuple, ('api_sig', sig)]
    #postdata.extend(datalist)
    #postdata.append(phototuple)
    #print postdata
    #result = httputils.request(url, urllib.urlencode(postdata))
    fields = []
    for k,v in parameters.iteritems():
        fields.append((k,v))
    fields.append(('api_sig', sig))
    imagefile = open(filename, 'rb')
    imagecontents = imagefile.read()
    imagefile.close()
    
    result = multipartpost.post_multipart('api.flickr.com', '/services/upload', fields, [('photo', filename, imagecontents)])
    print result
    return result