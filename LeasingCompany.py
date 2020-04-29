from time import sleep
from selenium import webdriver
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

chrome = webdriver.Chrome(ChromeDriverManager().install())
url = 'http://leasing.cbrc.gov.cn/topUserList.jhtml'
chrome.get(url)

input_ele = chrome.find_element_by_id('enterUser.name')
input_ele.send_keys("融资租赁")

submit_ele = chrome.find_element_by_class_name('btn_ccx')
submit_ele.click()
info_list = []
count = 0

while count <729:
    count += 1
    sleep(2)
    infos_per = chrome.find_element_by_class_name('dataListTable').find_element_by_tag_name(
        'tbody').find_elements_by_tag_name('tr')
    infos_per = infos_per[:-2]

    for i in infos_per:
        info_dict = {}
        origin_info_ele = i.find_elements_by_tag_name("td")

        info_dict['name'] = origin_info_ele[1].text
        info_dict['location'] = origin_info_ele[2].text
        info_dict['type'] = origin_info_ele[3].text
        info_dict['code'] = origin_info_ele[4].text

        info_list.append(info_dict)

    next_ele = chrome.find_element_by_xpath('//*[@id="userForm"]/table[2]/tbody/tr[16]/td/table/tbody/tr/td[9]/a')
    next_ele.click()

    if count % 50 == 0:
        print("Scraped", count, "pages.")


all_info = pd.DataFrame.from_dict(info_list)
all_info.to_csv("LeasingInfo2.csv", index=False)

chrome.close()