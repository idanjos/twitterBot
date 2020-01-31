#region imports
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
#endregion

# States:
# 0: Instantiation 
# 1: Home
# 2: Scraping, discontinued
# 3: Article viewpoint
# 4: Profile viewpoint
# 5: Search viewpoint
class Twitter():
    def __init__(self,user,passwd,timeout = 10,debug=False):
        self.__state = 0
       
        self.__timeout = timeout
        self.__following = set()
        self.__tweets = []
        self.__feed = set()
        self.__sleep = 3          # Time in seconds between each action

        locale='en-us'
        options = Options()
        options.headless = True
        if debug:
            options.headless = False
        
        profile = webdriver.FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        
        profile.accept_untrusted_certs = True
        profile.set_preference("intl.accept_languages", locale)
        profile.update_preferences()
        self.__driver = webdriver.Firefox(executable_path="./drivers/geckodriver.exe", firefox_profile=profile, options=options)
        self.__home = "https://twitter.com/home"
        url = "https://twitter.com/login"
        self.__driver.get(url)
      
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//input[@name='session[password]']")))
        clearFixes = self.__driver.find_elements_by_xpath("//div[@class='clearfix field']")
      
        if len(clearFixes) > 0:
            print("Clear fix problem")
            #ActionChains(self.__driver).send_keys(user).send_keys(Keys.TAB).send_keys(passwd).send_keys(Keys.ENTER).perform()
            username = self.__driver.find_element_by_class_name("js-username-field")
            password = self.__driver.find_element_by_xpath("//input[@class='js-password-field']")
            username.send_keys(user)
            password.send_keys(passwd)
            password.send_keys(Keys.ENTER)
            
        else:
            username = self.__driver.find_element_by_name("session[username_or_email]")
            password = self.__driver.find_element_by_name("session[password]")
            username.send_keys(user)
            password.send_keys(passwd)
            password.send_keys(Keys.ENTER)
        
        
       
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//time")))
        print(user+" logged in successfully")
        self.__updateState()

    #region States Region 
    def __resetState(self):
        time.sleep(self.__sleep)
        self.__driver.get(self.__home)
        self.__updateState()

    def __updateState(self):
        #if len(self.__driver.find_elements_by_xpath("//div[@class='DraftEditor-root']")) > 0:
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//div[@class='DraftEditor-root']")))
        self.__state = 1
    #endregion

    #region Browser operations Region
    def dispose(self):
        self.__driver.quit()
    #endregion

    #region Open pages Region 
    def __openProfile(self,url):
        self.__openURL(url)
        self.__state = 4

    def __openSearch(self,url):
        self.__openURL(url)
        self.__state = 5

    def __openArticle(self, url):
        self.__openURL(url)
        self.__state = 3

    def __openURL(self, url): 
        self.__driver.get(url)
        WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//article")))
        
        print("Open: "+url)
        time.sleep(self.__sleep)
    #endregion

    #region Get Browser Attributes Region 
    def getPageSource(self):
        return self.__driver.page_source
    
    def getCurrentURL(self):
        return self.__driver.current_url
    #endregion

    #region Feed/Articles related Region 
    def getUserFeed(self,url):
        self.__openProfile(url)
        return self.getFeed()

    def getSearchFeed(self,string):
        self.__openSearch("https://twitter.com/search?q="+string)
        return self.getFeed()

    def getFeed(self):
        output = []
        while(len(output)< 1):
            if self.__state == 1 or self.__state == 4 or self.__state == 5:
                soup = BeautifulSoup(self.getPageSource(),"html.parser")
                #soup.find('time').find_parent
                for article in soup.find_all('article'):

                    #The following articles are still loading or broken
                    if article.find('time') == None:
                        break
                    output += [article.find('time').find_parent('a')['href']]
                    self.__feed.add(article.find('time').find_parent('a')['href'])
                    print("https://twitter.com"+article.find('time').find_parent('a')['href'])
                    
                    print("-------------------")
        return output
    #endregion

    #region Article Actions Region
    def likeArticle(self,url):
        self.__openArticle(url)
        if self.__state == 3:
            if len(self.__driver.find_elements_by_xpath("//div[@aria-label='Liked']")) > 0:
                print("Already liked!")
                self.__resetState()
                return
            reply = self.__driver.find_element_by_xpath("//div[@aria-label='Like']")
            try:
                reply.click()
            except:
                time.sleep(self.__sleep)
                self.__driver.execute_script("window.scrollTo(0, document.getElementsByTagName('article')[0].scrollHeight/2);")
                reply.click()            
            
            WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Liked']")))
            print("Liked!")
        self.__resetState()

    def retweetArticle(self,url):
        self.__openArticle(url)
        if self.__state == 3:
            if len(self.__driver.find_elements_by_xpath("//div[@aria-label='Retweeted']")) > 0:
                print("Already retweeted!")
                self.__resetState()
                return
            
            reply = self.__driver.find_element_by_xpath("//div[@aria-label='Retweet']")
            try:
                reply.click()
            except:
                time.sleep(self.__sleep)
                self.__driver.execute_script("window.scrollTo(0, document.getElementsByTagName('article')[0].scrollHeight/2);")
                reply.click()           
            ActionChains(self.__driver).send_keys(Keys.ENTER).perform()
            WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Retweeted']")))
            print("Retweeted!")
        self.__resetState()

    def commentArticle(self, url ,string):
        self.__openArticle(url)
        if self.__state == 3:
            reply = self.__driver.find_element_by_xpath("//div[@aria-label='Reply']")
            try:
                reply.click()
            except:
                time.sleep(self.__sleep)
                self.__driver.execute_script("window.scrollTo(0, document.getElementsByTagName('article')[0].scrollHeight/2);")
                reply.click()
            WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetButton']")))
            tweetButton = self.__driver.find_element_by_xpath("//div[@data-testid='tweetButton']")
            ActionChains(self.__driver).send_keys(string).perform()
            tweetButton.click()
            print("Commented!")
        self.__resetState()
    #endregion

    #region User Action Region 
    def followUser(self,url):
        if url in self.__following:
            print("Already Following!")
            return
        self.__openProfile(url)
        if self.__state == 4:
    
            WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='placementTracking']")))
            follow = self.__driver.find_element_by_xpath("//div[@data-testid='placementTracking']")
            follow.click()           
            #WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Turn on Tweet notifications']")))
            print("Followed User!")
            self.__following.add(url)
        self.__resetState()

    def publishTweet(self, string):
        if self.__state == 1:
            self.__state = 2
            tweetTextBox = self.__driver.find_element_by_xpath("//div[@class='DraftEditor-root']")
            tweetTextBox.click()

            time.sleep(1)
            ActionChains(self.__driver).send_keys(string).perform()
            tweetButton = self.__driver.find_element_by_xpath("//div[@data-testid='tweetButtonInline']")
            tweetButton.click()
            print("Tweeted")        
        else:
            self.__driver.get(self.__home)
            WebDriverWait(self.__driver, self.__timeout).until(EC.presence_of_element_located((By.XPATH, "//time")))
            self.__updateState()
            self.publishTweet(string)
        self.__resetState()

    #endregion
    # Testing development <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 
if __name__== "__main__":
    user = "email"
    passwd = "pass"
    t = Twitter(user,passwd,debug=True)
    t.getUserFeed("https://twitter.com/realdonaldtrump")
    t.getSearchFeed("Ok Bruh")
    input("Enter any Key to finish!")
    t.dispose()