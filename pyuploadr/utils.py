from settings import API_SECRET
import hashlib
import openanything

def getsignature(parameters):
   sig_str = API_SECRET
   key_list = parameters.keys()
   key_list.sort()
   for key in key_list:
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

def get(url, parameters):
    final_url = getsignedurl(url, parameters)
    result = openanything.fetch(final_url)
    print '*********************************'
    print 'DEBUG: status=' + str(result['status'])
    print 'DEBUG: url=' + result['url']
    print 'DEBUG: data=' + result['data']
    print '*********************************'
    return result