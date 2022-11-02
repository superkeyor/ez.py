# eg.
# e=f.find('linktext','Download')
# e.click()
# e.send(KEYS.COMMAND,KEYS.SHIFT,KEYS.ARROW_LEFT)
# e.send(KEYS.COMMAND,'a')
# e.submit(), e.sendsubmit()
# f.findall(By.CLASS_NAME,'d2l-datetime-selector-date-input.d2l-edit')  
# https://stackoverflow.com/questions/17000703/is-string-matches-supported-in-selenium-webdriver-2
# https://stackoverflow.com/questions/22436789/xpath-ends-with-does-not-work
# f.findall('xpath','//*[starts-with(@id,"z_")]')  #contains(), but matches() ends-with() not supported by webdriver/xpath1.0
# f.findall('xpath','//*[contains(@id,"time")][contains(@title,"Date")]')
# f.findsel('id','activity--history',timeout=10).select_by_visible_text('history')
#                                               .select_by_value()
#                                               .select_by_index(2)  # 0-based
#                                               .options[1].text  # first option's text
# select = f.findsel('id','period_1_id',timeout=10)
# options = select.options
# for i in range(0,len(options)):
#     option = options[i]
#     if 'In Progress' in option.text:
#         f.findsel('id','period_1_id',timeout=10).select_by_index(i)
# f.save_screenshot()                                        | f.snap()
# f.js_click(e)                                              | f.click(e)
# f.js_rightclick(e)                                         | f.rclick(e)
# f.js_setvalue(e,value)                                     | 
# f.js_setvalue_via_typing(e,value)  # essentially send keys | f.send(e,value)
# f.execute_script("arguments[0].click();", e)
# f.execute_script(f"arguments[0].value='{smscode}';", f.find('id','code'))
# f.driver is the native webdriver object

# modified from https://github.com/kkristof200/selenium_firefox
# By.CLASS_NAME is a string: 'class name'; I remapped: 
# 'class': By.CLASS_NAME,
# 'linktext': By.LINK_TEXT,
# 'partiallinktext': By.PARTIAL_LINK_TEXT,
# 'css': By.CSS_SELECTOR,
# 'id': By.ID,
# 'name': By.NAME,
# 'xpath': By.XPATH,
# 'tag': By.TAG_NAME,

# xpath quick syntax:
# //tagname/child[@Attribute='value']
# //p[contains(text(),"Unit A")][1]  --1 based
# (//input[@type="RADIO"])[2]

# config
# http://kb.mozillazine.org/Firefox_%3A_FAQs_%3A_About%3Aconfig_Entries

# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Union, List, Dict, Callable, Tuple
import pickle, os, time, json, inspect, platform, tempfile, re

# Pip
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as by
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from fake_useragent import UserAgent
import tldextract

By = by
BY = by
KEYS = Keys
# ---------------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------------- Defines ---------------------------------------------------------------- #

RANDOM_USERAGENT = 'random'

# ---------------------------------------------------------------------------------------------------------------------------------------- #


# ------------------------------------------------------------ class: Firefox ------------------------------------------------------------ #

