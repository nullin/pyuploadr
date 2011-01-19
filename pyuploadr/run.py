#!/usr/bin/python

from settings import API_KEY, PERMS
import sys
from optparse import OptionParser
import utils
from xml.dom.minidom import parseString

URL_SVC = 'http://api.flickr.com/services/'
URL_REST = URL_SVC + 'rest/'
URL_AUTH = URL_SVC + 'auth/'

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

def login(frob):
    
    parameters = { 'api_key':API_KEY, 'frob':frob, 'perms':PERMS }
    url = utils.getsignedurl(URL_AUTH, parameters)
    
    print 'Please go to the following URL to allow Flickr to give access to this application:'
    print url
    raw_input('Once done, hit any key:')
    
    parameters = { 'method':'flickr.auth.getToken', 'api_key':API_KEY, 'frob':frob }
    frobxml = utils.get(URL_REST, parameters)['data']
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
    parameters = { 'method':'flickr.blogs.getList', 'api_key':API_KEY, 'auth_token':token }
    frobxml = utils.get(URL_REST, parameters)['data']
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
    parameters = { 'method':'flickr.photosets.getList', 'user_id':'86813154@N00', 'api_key':API_KEY }
    frobxml = utils.get(URL_REST, parameters)['data']
    xmldoc = parseString(frobxml)

def parse_options(args):
    parser = OptionParser(usage="%prog [-pond] [-r review_id] [changenum]",
                          version="RBTools ") #FIXME: + get_version_string())

    parser.add_option("-p", "--publish",
                      dest="publish", action="store_true", default='PUBLISH',
                      help="publish the review request immediately after "
                           "submitting")
    parser.add_option("-r", "--review-request-id",
                      dest="rid", metavar="ID", default=None,
                      help="existing review request ID to update")
    parser.add_option("-o", "--open",
                      dest="open_browser", action="store_true",
                      default='OPEN_BROWSER',
                      help="open a web browser to the review request page")
    parser.add_option("-n", "--output-diff",
                      dest="output_diff_only", action="store_true",
                      default=False,
                      help="outputs a diff to the console and exits. "
                           "Does not post")
    parser.add_option("--server",
                      dest="server", default='REVIEWBOARD_URL',
                      metavar="SERVER",
                      help="specify a different Review Board server "
                           "to use")
    parser.add_option("--diff-only",
                      dest="diff_only", action="store_true", default=False,
                      help="uploads a new diff, but does not update "
                           "info from changelist")
    parser.add_option("--reopen",
                      dest="reopen", action="store_true", default=False,
                      help="reopen discarded review request "
                           "after update")
    parser.add_option("--target-groups",
                      dest="target_groups", default='TARGET_GROUPS',
                      help="names of the groups who will perform "
                           "the review")
    parser.add_option("--target-people",
                      dest="target_people", default='TARGET_PEOPLE',
                      help="names of the people who will perform "
                           "the review")
    parser.add_option("--summary",
                      dest="summary", default=None,
                      help="summary of the review ")
    parser.add_option("--description",
                      dest="description", default=None,
                      help="description of the review ")
    parser.add_option("--description-file",
                      dest="description_file", default=None,
                      help="text file containing a description of the review")
    parser.add_option("--guess-summary",
                      dest="guess_summary", action="store_true",
                      default=False,
                      help="guess summary from the latest commit (git/"
                           "hg/hgsubversion only)")
    parser.add_option("--guess-description",
                      dest="guess_description", action="store_true",
                      default=False,
                      help="guess description based on commits on this branch "
                           "(git/hg/hgsubversion only)")
    parser.add_option("--testing-done",
                      dest="testing_done", default=None,
                      help="details of testing done ")
    parser.add_option("--testing-done-file",
                      dest="testing_file", default=None,
                      help="text file containing details of testing done ")
    parser.add_option("--branch",
                      dest="branch", default=None,
                      help="affected branch ")
    parser.add_option("--bugs-closed",
                      dest="bugs_closed", default=None,
                      help="list of bugs closed ")
    parser.add_option("--revision-range",
                      dest="revision_range", default=None,
                      help="generate the diff for review based on given "
                           "revision range")
    parser.add_option("--label",
                      dest="label", default=None,
                      help="label (ClearCase Only) ")
    parser.add_option("--submit-as",
                      dest="submit_as", default='SUBMIT_AS', metavar="USERNAME",
                      help="user name to be recorded as the author of the "
                           "review request, instead of the logged in user")
    parser.add_option("--username",
                      dest="username", default=None, metavar="USERNAME",
                      help="user name to be supplied to the reviewboard server")
    parser.add_option("--password",
                      dest="password", default=None, metavar="PASSWORD",
                      help="password to be supplied to the reviewboard server")
    parser.add_option("--change-only",
                      dest="change_only", action="store_true",
                      default=False,
                      help="updates info from changelist, but does "
                           "not upload a new diff (only available if your "
                           "repository supports changesets)")
    parser.add_option("--parent",
                      dest="parent_branch", default=None,
                      metavar="PARENT_BRANCH",
                      help="the parent branch this diff should be against "
                           "(only available if your repository supports "
                           "parent diffs)")
    parser.add_option("--tracking-branch",
                      dest="tracking", default=None,
                      metavar="TRACKING",
                      help="Tracking branch from which your branch is derived "
                           "(git only, defaults to origin/master)")
    parser.add_option("--p4-client",
                      dest="p4_client", default=None,
                      help="the Perforce client name that the review is in")
    parser.add_option("--p4-port",
                      dest="p4_port", default=None,
                      help="the Perforce servers IP address that the review is on")
    parser.add_option("--repository-url",
                      dest="repository_url", default=None,
                      help="the url for a repository for creating a diff "
                           "outside of a working copy (currently only "
                           "supported by Subversion with --revision-range or "
                           "--diff-filename and ClearCase with relative "
                           "paths outside the view)")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default='DEBUG',
                      help="display debug output")
    parser.add_option("--diff-filename",
                      dest="diff_filename", default=None,
                      help='upload an existing diff file, instead of '
                           'generating a new diff')

    (globals()["options"], args) = parser.parse_args(args)

    if options.description and options.description_file:
        sys.stderr.write("The --description and --description-file options "
                         "are mutually exclusive.\n")
        sys.exit(1)

    if options.description_file:
        if os.path.exists(options.description_file):
            fp = open(options.description_file, "r")
            options.description = fp.read()
            fp.close()
        else:
            sys.stderr.write("The description file %s does not exist.\n" %
                             options.description_file)
            sys.exit(1)

    if options.testing_done and options.testing_file:
        sys.stderr.write("The --testing-done and --testing-done-file options "
                         "are mutually exclusive.\n")
        sys.exit(1)

    if options.testing_file:
        if os.path.exists(options.testing_file):
            fp = open(options.testing_file, "r")
            options.testing_done = fp.read()
            fp.close()
        else:
            sys.stderr.write("The testing file %s does not exist.\n" %
                             options.testing_file)
            sys.exit(1)

    if options.reopen and not options.rid:
        sys.stderr.write("The --reopen option requires "
                         "--review-request-id option.\n")
        sys.exit(1)

    return args

def main():
    args = parse_options(sys.argv[1:])
    
    #setup()
    listsets()

if __name__ == '__main__':
    main()

