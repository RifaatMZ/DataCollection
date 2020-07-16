import json
import datetime as dt
import requests


class Catalog:
    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
        }

    def __init__(self, url, catg_url):
        self.__url = url
        self.__catg_url = catg_url
        self.__catalog = []
        self.__catg_name = ''
        response = requests.get(self.__catg_url, headers=self.headers)
        self.__categories = response.json()

    def parse(self, i):
        url = self.__url
        categories = self.__categories
        catg_code = categories[i]['parent_group_code']
        self.__catg_name = categories[i]['parent_group_name']
        params = {
                'records_per_page': 50,
                'categories': catg_code,
            }

        while url:
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            url = data['next']
            params = {}
            self.__catalog.extend(data['results'])

    def save_to_file(self):
        catg_name = self.__catg_name
        now = dt.datetime.now().strftime('%d-%m-%Y')
        with open(F'{now}_{catg_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(self.__catalog, file, ensure_ascii=False)

    def save_files(self):
        for i, j in enumerate(self.__categories):
            Catalog.parse(self, i)
            Catalog.save_to_file(self)
            self.__catalog = []


if __name__ == '__main__':
    catalog = Catalog('https://5ka.ru/api/v2/special_offers/', 'https://5ka.ru/api/v2/categories/')
    catalog.parse()
    print()




