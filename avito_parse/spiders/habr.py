import scrapy
from pymongo import MongoClient
from scrapy.http import Response
from scrapy.loader import ItemLoader
from avito_parse.items import AvitoParseItem, AuthorParseItem


class HabrSpider(scrapy.Spider):
    client = MongoClient('localhost:27017')
    data_base = client['parse_habr']
    collection = data_base['posts']

    name = 'habr'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/all']

    css_sel = {
        'pagination': 'li.toggle-menu__item_pagination a::attr("href")',
        'post_urls': 'h2.post__title a::attr("href")'
    }
    xpath_sel = {}

    authors = {
        'author_url': '//a[contains(@class, "user-info__nickname")]//@href'
    }

    def parse(self, response: Response):
        for link in response.css(self.css_sel['pagination']):
            yield response.follow(link, callback=self.post_feed_pars)

    def post_feed_pars(self, response: Response):
        for link in response.css(self.css_sel['post_urls']):
            yield response.follow(link, callback=self.post_pars)

    def post_pars(self, response: Response):
        item = ItemLoader(AvitoParseItem(), response)
        item.add_css('title', 'h1.post__title span::text')
        item.add_css('images', 'div.post__body img::attr("src")')
        item.add_xpath('comments_count', '//span[contains(@class, "post-stats__comments-count")]//text()')
        item.add_xpath('author_name', '//div[contains(@class, "user-info__links")]//a/text()')
        item.add_xpath('author_url', '//a[contains(@class, "user-info__nickname")]//@href')
        item.add_value('post_url', response.url)
        yield item.load_item()
        # yield response.follow(response.xpath('//a[contains(@class, "user-info__nickname")]//@href'), callback=self.author_page_pars())


    # def author_page_pars(self, response):
    #     item = ItemLoader(AuthorParseItem, response)
    #     item.add_xpath('author_posts', '//div[contains(@class, "posts_list")')
        # author_info = response.xpath('')
        # nickname = response.xpath('')
        # contacts = response.xpath('')
        # yield {'author_post': author_posts}
        # print(1)
        # yield {'author_post': author_posts, 'author_info': author_info,
        #        'nickname': nickname, 'contacts': contacts}
        # print(author_posts)
        # yield item.load_item()
        # print(1)
