import requests
from lxml import etree
import csv


class FlightCrawler:
    def __init__(self, data_type, max_order):  # arrival/departure
        self._search_type = data_type
        self._max = max_order
        self._dict_list = []

    def url_process(self, order):
        head = 'https://uk.flightaware.com/live/airport/ZHCC/'
        url = head + self._search_type+'s/all?;offset='+str(order)+';actual'+self._search_type+'time;sort=DESC'
        return url

    def page_content(self, url):
        web = requests.get(url).text
        tree = etree.HTML(web)
        temp = tree.xpath('//table[@class="prettyTable fullWidth"]//tr')

        for info in temp[2:len(temp)]:
            info_dict = dict()
            basic_info = info.findall('td//span//a')

            if len(basic_info) >= 3:
                info_dict['id'], info_dict['plane_type'], info_dict[self._search_type] = basic_info[0].text, basic_info[1].text, basic_info[2].text
            else:
                info_dict['id'], info_dict['plane_type'], info_dict[self._search_type] = basic_info[0].text, None, basic_info[1].text

            time = info.findall('td')
            if time[3].text is None:
                end = time[4].text.split(' ')
                info_dict['D_day'], info_dict['D_time'], info_dict['A_day'], info_dict['A_time'] = None, None, end[0], end[1]
                self._dict_list.append(info_dict)
                continue

            if time[4].text is None:
                start = time[3].text.split(' ')
                info_dict['D_day'], info_dict['D_time'], info_dict['A_day'], info_dict['A_time'] = start[0], start[1], None, None
                self._dict_list.append(info_dict)
                continue

            start, end = time[3].text.split(' '), time[4].text.split(' ')
            info_dict['D_day'], info_dict['D_time'], info_dict['A_day'], info_dict['A_time'] = start[0], start[1], end[0], end[1]

            self._dict_list.append(info_dict)

    def to_csv(self):
        order = 0
        while order <= self._max:
            url = self.url_process(order)
            self.page_content(url)
            print('finish order ', order)
            order += 20

        name = self._search_type + '.csv'

        keys = self._dict_list[0].keys()
        with open(name, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self._dict_list)


def init_crawler():
    fc_arrival = FlightCrawler('arrival', 3360)
    fc_arrival.to_csv()
    fc_depart = FlightCrawler('departure', 3380)
    fc_depart.to_csv()


if __name__ == '__main__':
    init_crawler()
