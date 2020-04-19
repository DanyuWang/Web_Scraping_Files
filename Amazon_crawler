from selenium import webdriver
import csv

GOOD_LIST = ['B01MUAGZ49', 'B00YD547Q6', 'B01B1VC13K', 'B00EI7DPOO']
HEADERS = ['helpful_votes', 'title', 'review_text', 'average_score', 'review_score', 'isBuy', 'comment', 'pic_num',
           'user_helpful', 'user_comment']


class GoodInfoCrawler():
    def __init__(self, good_name):
        self._good_name = good_name
        self._browser_main = webdriver.Chrome()
        self._browser_person = webdriver.Chrome()
        self._reviews_arr = []

    def get_main_page(self):
        for i in range(1, 11):
            url = 'https://www.amazon.com/product-reviews/' + self._good_name + '/ref=cm_cr_dp_d_show_all_btm' + str(
                i) + \
                  '?ie=UTF8&reviewerType=all_reviews&pageNumber=' + str(i)
            self._browser_main.get(url)

            reviews_html = self._browser_main.find_elements_by_xpath('//div[@class="a-section review"]')
            total_score = self._browser_main.find_elements_by_xpath('//span[@data-hook="rating-out-of-text"]')
            score = float(total_score[0].text.split(' ')[0])  # 平均评分，数据类型str

            for review in reviews_html:
                review_dic = {}
                temp_vote = review.find_elements_by_xpath('.//span[@data-hook="helpful-vote-statement"]')
                if len(temp_vote) > 0 and (temp_vote[0].text.split(' ')[0] != 'One'):
                    review_dic['helpful_votes'] = int(temp_vote[0].text.split(' ')[0].replace(',', ''))  # 因变量

                    review_dic['title'] = review.find_element_by_xpath('.//a[@data-hook="review-title"]').text
                    review_dic['review_text'] = review.find_element_by_xpath(
                        './/span[@data-hook="review-body"]').text.replace('\n', ' ')

                    review_dic['average_score'] = score
                    temp_score = review.find_element_by_xpath('.//a[@class="a-link-normal"]')
                    review_dic['review_score'] = float(temp_score.get_attribute('title').split(' ')[0])

                    temp_buy = review.find_elements_by_xpath('.//span[@data-hook="avp-badge"]')
                    if len(temp_buy) > 0:
                        review_dic['isBuy'] = 1
                    else:
                        review_dic['isBuy'] = 0

                    temp_comment = review.find_element_by_xpath('.//span[@class="a-size-base"]').text.split(' ')
                    if len(temp_comment) > 1:
                        review_dic['comment'] = int(temp_comment[0].replace('+', ''))
                    else:
                        review_dic['comment'] = 0

                    temp_user_pic = review.find_elements_by_xpath('.//img[@alt="review image"]')
                    review_dic['pic_num'] = len(temp_user_pic)

                    temp_user = review.find_element_by_xpath('.//a[@class="a-profile"]')
                    temp_user = temp_user.get_attribute('href')
                    review_dic = self.get_person_page(temp_user, review_dic)

                if len(review_dic) > 0:
                    self.reviews_arr.append(review_dic)

        self._browser_main.close()

        return self.reviews_arr

    def get_person_page(self, person_url, review_dic):
        self._browser_person.get(person_url)
        element = self._browser_person.find_elements_by_xpath('//span[@class="a-size-large a-color-base"]')
        if element.__len__() > 0:
            review_dic['user_helpful'] = int(element[0].text)
            review_dic['user_comment'] = int(element[1].text)
        self._browser_person.close()

        return review_dic

    def form_csv(self, reviews_arr):
        filename = self._good_name + '.csv'
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, HEADERS)
            writer.writeheader()

            for row in reviews_arr:
                writer.writerow(row)


def collect_goods_info():
    for good in GOOD_LIST:
        good_crawler = GoodInfoCrawler(good)
        good_info = good_crawler.get_main_page()
        good_crawler.form_csv(good_info)


if __name__ == '__main__':
    collect_goods_info()
