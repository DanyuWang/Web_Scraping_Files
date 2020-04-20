import requests
from time import sleep
from lxml import etree
from selenium import webdriver
import pandas as pd
import os

DATA_DIR = '/Users/holly/Desktop/毕设/Data'


class P2PEyeCrawler:
    def __init__(self, flag=1):
        self._headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                                       'like Gecko) fChrome/79.0.3945.130 Safari/537.36'}
        if flag == 0:
            self._chrome = webdriver.Chrome()
        self._datapath = DATA_DIR
        self._trading_info_dir = os.path.join(self._datapath, 'MonthlyTradingData')
        self._comments_dir = os.path.join(self._datapath, 'CommentsData')
        self._discussion_dir = os.path.join(self._datapath, 'DiscussionsData')
        self._dir_list = [self._datapath, self._trading_info_dir, self._comments_dir, self._discussion_dir]

    def create_csv(self, dir_choice, filename, data):
        data.to_csv(os.path.join(self._dir_list[dir_choice], filename + '.csv'), index=False)

        print("Saved", filename + '.csv', "successfully.")
        return 0

    def scrape_trading_info(self):
        url = 'https://www.p2peye.com/shuju/ptsj/'
        self._chrome.get(url)

        choices = self._chrome.find_elements_by_xpath('//div[@class="lis"]')
        for i in range(1, len(choices)):
            self._chrome.find_element_by_class_name('select').click()
            sleep(2)
            choices[i].click()
            dict_list = []

            sleep(5)
            date = self._chrome.find_element_by_xpath('//p[@class="hdl"]').text
            all_platforms = self._chrome.find_elements_by_xpath('//tr[@class="bd"]')
            for platform in all_platforms:
                info_dict = {}
                info_dict['name'] = platform.find_elements_by_tag_name('a')[0].get_attribute('title')
                info_dict['ref'] = platform.find_elements_by_tag_name('a')[0].get_attribute('href')
                info_dict['total left'] = platform.find_element_by_xpath('.//td[@class="total left"]').text
                info_dict['rate left'] = platform.find_element_by_xpath('.//td[@class="rate left"]').text
                info_dict['pnum left'] = platform.find_element_by_xpath('.//td[@class="pnum left"]').text
                info_dict['cycle left'] = platform.find_element_by_xpath('.//td[@class="cycle left"]').text
                info_dict['p1num left'] = platform.find_element_by_xpath('.//td[@class="p1num left"]').text
                info_dict['fuload left'] = platform.find_element_by_xpath('.//td[@class="fuload left"]').text
                info_dict['alltotal left'] = platform.find_element_by_xpath('.//td[@class="alltotal left"]').text
                print(date, info_dict['name'])

                dict_list.append(info_dict)
            monthly_trading = pd.DataFrame.from_dict(dict_list)
            self.create_csv(1, date, monthly_trading)

        self._chrome.close()
        return 0

    def basic_info_dict(self):
        df = pd.read_csv(os.path.join('/Users/holly/Desktop/Avicii', 'name&ref.csv'))

        return df.to_dict('records')

    def scrape_single_comments(self, page_url):
        comment_web = requests.get(page_url, headers=self._headers).text
        comment_tree = etree.HTML(comment_web)
        temp = comment_tree.xpath('//div[@class="c-page"]')[0].xpath('.//a')
        if len(temp) > 0:
            max_page = int(temp[-2].text)
        else:
            max_page = 1

        platform_all_comments = []
        count = 0
        for i in range(max_page):
            i_url = page_url + 'list-0-0-' + str(i + 1) + '.html'
            i_web = requests.get(i_url, headers=self._headers).text
            i_tree = etree.HTML(i_web)
            comments_list = i_tree.xpath('//div[@class="floor"]')

            for comment in comments_list:
                comment_dict = {}
                comment_dict['user_name'] = comment.xpath('.//a[@class="qt-gl username"]')[0].text
                comment_dict['user_page'] = comment.xpath('.//a[@class="qt-gl username"]')[0].get('href')
                comment_dict['user_pid'] = comment_dict['user_page'].split('/')[-2][1:]
                if len(comment.xpath('.//div[@class="info clearfix"]')[0].xpath('.//div')) > 0:
                    comment_dict['major_tag'] = comment.xpath('.//div[@class="info clearfix"]')[0].xpath('.//div')[
                        0].text
                tags_list = comment.xpath('.//li[@class="qt-gl"]')
                if len(tags_list) > 0:
                    tags = []
                    for j in range(len(tags_list)):
                        tags.append(comment.xpath('.//li[@class="qt-gl"]')[j].text)
                        tags.append(', ')

                    tags = ''.join(tags[:-1])
                    comment_dict['minor_tags'] = tags

                comment_dict['text'] = comment.xpath('.//a[@target="_blank"]')[1].text
                comment_dict['time'] = comment.xpath('.//div[@class="qt-gl time"]')[0].text

                comment_dict['num_like'] = comment.xpath('.//i')[0].text
                comment_dict['num_comments'] = comment.xpath('.//i')[1].text
                count += 1

                platform_all_comments.append(comment_dict)
            if count % 1000 == 0:
                print("Comment number & Page:", count, i)
        df_single_platforms = pd.DataFrame.from_dict(platform_all_comments)

        return df_single_platforms

    def scrape_all_comments(self):
        info_dict = self.basic_info_dict()
        for d in info_dict:
            name = d['name']
            if os.path.exists(os.path.join(self._comments_dir, name+'.csv')):
                continue
            url = d['ref'][:-6] + 'comment/'
            print("Started", name)
            df_cmt = self.scrape_single_comments(url)
            self.create_csv(2, name, df_cmt)
            print("Finished", name)

        return 0

    def scrape_specific_comment(self, url):
        c_tree = etree.HTML(requests.get(url, headers=self._headers).text)
        if c_tree is None:
            return None
        element = c_tree.xpath('//div[@class="ui-article-bd"]')
        if len(element) == 0:
            return None
        element = element[0].xpath('.//td[@class="t_f"]')
        if len(element) == 0:
            return None
        temp_text = ''.join(element[0].itertext())
        temp_text = temp_text.strip()
        temp_text = temp_text.replace('\n', '')
        temp_text = temp_text.replace('\r', '')

        return temp_text

    def scrape_single_discussions(self, page_url):
        discussion_web = requests.get(page_url, headers=crawler._headers).text
        discussion_tree = etree.HTML(discussion_web)
        max_page = int(discussion_tree.xpath('//div[@class="c-page"]')[0].get('pn'))
        platform_all_discussions = []
        count = 0

        for i in range(max_page):
            i_url = page_url + 'p' + str(i + 1)
            i_web = requests.get(i_url, headers=self._headers).text
            i_tree = etree.HTML(i_web)

            all_discussions = i_tree.xpath('//div[@class="mod-list"]')[0].xpath('.//li[@class="item clearfix"]')
            for di in all_discussions:
                discuss_dict = {}
                a_elements = di.xpath('.//a')
                discuss_dict['block'] = a_elements[0].get('title')
                discuss_dict['title'] = a_elements[1].get('title')
                discuss_dict['ref'] = 'http:' + di.xpath('.//a')[1].get('href')
                discuss_dict['text'] = self.scrape_specific_comment(discuss_dict['ref'])
                discuss_dict['time'] = di.xpath('.//span[@class="mc-ft-l"]')[0].text
                discuss_dict['source'] = di.xpath('.//span[@class="mc-ft-c"]')[0].text
                discuss_dict['comment_num'] = ''.join(di.xpath('.//span[@class="ft-comment"]')[0].itertext())
                discuss_dict['view_num'] = ''.join(di.xpath('.//span[@class="ft-see"]')[0].itertext())

                count += 1
                platform_all_discussions.append(discuss_dict)

            if count % 1000 == 0:
                print("Discussion number & Page:", count, i)

        df_single_platforms = pd.DataFrame.from_dict(platform_all_discussions)

        return df_single_platforms

    def scrape_all_discussions(self):
        info_dict = self.basic_info_dict()
        for d in info_dict:
            name = d['name']
            if os.path.exists(os.path.join(self._discussion_dir, name+'.csv')):
                continue
            url = d['ref'][:-6] + 'forum/'
            print("Started", name)
            df_cmt = self.scrape_single_discussions(url)
            self.create_csv(3, name, df_cmt)
            print("Finished", name)

        return 0


if __name__ == '__main__':
    crawler = P2PEyeCrawler(1)
    crawler.scrape_all_discussions()