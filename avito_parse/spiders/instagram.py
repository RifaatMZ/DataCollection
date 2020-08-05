import re
from copy import deepcopy
import json
import scrapy
from scrapy.loader import ItemLoader
from avito_parse.items import InstgramParsFeed


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']     # needs to add s to http because of the login page
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __api_url = '/graphql/query/'
    __api_query = {
        'post_feed': '7437567ae0de0773fd96545592359a6b'    # query_hash for each feed is unique
    }
    variables = {"id": None, "first": 12}     # Just a draft to copy

    def __init__(self, login: str, passwd: str, parse_users: list, *args, **kwargs):
        self.parse_users = parse_users
        self.login = login
        self.passwd = passwd
        super().__init__(*args, **kwargs)
        print(1)

    def parse(self, response):
        token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.__login_url,
            method='POST',
            callback=self.im_login,
            formdata={
                'username': self.login,
                'enc_password': self.passwd
            },
            headers={'X-CSRFToken': token}
        )

    def im_login(self, response):
        data = response.json()
        if data['authenticated']:
            for user_name in self.parse_users:
                yield response.follow(f'/{user_name}',
                                      callback=self.user_parse,
                                      cb_kwargs={'user_name': user_name})    # adds user_name to func user_parse

    def user_parse(self, response, user_name):
        user_id = self.fetch_user_id(response, user_name)
        variables = deepcopy(self.variables)    # deepcopy as insurance to not change variables for user x
        variables["id"] = f'{user_id}'
        url = f"{self.__api_url}?query_hash={self.__api_query['post_feed']}&variables={json.dumps(variables,separators=(',', ':'))}"
        yield response.follow(url,
                              callback=self.user_feed_parse,
                              cb_kwargs={"user_name": user_name,
                                         "variables": variables}
                              )

    def user_feed_parse(self, response, user_name, variables, i=0):
        item = ItemLoader(InstgramParsFeed(), response)
        data = response.json()
        page_info = data['data']['user']['edge_owner_to_timeline_media']
        item.add_value("user_name", page_info["edges"][i]["node"]["owner"]["username"])
        item.add_value("user_id", page_info["edges"][i]["node"]["owner"]["id"])
        item.add_value("like_count", page_info["edges"][i]["node"]["edge_media_preview_like"]["count"])
        item.add_value("photo_url", page_info["edges"][i]["node"]["display_url"])
        yield item.load_item()
        if page_info['page_info']['has_next_page']:

            variables["after"] = page_info['page_info']["end_cursor"]
            url = f"{self.__api_url}?query_hash={self.__api_query['post_feed']}&variables={json.dumps(variables, separators=(',', ':'))}"
            yield response.follow(url,
                                  callback=self.user_feed_parse,
                                  cb_kwargs={"user_name": user_name,
                                             "variables": variables,
                                             "i": i+1}
                                  )

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text.text).group()
        return json.loads(matched).get('id')

    def fetch_csrf_token(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')
