import urllib

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import cookielib
import mechanize

def BuildBrowser(proxy=False, cookies=False, debug=False):
    '''
     Build a Mechanize Browser Instance.
     input:
        proxy = ProxyServer object
        cookies = use mechanize cookiejar
        debug = set debug handlers
     return:
        browser instance
    '''
    # Browser
    br = mechanize.Browser()
    
    if proxy:
        br.set_proxies({'http' : '%s:%s' % (proxy.address,proxy.port)})

    if cookies:
        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    if debug:
        br.set_debug_http(True)
        br.set_debug_redirects(True)
        br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13')]
    return br

def ReadPageResponse(url, data=False, proxy=False, run=True):
    if data:
        vals = urllib.urlencode(data)
        req = mechanize.Request(url, vals)
    else:
        req = mechanize.Request(url)
    count = 0
    while run:
        try:
            response = mechanize.urlopen(req)
            run = False
        except:
            count += 1
            print "Unable to connect - trying again - count: %s." % count
    return response

#########################################################################
# Shortcuts to work with Browser Objects
#########################################################################

def getrooturl(br):
    url_list = str(br.geturl()).split('/')
    return '%s//%s' % (url_list[0], url_list[2])


def tryopenurl(br, url):
    try:
        page = br.open(url).read()
    except HTTPError, e:
        print e.code
        page = e.read()
    return page

#########################################################################
# Shortcuts to work with web-pages
#########################################################################

## pull page
def ReadPage(url, data=False, proxy=False, run=True):
    response = ReadPageResponse(url, data, proxy, run)
    return response.read()

#pull page and return mechanize forms
def ReadPageForms(url, data=False, proxy=False, run=True):
    response = ReadPageResponse(url, data, proxy, run)
    return mechanize.ParseResponse(response, backwards_compat=False)

#pull page and return mechanize form (singular)
def ReadPageForm(url, form_num=0, data=False, proxy=False, run=True):
    forms = ReadPageForms(url, data, proxy, run)
    return forms[form_num]

