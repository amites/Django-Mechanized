from datetime import datetime
import httplib
import urllib
import xmlrpclib

from browser.functions import *
from proxies.models import *

def ProxyRandom(url=False):
    '''
    Shortcut to pull proxy server at random, tested to be an active proxy.
    return
        ProxyServer object
    '''
    check = False
    while not check:
        proxy = ProxyServer.objects.filter(active=True).order_by('?')[0]
        check = ProxyCheckHttp(proxy, url)
    return proxy


#TODO: improve connection testing (response time, validate country, test anonymity, etc...)
def ProxyCheckHttp(proxy, url='http://www.google.com'):
    '''
    Check if proxy server is active.
    input
        proxy = ProxyServer objects
        url = URL to be opened in testing, defaults to Google.
    return
        boolean value
    '''

    if proxy.proxy_type == 'http':
        try:
            urllib.urlopen(
                url,
                proxies={'http':'http://%s:%s' % (proxy.address, proxy.port)}
            )
            return True
        except IOError:
            print "Connection error! (Proxy: %s - %s)" % (proxy.id, proxy.address)
            proxy.active = False
            proxy.save()
    return False


class ProxiedTransport(xmlrpclib.Transport):
    '''
    Minor tweaks to Python Docs example of extending xmlrpclib to use a proxy.
    '''
    def set_proxy(self, proxy=False):
        '''
        Set proxy to use in xmlrpclib, accepts 3 options:
            Proxy address string.
            ProxyServer instance.
            Boolean value False (default) = Use random proxy.
        '''
        if isinstance(proxy, str):
            self.proxy = proxy
        else
            if not isinstance(proxy, ProxyServer):
                proxy = ProxyRandom()
            self.proxy = '%s:%s' % (proxy.address, proxy.port)

    def make_connection(self, host):
        self.realhost = host
        h = httplib.HTTP(self.proxy)
        return h

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)
