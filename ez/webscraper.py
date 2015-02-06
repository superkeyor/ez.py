import urllib, urllib2, re, urlparse, os, sys, string
from webscraping.xpath import Doc
import webscraping.common as common

__doc__ = """
Attributes:
    name
    url
    html    # html code
Methods:
    __init__(source, render=False, name=None)
        # source could be url or string code
        # render requires wx/webkit to parse html
        # internally update the scraper object's attributes (e.g. url, html)
    xpath(xpath, first=False)    # first=False returns all matched as a list; first=True, first matched as string

Examples:
    / = root, // = all, [] = constriction, @ = attributes

    s = Scraper('<div>abc<a class="link">LINK 1</a><div><a>LINK 2</a>def</div>abc</div>ghi<div><a>LINK 3</a>jkl</div>')
    
    print s.xpath('/div/a')
    # ['LINK 1', 'LINK 3']

    print s.xpath('/div/a[@class="link"]')
    # ['LINK 1']

    print s.xpath('/div[1]//a')
    # ['LINK 1', 'LINK 2']

    print s.xpath('/div/a/@class')
    # ['link', '']

    print s.xpath('/div[-1]/a')
    # ['LINK 3']

    s = Scraper(u'<a href="http://www.google.com" class="flink">google</a>')
    print s.xpath('//a[@class="flink"]', 1)
    # 'google'

    # test finding just the first instance for a large amount of content
    s = Scraper('<div><span>content</span></div>' * 10000)
    print s.xpath('//span', 1)
    # 'content'

    # test extracting attribute of self closing tag
    s = Scraper('<div><img src="img.png"></div>')
    print s.xpath('/div/img/@src', 1)
    # 'img.png'

    # test extracting attribute after self closing tag
    s = Scraper('<div><br><p>content</p></div>')
    print s.xpath('/div/p')
    # 'content'

Sample:
    import time
    COL_NAME = "Words_And_Idioms"

    output = open(COL_NAME+".txt", 'w')

    for i in range(1,2):
        first = Scraper("http://www.51voa.com/"+COL_NAME+"_"+str(i)+".html")
        time.sleep(1)
        lists = first.xpath("//li")
        for item in lists:
            if "/Voa_English_Learning/" in item:
                temp = Scraper(item)
                time.sleep(1)
                link = "http://www.51voa.com"+temp.xpath("/@href",1)
                second = Scraper(link)
                time.sleep(1)
                try:
                    download = re.search("/.*/.*mp3", second.html).group(0)
                except:
                    download = "missing"
                print >> output, "http://stream.51voa.com"+download
                output.flush()
"""
    