class Firefox:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        url = 'https://bot.sannysoft.com/',
        headless: bool = False,
        wire: bool = False, # Use seleniumwire only when necessary, because it would slow things down a bit (not working if session is True)
        session: bool = False, # Use seleniumrequests for cross-session cookies (overrides wire)
        wait_ajax = 60 if platform.system()=='Linux' else 10,
        default_find_func_timeout: int = 3,
        service_log_path: Optional[str] = os.devnull,
        log_path: Optional[str] = os.devnull,
        cookies_folder_path: Optional[str] = None, # not working? Use session instead
        extensions_folder_path: Optional[str] = None, # about:support  ~/Library/Application Support/Firefox/Profiles/h7d5u192.default-esr/extensions
        host: Optional[str] = None,
        port: Optional[int] = None,
        cookies_id: Optional[str] = None,
        firefox_binary_path: Optional[str] = None,
        # proxy: Optional[str] = None,
        profile_path: Optional[str] = None,
        download_path: Optional[str] = None,  # None will generate a temp folder (and auto deleted when done)
        private: bool = False,
        screen_size: Optional[Tuple[int, int]] = None, # (width, height)
        full_screen: bool = False,
        max_window: bool = True,  # overrides full_screen
        language: str = 'en-us',
        manual_set_timezone: bool = False,
        user_agent: Optional[str] = None,  # random
        load_proxy_checker_website: bool = False,
        disable_images: bool = False,
        auto_close: bool = True, # no auto_close for keyboard maestro
        *args, **kwargs
    ):
        '''EITHER PROVIDE 'cookies_id' OR  'cookies_folder_path'.
           IF 'cookies_folder_path' is None, 'cokies_id', will be used to calculate 'cookies_folder_path'
           IF 'cokies_id' is None, it will become 'test'

           wait_ajax: seconds
           I should mention that the webdriver will wait for a page to load by default. It does not wait for
           loading inside frames or for ajax requests. It means when you use .get('url'), your browser will
           wait until the page is completely loaded and then go to the next command in the code. But when you
           are posting an ajax request, webdriver does not wait and it's your responsibility to wait an
           appropriate amount of time for the page or a part of page to load; so there is a module named
           expected_conditions.
        '''
        self.auto_close=auto_close  # for destructor
        # force headless on linux
        if platform.system()=='Linux':
            headless=True
        
        if wire:
            from seleniumwire import webdriver
        else:
            from selenium import webdriver

        self.wait_ajax = wait_ajax
        self.default_find_func_timeout = default_find_func_timeout

        if cookies_folder_path is None:
            cookies_id = cookies_id or 'test'

            current_folder_path = os.path.dirname(os.path.abspath(__file__))
            general_cookies_folder_path = os.path.join(current_folder_path, 'cookies')
            os.makedirs(general_cookies_folder_path, exist_ok=True)

            cookies_folder_path = os.path.join(general_cookies_folder_path, cookies_id)

        self.cookies_folder_path = cookies_folder_path
        os.makedirs(self.cookies_folder_path, exist_ok=True)

        user_agent_file_path = os.path.join(cookies_folder_path, 'ua.txt')

        if user_agent:
            user_agent = user_agent.strip()

            if not os.path.exists(user_agent_file_path):
                with open(user_agent_file_path, 'w') as f:
                    f.write(user_agent)
        else:
            if os.path.exists(user_agent_file_path):
                with open(user_agent_file_path, 'r') as f:
                    user_agent = f.read()

        if download_path is None: download_path = tempfile.TemporaryDirectory().name
        self.download_path = download_path

        if service_log_path is None: service_log_path = tempfile.TemporaryDirectory().name
        if log_path is None: log_path = tempfile.TemporaryDirectory().name

        import selenium
        profile = selenium.webdriver.FirefoxProfile(profile_path if profile_path and os.path.exists(profile_path) else None)
        # https://erayerdin.com/how-to-make-selenium-load-faster-with-firefox-in-python-ck7ncjyvw00sd8ss1v4i5xob1
        profile.set_preference('browser.formfill.enable', False)
        profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
        profile.set_preference("extensions.checkUpdateSecurity", False)
        profile.set_preference("extensions.update.autoUpdateEnabled", False)
        profile.set_preference("extensions.update.enabled", False)

        if user_agent is not None:
            if user_agent == RANDOM_USERAGENT:
                user_agent_path = os.path.join(cookies_folder_path, 'user_agent.txt')

                if os.path.exists(user_agent_path):
                    with open(user_agent_path, 'r') as file:
                        user_agent = file.read().strip()
                else:
                    user_agent = self.__random_firefox_user_agent(min_version=60.0)
                    
                    with open(user_agent_path, 'w') as file:
                        file.write(user_agent)

            profile.set_preference('general.useragent.override', user_agent)
        
        if language is not None:
            profile.set_preference('intl.accept_languages', language)

        if private:
            profile.set_preference('browser.privatebrowsing.autostart', True)
        
        if disable_images:
            profile.set_preference('permissions.default.image', 2)
            profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
        
        if host is not None and port is not None:
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.http', host)
            profile.set_preference('network.proxy.http_port', port)
            profile.set_preference('network.proxy.ssl', host)
            profile.set_preference('network.proxy.ssl_port', port)
            profile.set_preference('network.proxy.ftp', host)
            profile.set_preference('network.proxy.ftp_port', port)
            profile.set_preference('network.proxy.socks', host)
            profile.set_preference('network.proxy.socks_port', port)
            profile.set_preference('network.proxy.socks_version', 5)
            profile.set_preference('signon.autologin.proxy', True)
        
        profile.set_preference('marionatte', False)
        profile.set_preference('dom.webdriver.enabled', False)
        profile.set_preference('media.peerconnection.enabled', False)
        profile.set_preference('useAutomationExtension', False)

        # https://stackoverflow.com/questions/18439851/how-can-i-download-a-file-on-a-click-event-using-selenium
        # https://selenium-python.readthedocs.io/faq.html#how-to-auto-save-files-using-custom-firefox-profile
        # use HTTPHeaderLive plugin to check, e.g., application/force-download
        # most reliable: about:support, profile folder->handlers.json see waht has changed
        #   how I discovered: use fsmonitor (https://fsmonitor.com/)->download manually and "do this automatically"->about:support, profile folder->handlers.json see waht has changed
        #   https://www.reddit.com/r/selenium/comments/m3og31/how_do_i_download_blobhttps_files/gqq88ha?utm_source=share&utm_medium=web2x&context=3
        profile.set_preference('browser.download.folderList', 2) # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', download_path)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', "text/csv,application/force-download,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/x-msexcel,application/excel,application/x-excel,application/vnd.ms-excel,image/png,image/jpeg,image/svg+xml,text/html,text/plain,application/msword,application/xml,application/x-gzip,application/octet-stream")

        profile.set_preference('general.warnOnAboutConfig', False)
        profile.update_preferences()
        options = FirefoxOptions()

        if headless:
            options.add_argument('--headless')

        # specify screen size (width, height)
        # otherwise, it would obscure some contents or not work the same under headless
        if screen_size is None:
            screen_size = (1920,1080)

        if screen_size is not None:
            options.add_argument('--width={}'.format(screen_size[0]))
            options.add_argument('--height={}'.format(screen_size[1]))

        # if proxy:
        #     if type(proxy) == str:
        #         proxy = proxy.strip().lstrip('https://').lstrip('http://').lstrip('ftp://')

        #         seleniumwire_options['proxy'] = {
        #             'https': 'https://{}'.format(proxy),
        #             'http': 'http://{}'.format(proxy),
        #             'ftp': 'ftp://{}'.format(proxy)
        #         }
        # else:
        #     seleniumwire_options = None

        ff_binary = FirefoxBinary(firefox_path=firefox_binary_path) if firefox_binary_path and os.path.exists(firefox_binary_path) else None
        
        if session:
            from seleniumrequests import Firefox
            self.driver = Firefox(
                firefox_profile=profile,
                options=options,
                service_log_path=service_log_path,
                log_path=log_path,
                firefox_binary=ff_binary,
                *args, **kwargs
            )
        else: 
            if not wire:
                self.driver = webdriver.Firefox(
                    firefox_profile=profile,
                    options=options,
                    service_log_path=service_log_path,
                    log_path=log_path,
                    firefox_binary=ff_binary,
                    *args, **kwargs
                )
            else:
                seleniumwire_options = {
                    'suppress_connection_errors': True
                }
                self.driver = webdriver.Firefox(
                    firefox_profile=profile,
                    options=options,
                    seleniumwire_options=seleniumwire_options,
                    service_log_path=service_log_path,
                    log_path=log_path,
                    firefox_binary=ff_binary,
                    *args, **kwargs
                )
        
        if full_screen:
            self.driver.fullscreen_window()

        if max_window:
            self.driver.maximize_window()

        if extensions_folder_path is not None:
            try:
                change_timezone_id = None

                for (dirpath, _, filenames) in os.walk(extensions_folder_path):
                    for filename in filenames:
                        if filename.endswith('.xpi') or filename.endswith('.zip'):
                            addon_id = self.driver.install_addon(os.path.join(dirpath, filename), temporary=False)

                            if 'change_timezone' in filename:
                                change_timezone_id = addon_id

                # self.driver.get("about:addons")
                # self.driver.find_element_by_id("category-extension").click()
                # self.driver.execute_script("""
                #     let hb = document.getElementById("html-view-browser");
                #     let al = hb.contentWindow.window.document.getElementsByTagName("addon-list")[0];
                #     let cards = al.getElementsByTagName("addon-card");
                #     for(let card of cards){
                #         card.addon.disable();
                #         card.addon.enable();
                #     }
                # """)

                while len(self.driver.window_handles) > 1:
                    time.sleep(0.5)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                
                self.driver.switch_to.window(self.driver.window_handles[0])

                if change_timezone_id is not None and manual_set_timezone:
                    if host is not None and port is not None:
                        self.open_new_tab('https://whatismyipaddress.com/')
                        time.sleep(0.25)

                    self.open_new_tab('https://www.google.com/search?client=firefox-b-d&q=my+timezone')
                    time.sleep(0.25)

                    self.driver.switch_to.window(self.driver.window_handles[0])
                    
                    input('\n\n\nSet timezone.\n\nPress ENTER, when finished. ')
                
                    while len(self.driver.window_handles) > 1:
                        time.sleep(0.5)
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        self.driver.close()
                    
                    self.driver.switch_to.window(self.driver.window_handles[0])
                elif load_proxy_checker_website and host is not None and port is not None:
                    self.driver.get('https://whatismyipaddress.com/')
            except:
                while len(self.driver.window_handles) > 1:
                    time.sleep(0.5)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()

        # https://akarin.dev/2022/02/15/disable-geckodriver-detection-with-addon/
        # customized addon, xpi is zip
        # can be found at about:addons
        HERE=os.path.dirname(os.path.abspath(__file__))
        self.driver.install_addon(os.path.join(HERE,'firefox.xpi'), temporary=True)
        if url is not None: self.driver.get(url)

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #
    def install(self,xpi,signed=True):
        """
        signed: the package has been signed or not
        """
        self.driver.install_addon(xpi, temporary=(not signed))

    def wait(self,seconds=None):
        if seconds is None: seconds=self.wait_ajax
        time.sleep(seconds)
    sleep=wait

    def downloaded(self, filename, timeout=20):
        file_path = os.path.join(self.download_path,filename)
        seconds = 0
        while (not os.path.exists(file_path)) and (seconds < timeout):
            time.sleep(1)
            seconds += 1
        return os.path.exists(file_path)

    def login_via_cookies(self, url: str, needed_cookie_name: Optional[str] = None) -> bool:
        org_url = self.driver.current_url
        self.driver.get(url)
        time.sleep(1)

        try:
            if self.has_cookies_for_current_website():
                self.load_cookies()
                time.sleep(1)
                self.driver.get(url)
            else:
                self.driver.get(url)

                return False

            for cookie in self.driver.get_cookies():
                if needed_cookie_name is not None:
                    if 'name' in cookie and cookie['name'] == needed_cookie_name:
                        self.driver.get(url)

                        # seems to be most reliable by detection of password input
                        if self.find('xpath', '//input[@type="password"]') is None:
                            return True # sucessfully loaded and cookie not expired yet
                        else:
                            return False
                else:
                    for k, v in cookie.items():
                        if k == 'expiry':
                            if v - int(time.time()) < 0:
                                self.driver.get(url)

                                return False
            
            # for return from above has_cookies_for_current_website()
            # seems to be most reliable by detection of password input
            if self.find('xpath', '//input[@type="password"]') is None:
                return True # sucessfully loaded and cookie not expired yet
            else:
                return False
        
        except Exception as e:
            print(e)
            self.driver.get(url)

            return False

    def quit(self,delete_download_path=False):
        if delete_download_path:
            import shutil
            try:
                shutil.rmtree(self.download_path)
            except:
                pass
        return self.driver.quit()

    @property
    def title(self):
        return self.driver.title

    # title2 quote to escape / to avoid the confusion when title is used for file name
    @property
    def title2(self):
        import urllib.parse
        return urllib.parse.quote_plus(self.driver.title)
        
    @property
    def url(self):
        return self.driver.current_url

    @property
    def source(self):
        return self.driver.page_source

    def get_cookies(self,*args,**kwargs):
        return self.driver.get_cookies(*args,**kwargs)

    def get_cookie(self,*args,**kwargs):
        return self.driver.get_cookie(*args,**kwargs)
    
    def save_screenshot(self,*args,**kwargs):
        return self.driver.save_screenshot(*args,**kwargs)
    snap=save_screenshot
    
    def has_cookie(self, cookie_name: str) -> bool:
        for cookie in self.driver.get_cookies():
            if 'name' in cookie and cookie['name'] == cookie_name:
                return True

        return False

    def get(
        self,
        url: str,
        timeout=300
    ) -> bool:
        # clean_current = self.driver.current_url.replace('https://', '').replace('www.', '').strip('/')
        # clean_new = url.replace('https://', '').replace('www.', '').strip('/')

        # if clean_current == clean_new:
        #     return False

        # https://stackoverflow.com/a/30121876/2292993
        # For implicit waits: 0 seconds. This means that if a selenium command does not find an element immediately, it reports immediately, rather than wait until an element is found.
        # For page loads: 300 seconds.
        # For script timeouts: 30 seconds.
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            self.driver.set_page_load_timeout(300)
            return f'Title: {self.driver.title}'
        except:
            self.driver.set_page_load_timeout(300)
            return False

    def getreq(self,url,regexpat,timeout=300,raw=False):
        """
        url: if '', will search visited urls 
        regexpat: The pat attribute will be matched within the request URL. pat a regular expression
        if timeout and/or no match, returns ''
        else returns 
            if not raw: request.url
            else request (so that can check request.headers, request.response.headers, request.response.status_code etc)
        """
        # https://pypi.org/project/selenium-wire/

        if url=='':
            # Access requests via the `requests` attribute
            # for request in driver.requests:
            # request.url, request.response.status_code, request.response.headers['Content-Type']
            for request in self.driver.iter_requests():
                if request.response:
                    if re.search(regexpat,request.url):
                        if not raw:
                            return request.url
                        else:
                            return request
            return ''

        # delete previous requests to get fresh results
        del self.driver.requests
        self.driver.get(url)
        # https://github.com/wkeeling/selenium-wire/blob/master/seleniumwire/storage.py#L272
        # https://github.com/wkeeling/selenium-wire/blob/master/seleniumwire/inspect.py#L51
        # Note that driver.wait_for_request() doesn't make a request, 
        # it just waits for a previous request made by some other action and 
        # it will return the first request it finds. 
        # Also note that since pat can be a regular expression, 
        # you must escape special characters such as question marks with a slash. 
        # A TimeoutException is raised if no match is found within the timeout period.
        try:
            request = self.driver.wait_for_request(regexpat,timeout)
            if not raw:
                return request.url
            else:
                return request
        except TimeoutException: 
            return ''

    def getresp(self,url:str,regexpat,timeout=300,raw=False,*args,**kwargs):
        """
        catch matched url, then request the url with headers, returns json (raw=False) or raw resp (raw=True)
        """
        import requests
        resp=self.getreq(url,regexpat,timeout=timeout,raw=True)
        resp=requests.get(resp.url,headers=resp.headers,*args,**kwargs)
        if not raw:
            return resp.json()
        else:
            return resp

    def refresh(self,seconds=5) -> None:
        self.driver.refresh()
        time.sleep(seconds)
        
    # https://selenium-python.readthedocs.io/navigating.html#filling-in-forms
    def findsel(self,*args,**kwargs):
        return Select(self.find(*args,**kwargs))

    def find(
        self,
        by: By,
        key: str,
        timeout: Optional[int] = None,
        element: Optional = None
    ) -> Union[Optional[WebElement], List[WebElement]]:
        return self.__find(
            by,
            EC.presence_of_element_located,
            key,
            element=element,
            timeout=timeout
        )

    # def find_by(
    #     self,
    #     type_: Optional[str] = None, #div, a, span, ...
    #     attributes: Optional[Dict[str, str]] = None,
    #     id_: Optional[str] = None,
    #     class_: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     in_element: Optional[WebElement] = None,
    #     **kwargs
    # ) -> Optional[WebElement]:
    #     return self.find(
    #         By.XPATH,
    #         self.generate_xpath(type_=type_, attributes=attributes, id_=id_, class_=class_, for_sub_element=in_element is not None, **kwargs),
    #         element=in_element,
    #         timeout=timeout
    #     )

    # # aliases
    # bsfind = find_by
    # find_ = find_by

    def reload_element(
        self,
        element,
        timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        return self.find(
            By.XPATH,
            key=element.get_xpath(),
            timeout=timeout
        )

    def find_all(
        self,
        by: By,
        key: str,
        timeout: Optional[int] = None,
        element: Optional = None
    ) -> List[WebElement]:
        return self.__find(
            by,
            EC.presence_of_all_elements_located,
            key,
            element=element,
            timeout=timeout
        )

    findall=find_all

    # def find_all_by(
    #     self,
    #     type_: Optional[str] = None, #div, a, span, ...
    #     attributes: Optional[Dict[str, str]] = None,
    #     id_: Optional[str] = None,
    #     class_: Optional[str] = None,
    #     timeout: Optional[int] = None,
    #     in_element: Optional[WebElement] = None,
    #     **kwargs
    # ) -> List[WebElement]:
    #     return self.find_all(
    #         By.XPATH,
    #         self.generate_xpath(type_=type_, attributes=attributes, id_=id_, class_=class_, for_sub_element=in_element is not None, **kwargs),
    #         element=in_element,
    #         timeout=timeout
    #     )

    # # aliases
    # bsfind_all = find_all_by
    # find_all_ = find_all_by

    def get_attribute(self, element, key: str) -> Optional[str]:
        try:
            return element.get_attribute(key)
        except:
            return None

    def get_attributes(self, element) -> Optional[Dict[str, str]]:
        try:
            return json.loads(
                self.driver.execute_script(
                    'var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return JSON.stringify(items);',
                    element
                )
            )
        except:
            return None

    def save_cookies(self, cookies: Optional[List[Dict]] = None) -> None:
        cookies_path = self.__cookies_path()

        try:
            os.remove(cookies_path)
        except:
            pass

        json.dump(
            cookies or self.driver.get_cookies(),
            open(self.__cookies_path(), 'w')
        )

    def load_cookies(self,verbose=False) -> None:
        if not self.has_cookies_for_current_website():
            self.save_cookies()

            return

        cookies = json.load(open(self.__cookies_path(), 'r'))
        should_save = False
        cookies_to_save = []

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
                cookies_to_save.append(cookie)
            except Exception as e:
                should_save = True
                if verbose:
                    print('Error while loading cookie:', e)
                    print(json.dumps(cookie, indent=4))
        
        if should_save:
            self.save_cookies(cookies_to_save)

    def has_cookies_for_current_website(self, create_folder_if_not_exists: bool = True) -> bool:
        return os.path.exists(
            self.__cookies_path(
                create_folder_if_not_exists=create_folder_if_not_exists
            )
        )

    def send_keys_delay_random(
        self,
        element: object,
        keys: str,
        min_delay: float = 0.025,
        max_delay: float = 0.25
    ) -> None:
        import random

        for key in keys:
            element.send_keys(key)
            time.sleep(random.uniform(min_delay,max_delay))

    def scroll(self, amount: int) -> None:
        self.scroll_to(self.current_page_offset_y()+amount)
    
    def scroll_to(self, position: int) -> None:
        try:
            self.driver.execute_script('window.scrollTo(0,'+str(position)+');')
        except:
            pass

    def scroll_to_element(self, element, header_element=None):
        try:
            header_h = 0

            if header_element is not None:
                _, _, _, header_h, _, _ = self.get_element_coordinates(header_element)

            _, element_y, _, _, _, _ = self.get_element_coordinates(element)

            self.scroll_to(element_y-header_h)
        except Exception as e:
            print('scroll_to_element', e)
    
    def move_to_element(self, element: Optional[WebElement]) -> bool:
        if not element:
            print('move_to_element: None element passed')
            return False
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            return True
        except Exception as e:
            print('move_to_element', e)
            return False

    def switch_to_default(self):
        # default is the first frame (frame 0)?
        self.driver.switch_to.default_content()
        return True

    def switch_to_frame(self, iframe: Optional[WebElement]) -> bool:
        if not iframe:
            print('switch_to_frame: None frame passed')
            return False
        try:
            self.driver.switch_to.default_content()
            time.sleep(1)
            self.driver.switch_to.frame(iframe)
            return True
        except Exception as e:
            print('switch_to_frame', e)
            return False

    def frames(self):
        self.driver.switch_to.default_content()
        time.sleep(1)
        n = self.driver.execute_script('return window.length')
        res = []
        for i in range(0,n):
            self.driver.switch_to.default_content()
            time.sleep(1)
            self.driver.switch_to.frame(i)
            name = self.driver.execute_script('return window.name')
            res.append({'i':i,'name':name})
        self.driver.switch_to.default_content()
        return res

    def find_frame(self,by,key,*args,**kwargs):
        # first frame is 0
        self.driver.switch_to.default_content()
        time.sleep(1)
        n = self.driver.execute_script('return window.length')
        for i in range(0,n):
            self.driver.switch_to.default_content()
            time.sleep(1)
            self.driver.switch_to.frame(i)
            if self.find(by,key,*args,**kwargs) is not None:
                name = self.driver.execute_script('return window.name')
                self.driver.switch_to.default_content()
                return({'i':i,'name':name})
        self.driver.switch_to.default_content()
        return False

    # returns x, y, w, h, max_x, max_y
    def get_element_coordinates(self, element) -> Tuple[int, int, int, int, int, int]:
        location = element.location
        size = element.size

        x = location['x']
        y = location['y']
        w = size['width']
        h = size['height']

        return x, y, w, h, x+w, y+h

    def current_page_offset_y(self) -> float:
        return self.driver.execute_script('return window.pageYOffset;')

    def open_new_tab(self, url: str) -> None:
        if url is None:
            url = ''

        cmd = 'window.open("'+url+'","_blank");'
        self.driver.execute_script(cmd)
        self.driver.switch_to.window(self.driver.window_handles[-1])
    
    @staticmethod
    def generate_xpath(
        type_: Optional[str] = None, #div, a, span, ...
        attributes: Optional[Dict[str, str]] = None,
        id_: Optional[str] = None,
        class_: Optional[str] = None,
        for_sub_element: bool = False, # selenium has a bug with xpath. If xpath does not start with '.' it will search in the whole doc
        **kwargs
    ) -> str:
        attributes = attributes or {}

        if class_ is not None:
            attributes['class'] = class_

        if id_ is not None:
            attributes['id'] = id_

        attributes.update({k:(v if type(v) == str else json.dumps(v)) for k, v in kwargs.items()})
        type_ = type_ or '*'
        xpath_query = ''

        for key, value in attributes.items():
            if len(xpath_query) > 0:
                xpath_query += ' and '

            xpath_query += '@' + key + '=\'' + value + '\''

        return ('.' if for_sub_element else '') + '//' + type_ + (('[' + xpath_query + ']') if len(xpath_query) > 0 else '')


    # JS
    def js_click(self, element: WebElement) -> bool:
        return self.execute_script_on_element('arguments[0].click();', element)
    click=js_click

    # https://www.tutorialspoint.com/how-to-perform-right-click-on-an-element-in-selenium-with-python
    # not really js powered
    def js_rightclick(self, element: WebElement) -> bool:
        action = ActionChains(self.driver)
        return action.context_click(element).perform()
    rclick=js_rightclick

    # click for n times or until not clickable, whichever comes first
    def js_clicks(self, element: WebElement, n=100) -> bool:
        i = 1
        while i<=n:
            try:
                # do not call driver.execute_script(), because it will not trigger error
                # call element.click(), will trigger error is no longer clickable?
                element.click()
                time.sleep(0.5)
            except:
                break
            i += 1
    clicks=js_clicks

    # essentially send keys
    def js_setvalue_via_typing(self, element: WebElement, value) -> bool:
        is_mac=platform.system()=='Darwin'
        if is_mac: 
            element.send_keys(KEYS.COMMAND,"a")
        else:
            element.send_keys(KEYS.CONTROL,"a")
        time.sleep(0.5)
        element.send_keys(value)
    send_keys=js_setvalue_via_typing
    send=js_setvalue_via_typing

    # for D2L, this methods would not save value!
    def js_setvalue(self, element: WebElement, value) -> bool:
        return self.execute_script_on_element(f'arguments[0].value="{value}";', element)

    def js_scroll_into_view(self, element: WebElement) -> bool:
        return self.execute_script_on_element('arguments[0].scrollIntoView();', element)

    def execute_script_on_element(self, script: str, element: WebElement) -> bool:
        caller_name = inspect.stack()[2][3]

        if not element:
            print('{}: passed element is None'.format(caller_name))

            return False

        return self.execute_script(script, element)

    def execute_script(self, script: str, element: Optional[WebElement] = None) -> bool:
        try:
            return self.driver.execute_script(script, element) if element else self.driver.execute_script(script)

            # return True
        except Exception as e:
            print('{}: {} - {}'.format(inspect.stack()[2][3], script, e))

            return False

    def print(self,filepath=None):
        if filepath is None: filepath = self.driver.title2

        def _cleanpath(path,allow_unicode=False):
            import unicodedata, urllib.parse
            from ez import splitpath, joinpath

            [pth, fname, ext] = splitpath(path)
            fname = urllib.parse.unquote_plus(fname)

            if allow_unicode:
                fname = unicodedata.normalize('NFKC', fname)
            else:
                fname = unicodedata.normalize('NFKD', fname).encode('ascii', 'ignore').decode('ascii')
            
            # (?u) switch on unicode
            fname = re.sub(r'(?u)[^\w.\s-]', '', fname)
            expression = '(?<=[(%s)])(%s)*|^(%s)+|(%s)+$' % ('\s|_|\-','\s|_|\-','\s|_|\-','\s|_|\-')
            fname = re.sub(expression, "", fname, count=0)
            if fname in {'', '.', '..'}:
                raise Exception(f"Could not clean path '{path}'")
            path = joinpath(pth,fname+ext)
            return path
        filepath = _cleanpath(filepath)

        # https://gist.github.com/lrhache/7686903
        main_window= self.driver.current_window_handle
        #Open a new tab in blank
        self.driver.execute_script("window.open(''),'_blank'")
        # Switch to the new window
        self.driver.switch_to.window(self.driver.window_handles[1])

        # https://stackoverflow.com/a/64987078/2292993
        # Get about:config
        self.driver.get('about:config')
        time.sleep(1)
        # Define Configurations        
        script = """
        var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefBranch);
        prefs.setBoolPref('print.always_print_silent', true);
        prefs.setBoolPref('print.show_print_progress', false)
        prefs.setCharPref('print.print_headerright', '')
        prefs.setCharPref('print.print_headercenter', '')
        prefs.setCharPref('print.print_headerleft', '')
        prefs.setCharPref('print.print_footerright', '')
        prefs.setCharPref('print.print_footercenter', '')
        prefs.setCharPref('print.print_footerleft', '')
        prefs.setCharPref('print_printer', 'Print to File');
        prefs.setBoolPref('print.printer_Print_to_File.print_to_file', true);
        prefs.setCharPref('print.printer_Print_to_File.print_to_filename', '{}');
        prefs.setBoolPref('print.printer_Print_to_File.show_print_progress', true);
        """.format(filepath)
        # Set Configurations
        self.driver.execute_script(script)
        time.sleep(1)

        #Close Current Tab
        self.driver.close()
        #Focus to the main window
        self.driver.switch_to.window(main_window)

        self.driver.execute_script("window.print();")

    # LEGACY
    def scroll_to_bottom(self) -> None:
        MAX_TRIES = 25
        SCROLL_PAUSE_TIME = 0.5
        SCROLL_STEP_PIXELS = 5000
        current_tries = 1

        while True:
            last_height = self.current_page_offset_y()
            self.scroll(last_height+SCROLL_STEP_PIXELS)
            time.sleep(SCROLL_PAUSE_TIME)
            current_height = self.current_page_offset_y()

            if last_height == current_height:
                current_tries += 1

                if current_tries == MAX_TRIES:
                    break
            else:
                current_tries = 1


    # --------------------------------------------------------- Destructor ----------------------------------------------------------- #

    def __del__(self):
        # no auto_close for keyboard maestro
        if self.auto_close: 
            try:
                # prevent double quit if already manually called quit
                if os.path.exists(self.driver.profile.path):
                    self.quit()
            except:
                pass


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    def __find(
        self,
        by: By,
        find_func: Callable,
        key: str,
        timeout: Optional[int] = None,
        element: Optional = None
    ) -> Union[Optional[WebElement], List[WebElement]]:
        timeout = timeout if timeout is not None else self.default_find_func_timeout

        # jerry: remap by
        bydict = {
            'class': By.CLASS_NAME,
            'linktext': By.LINK_TEXT,
            'partiallinktext': By.PARTIAL_LINK_TEXT,
            'css': By.CSS_SELECTOR,
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'tag': By.TAG_NAME,
            By.CLASS_NAME: By.CLASS_NAME,
            By.LINK_TEXT: By.LINK_TEXT,
            By.PARTIAL_LINK_TEXT: By.PARTIAL_LINK_TEXT,
            By.CSS_SELECTOR: By.CSS_SELECTOR,
            By.ID: By.ID,
            By.NAME: By.NAME,
            By.XPATH: By.XPATH,
            By.TAG_NAME: By.TAG_NAME,
        }
        by=bydict[by]
        key = key.strip()
        if by == By.CLASS_NAME:
            # if space in class name, convert to . Jerry
            key = key.replace(" ",".")
        if element is None:
            element = self.driver
        elif by == By.XPATH and not key.startswith('.'):
            # selenium has a bug with xpath. If xpath does not start with '.', it will search in the whole doc
            if key.startswith('('): 
                # (//input[@type="RADIO"])[2]
                key = '(.' + key[1:]
            else:
                key = '.' + key

        try:
            es = WebDriverWait(element, timeout).until(
                find_func((by, key))
            )
            # jerry: alias enhanced
            # https://stackoverflow.com/a/54662690/2292993
            from functools import partial
            def _send(
                self,
                keys: str,
                delay=[0.025,0.25],
                n=None
            ) -> None:
                # keys could only be single str with many chars
                # delay in seconds after each key press, 0, [0.025,0.25] <-random between
                import random
                if type(delay) not in [tuple,list]: delay=[delay,delay]
                for key in keys:
                    self.send_keys(key)
                    time.sleep(random.uniform(delay[0],delay[1]))
            def _sendsubmit(self,*value,n=None):
                # send keys and then submit
                self.send(*value)
                time.sleep(0.5)
                self.submit()
            def _getarea(self):
                # https://stackoverflow.com/a/59347207/2292993
                # Assume there is equal amount of browser chrome on the left and right sides of the screen.
                canvas_x_offset = self.parent.execute_script("return window.screenX + (window.outerWidth - window.innerWidth) / 2 - window.scrollX;")
                # Assume all the browser chrome is on the top of the screen and none on the bottom.
                canvas_y_offset = self.parent.execute_script("return window.screenY + (window.outerHeight - window.innerHeight) - window.scrollY;")
                # Get the element center.
                element_area = (self.rect["x"] + canvas_x_offset,
                                self.rect["y"] + canvas_y_offset,
                                self.rect["width"],
                                self.rect["height"])
                return element_area
            def _moveclick(self,radius=5,n=2,wait=0.25,*args,**kwargs):
                """
                n could be 0; 2 in case the first click only gets the focus
                """
                # # self is the element, self.parent is driver
                # actions = ActionChains(self.parent)
                # actions.move_to_element(self).click().perform()
                import ez
                ez.moveclick(self.getarea(), radius, n, wait, *args, **kwargs)
            def _movesend(self,keys,delay=[0.025,0.25],radius=5,n=2,wait=0.25):
                self.moveclick(radius,n,wait)
                import time
                time.sleep(wait)
                self.send(keys,delay)
            # es.send=es.send_keys
            # finall
            if find_func is EC.presence_of_all_elements_located: 
                for e in es:
                    e.send=partial(_send, e)
                    e.sendsubmit=partial(_sendsubmit, e)
                    e.getarea=partial(_getarea, e)
                    e.moveclick=partial(_moveclick, e)
                    e.movesend=partial(_movesend, e)
            else:
                es.send=partial(_send, es)
                es.sendsubmit=partial(_sendsubmit, es)
                es.getarea=partial(_getarea, es)
                es.moveclick=partial(_moveclick, es)
                es.movesend=partial(_movesend, es)
            return es
        except:
            return None

    def __random_firefox_user_agent(self, min_version: float = 60.0) -> str:
        while True:
            agent = UserAgent().firefox

            try:
                version_str_comps = agent.split('/')[-1].strip().split('.', 1)
                version = float(version_str_comps[0] + '.' + version_str_comps[1].replace('.', ''))

                if version >= min_version:
                    return agent
            except:
                pass

    def __cookies_path(self, create_folder_if_not_exists: bool = True) -> str:
        url_comps = tldextract.extract(self.driver.current_url)
        formatted_url = url_comps.domain + '.' + url_comps.suffix

        return os.path.join(
            self.cookies_folder_path,
            formatted_url + '.json'
        )

# ---------------------------------------------------------------------------------------------------------------------------------------- #