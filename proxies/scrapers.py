import Image
import re

from browser.functions import *
from proxies.models import *

# Module not yet in use - commented to prevent dependency.
# See: http://github.com/hoffstaetter/python-tesseract
#from tesseract import image_to_string

'''
Use at your own risk, these functions will pull proxies based on the listing. Some of them will test for a valid connection though none test what type of proxy is in place.
IE: A Proxy labeled High Anonymous may be transparent
'''

#TODO: Convert this collection into a single object class.

def ProxyListsHttp():
    '''
    Scrape the High anonymity http proxy list from proxylists.net. Uses the published text file as a source.
    return
        int: number of proxy servers added
    '''
    try:
        source = ProxySource.objects.get(url='http://www.proxylists.net/http_highanon.txt')
    except:
        source = ProxySource(url='http://www.proxylists.net/http_highanon.txt')
        source.save()

    scraped_list = ReadPage(source.url)
    proxy_list = scraped_list.split('\r\n')
    i = 0
    for proxy in proxy_list:
        if len(proxy) > 1:
            obj = proxy.split(':')
            
            try:
                check_proxy = ProxyServer.objects.get(address=obj[0])
            except:
                check_proxy = False

            if check_proxy:
                check_proxy.last_checked = datetime.now()
                check = ProxyCheckHttp(check_proxy)
                if not check:
                    check_proxy.active = False
                check_proxy.save()
            else:
                new_proxy = ProxyServer(address=obj[0], port=obj[1], proxy_type='http', source=source, anonymous=True)
                check = ProxyCheckHttp(new_proxy)
                if check:
                    new_proxy.active = True
                new_proxy.save()
            i += 1
            print 'Added proxy %s' % (proxy)
    return i

def ProcessHidemyassList(page):
    '''
    INCOMPLETE!!!
    Scrapes list of proxies from HideMyAss.com
    HideMyAss.com publishes ports using an image rather than a text field (to prevent scripts like this most likely *grin*).
    Somewhere low on my todo list is preparing those images to be run through tesseract OCR to automate the process.
    '''
    soup = BeautifulSoup(page)
    table = soup.findAll(attrs={'id' : 'proxylist-table'})
    rows = table[0].findAll('tr')
    rows.pop(0)

    count = 0

    for row in rows:
        cells = row.findAll('td')
        match = re.search(r'HTTP', str(cells[6]))
        if cells[7].contents[0] == 'High' and match:
            f = br.retrieve('%s%s' % (getrooturl(br), cells[2].img['src']))[0]
#TODO: Test and add processing for image
            #port = image_to_string(Image.open(f))
            port = 0

            match = re.search(r'width: (\d+)', str(cells[4].li))
            response_time = 100 - int(match.group(1))
            match = re.search(r'width: (\d+)', str(cells[5].li))
            connection_time = 100 - int(match.group(1))

            proxy = ProxyServer(
                address = cells[1].contents[0],
                port = port,
                proxy_type = cells[6].contents[0],
                active = True,
                source = source,
                anonymouse = True,
                country = cells[3].contents[1],
                respose_time = response_time,
                connection_time = connection_time
                )
            proxy.save()
            count += 1
    return count

def ScrapeHidemyassList():
    source = ProxySource.objects.get(url='http://www.hidemyass.com/proxy-list/')
    if not source:
        source = ProxySource(url = 'http://www.hidemyass.com/proxy-list/', proxy_type='Various')
        source.save()

    br = BuildBrowser()
    i = 1
    count = 0
    while i <= 20:
        url = source.url
        if i > 1:
            url += i
        page = br.open(url).read()
        count += ProcessHidemyassList(page)
        #soup = BeautifulSoup(page)
        #get full page count
        #soup.findAll(attrs={'class' : 'pagination'})[0].findAll('a')[-2].contents[0]
        #get next link
        #soup.findAll(attrs={'class' : 'pagination'})[0].findAll(attrs={'class' : 'next'})[0]['href']
    return count


class ProxyScrapeSamair(object):
    '''
    Object class to scrape updated proxy lists from samair.ru.
    Entire clas was put together quickly to Work in the methodology of Make it Work, Make it Right, Make it Fast.
    Class works though there are deffinetely cleaner ways to implement much of the processing. Highly ineffecient though shouldn't need to be run very often.
    To begin scrape simple initiate class from console and watch it run.
    '''
    def __init__(self, br=False):
        proxy_source = ProxySource.objects.filter(url__startswith='http://www.samair.ru')
        if proxy_source:
            self.proxy_source = proxy_source[0]
        else:
            proxy_source = ProxySource(url='http://www.samair.ru/proxy/proxy-01.htm', anonymous=True, proxy_type='various')
            proxy_source.save()
            self.proxy_source = proxy_source
        self.url = self.proxy_source.url
        if br:
            self.br = br
        else:
            self.br = BuildBrowser()
        self.soup = False
        self.PullPages()

    def ParsePage(self, page):
        result = re.findall(r"(\w)=(\d)", page)
        self.soup = BeautifulSoup(page)
        rows = self.soup.findAll('table', attrs={'class':'tablelist'})[0].findAll('tr')
        rows.pop(0)
        for row in rows:
            if not row.a and str(row).count('high-anonymous'):
                cells = row.findAll('td')
                match = re.search(r'>([\d\.]+)<', str(cells[0]))
                if match:
                    ip_address = match.group(1)
                    dup_check = ProxyServer.objects.filter(address=ip_address)
                    if dup_check:
                        continue
                else:
                    continue
                match = re.search(r'":"(.*?)\)', str(cells[0]))
                if match:
                    port_encoded = match.group(1).split('+')
                    port = ''
                    for n in port_encoded:
                        if len(n) > 0:
                            port += dict(result)[n]
                else:
                    continue
                
                proxy = ProxyServer(
                    address = ip_address,
                    port = port,
                    source = self.proxy_source,
                    anonymous = True,
                    country = cells[3].contents[0]
                    )
                proxy.save()
                print 'Added proxy: %s - %s:%s - %s' % (proxy.id, ip_address, port, cells[1].contents[0])
        self.PullPages()

    def PullPages(self):
        if self.soup:
            nav = self.soup.findAll(attrs={'class':'list_navigation'})
            match = re.search(r'<a.*?"(.*?)".*?>next</a>', str(nav))
            if match:
                self.url = match.group(1)
        print 'Processing page: %s' % (self.url)
        page = self.br.open(self.url).read()
        if page:
            self.ParsePage(page)