class Scraper(object):
    """
    Attributes:
        name
        url
        html    # html code
    Methods:
        __init__(source, render=False, name=None)
            # source could be url or string code
            # render requires wx/webkit to parse html
            # internally update the scraper object's attributes (e.g. url, html)
        xpath(xpath, first=False)    # first=False returns all matched as a list; first=True, first matched as string

    Examples:
        / = root, // = all, [] = constriction, @ = attributes

        s = Scraper('<div>abc<a class="link">LINK 1</a><div><a>LINK 2</a>def</div>abc</div>ghi<div><a>LINK 3</a>jkl</div>')
        
        print s.xpath('/div/a')
        # ['LINK 1', 'LINK 3']

        print s.xpath('/div/a[@class="link"]')
        # ['LINK 1']

        print s.xpath('/div[1]//a')
        # ['LINK 1', 'LINK 2']

        print s.xpath('/div/a/@class')
        # ['link', '']

        print s.xpath('/div[-1]/a')
        # ['LINK 3']

        s = Scraper(u'<a href="http://www.google.com" class="flink">google</a>')
        print s.xpath('//a[@class="flink"]', 1)
        # 'google'

        # test finding just the first instance for a large amount of content
        s = Scraper('<div><span>content</span></div>' * 10000)
        print s.xpath('//span', 1)
        # 'content'

        # test extracting attribute of self closing tag
        s = Scraper('<div><img src="img.png"></div>')
        print s.xpath('/div/img/@src', 1)
        # 'img.png'

        # test extracting attribute after self closing tag
        s = Scraper('<div><br><p>content</p></div>')
        print s.xpath('/div/p')
        # 'content'

    Sample:
        import time
        COL_NAME = "Words_And_Idioms"

        output = open(COL_NAME+".txt", 'w')

        for i in range(1,2):
            first = Scraper("http://www.51voa.com/"+COL_NAME+"_"+str(i)+".html")
            time.sleep(1)
            lists = first.xpath("//li")
            for item in lists:
                if "/Voa_English_Learning/" in item:
                    temp = Scraper(item)
                    time.sleep(1)
                    link = "http://www.51voa.com"+temp.xpath("/@href",1)
                    second = Scraper(link)
                    time.sleep(1)
                    try:
                        download = re.search("/.*/.*mp3", second.html).group(0)
                    except:
                        download = "missing"
                    print >> output, "http://stream.51voa.com"+download
                    output.flush()
    """

    def __init__(self, source, render=False, name=None):
        super (Scraper, self).__init__()
        self.name = name

        if source.startswith('http://') or source.startswith('https://'):
            self.url = source
            if render==False:
                self.html = urllib2.urlopen(self.url).read()
                # parsed webpage as Doc() object, don't use from external
                self._doc = Doc(self.html)
            else:
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                # render javascript with qt webkit
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                try:
                    import wx 
                    import wx.html2
                    import re

                    class Render(wx.Frame):
                        def __init__(self, url): 
                            self.pagetext = ''
                            self.app = wx.App()

                            wx.Frame.__init__(self, None, -1) 
                            sizer = wx.BoxSizer(wx.VERTICAL)
                            self.browser = wx.html2.WebView.New(self)
                            sizer.Add(self.browser, 1, wx.EXPAND, 10) 
                            self.SetSizer(sizer) 
                            self.SetSize((700, 700))

                            self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.OnLoaded, self.browser)

                            self.browser.LoadURL(url)
                            # self.Show()
                            self.app.MainLoop()
                            
                        def OnLoaded(self, evt):
                            if(not self.browser or self.browser.IsBusy()): return
                            self.pagetext = self.browser.GetPageText()
                            self.pagetext = common.to_ascii(self.pagetext)
                            self.app.ExitMainLoop()
                     
                    self.html = Render(self.url).pagetext
                    self._doc = Doc(self.html)
                except ImportError:
                    # raise Exception("Does not have the necessary libraries to render the webpage")
                    self.html = "Does not have the necessary libraries to render the webpage"
                    self._doc = Doc(self.html)
        else:
            self.url = None
            self.html = source
            self._doc = Doc(self.html)

    def __str__(self):
        return self.html
        # return self

    def xpath(self, xpath_pattern, first=False):
        if first==False:
            result = self._doc.search(xpath_pattern) if xpath_pattern else [self.html]
            result = [common.to_ascii(re.sub(r'\n|\r', '', r)) for r in result]
            return result
        else:
            result = self._doc.get(xpath_pattern) if xpath_pattern else self.html
            result = common.to_ascii(re.sub(r'\n|\r', '', result))
            return result

if __name__ == "__main__":
    a = Scraper('http://www.zhupsy.com',1)
    print a.html
    
#    import time
#    COL_NAME = "Words_And_Idioms"
#
#    output = open(COL_NAME+".txt", 'w')
#
#    for i in range(1,2):
#        first = Scraper("http://www.51voa.com/"+COL_NAME+"_"+str(i)+".html")
#        time.sleep(1)
#        lists = first.xpath("//li")
#        for item in lists:
#            if "/Voa_English_Learning/" in item:
#                temp = Scraper(item)
#                time.sleep(1)
#                link = "http://www.51voa.com"+temp.xpath("/@href",1)
#                second = Scraper(link)
#                time.sleep(1)
#                try:
#                    download = re.search("/.*/.*mp3", second.html).group(0)
#                except:
#                    download = "missing"
#                print >> output, "http://stream.51voa.com"+download
#                output.flush()
    
    # # / = root, // = all, [] = constriction, @ = attributes

    # s = Scraper('<div>abc<a class="link">LINK 1</a><div><a>LINK 2</a>def</div>abc</div>ghi<div><a>LINK 3</a>jkl</div>')
        
    # print s.xpath('/div/a')
    # # ['LINK 1', 'LINK 3']

    # print s.xpath('/div/a[@class="link"]')
    # # ['LINK 1']

    # print s.xpath('/div[1]//a')
    # # ['LINK 1', 'LINK 2']

    # print s.xpath('/div/a/@class')
    # # ['link', '']

    # print s.xpath('/div[-1]/a')
    # # ['LINK 3']

    # s = Scraper(u'<a href="http://www.google.com" class="flink">google</a>')
    # print s.xpath('//a[@class="flink"]', 1)
    # # 'google'

    # # test finding just the first instance for a large amount of content
    # s = Scraper('<div><span>content</span></div>' * 10000)
    # print s.xpath('//span', 1)
    # # 'content'

    # # test extracting attribute of self closing tag
    # s = Scraper('<div><img src="img.png"></div>')
    # print s.xpath('/div/img/@src', 1)
    # # 'img.png'

    # # test extracting attribute after self closing tag
    # s = Scraper('<div><br><p>content</p></div>')
    # print s.xpath('/div/p')
    # # 'content'