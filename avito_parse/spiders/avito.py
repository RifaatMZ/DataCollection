import scrapy
from pymongo import MongoClient


class AvitoSpider(scrapy.Spider):

    client = MongoClient('localhost:27017')
    data_base = client['parse_avito']
    collection = data_base['posts']

    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/sochi/kvartiry']

    css_sel = {
        'pagination': 'div.pagination-pages a::attr("href")'
    }
    xpath_sel = {
        'post_urls': '//div[contains(@class, "snippet-list")]//h3[contains(@class, "snippet-title")]/a/@href'
    }
    post_template = {
        'title': '//h1[contains(@class, "title-info-title")]/span/child::text()',
        'post_url': '//meta[contains(@property, "og:url")]/@content',
        'price': '//span[contains(@class, "price-value-string")]/span[contains(@class, "js-item-price")]/child::text()',
        'post_type': '//span[contains(@itemprop, "itemListElement")][4]/a/@title'
    }
    xpath_post_info = {
        'post_info': '//ul[contains(@class, "item-params-list")]//text()'
    }

    def parse(self, response):
        pagination = response.css(self.css_sel['pagination'])
        for url in pagination:
            yield response.follow(url, callback=self.parse)

        for post_url in response.xpath(self.xpath_sel['post_urls']):
            yield response.follow(post_url, callback=self.post_parse)

    def post_parse(self, response):
        item = {}
        for key, value in self.post_template.items():
            item[key] = response.xpath(value).get()
        item['post_info'] = response.xpath(self.xpath_post_info['post_info']).extract()
        item['post_info'] = self.post_info_to_dic(item['post_info'])

        self.collection.insert_one(item)

    def post_info_to_dic(self, a_list):
        a_list = filter(lambda x: x != " ", a_list)
        a_list = filter(lambda x: x != "\n  ", a_list)
        a_list = list(a_list)

        dic = {}
        i = 0
        while i != len(a_list):
            item = a_list[i]
            item = item.replace(": ", "")
            dic[item] = a_list[i+1]
            i += 2
        return dic

