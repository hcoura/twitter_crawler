import csv
import lxml.html as parser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

TWEETS_XPATH = "//li[@data-item-type='tweet']"
BASE_URL = "https://twitter.com/search?f=tweets&vertical=default&q="


def new_tweets(driver, min_len):
    return len(driver.find_elements_by_xpath(TWEETS_XPATH)) > min_len


class TwitterCrawler(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.items = []

    def save_items(self):
        keys = self.items[0].keys()
        with open("items.csv", 'w') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.items)

    def crawl_list_and_save(self, search_list):
        self.crawl_list(search_list)
        self.save_items()

    def crawl_list(self, search_list):
        items = []
        for term in search_list:
            url = BASE_URL + term
            tweets = self.crawl_url(url)
            image_name = term + ".png"
            self.screenshot(image_name)
            items.append({
                "term": term,
                "tweets": tweets,
                "image": image_name
            })
        self.items = items

    def crawl_url(self, url):
        self.driver.get(url)
        self.get_tweets(100)
        return self.parse_tweets()

    def get_tweets(self, num_of_tweets):
        self.driver_go_to_bottom()
        tweets = self.driver.find_elements_by_xpath(TWEETS_XPATH)
        while len(tweets) < num_of_tweets:
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: new_tweets(driver, len(tweets)))
            except TimeoutException:
                # simple exception handling, just move on in case of Timeout
                tweets = self.driver.find_elements_by_xpath(TWEETS_XPATH)
                break
            tweets = self.driver.find_elements_by_xpath(TWEETS_XPATH)
        return tweets

    def screenshot(self, image_name):
        self.driver_go_to_top()
        self.driver.save_screenshot(image_name)

    def driver_go_to_bottom(self):
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    def driver_go_to_top(self):
        self.driver.execute_script(
            "window.scrollTo(0, 0);")

    def parse_tweets(self):
        html = parser.fromstring(self.driver.page_source)
        tweets = html.xpath(TWEETS_XPATH)
        extracted_tweets = []
        for tweet in tweets:
            try:
                fullname = tweet.xpath(
                    ".//*[contains(@class, 'fullname')]/text()")[0]
            except IndexError:
                fullname = "Not Available"
            username = "".join(tweet.xpath(
                ".//*[contains(@class, 'username')]/descendant-or-self::*"
                "/text()"))
            tweet = "".join(tweet.xpath(
                ".//*[contains(@class, 'js-tweet-text-container')]"
                "/descendant-or-self::*[not(self::*[contains(@class,"
                " 'tco-ellipsis')])]/text()"
            )).strip()
            extracted_tweets.append({
                "fullname": fullname,
                "username": username,
                "tweet": tweet
            })
        return extracted_tweets


crawler = TwitterCrawler()
crawler.crawl_list_and_save(["javascript", "python", "scraping"])
