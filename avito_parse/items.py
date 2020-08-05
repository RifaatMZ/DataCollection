# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def clean_author_url(values):
    return f'https://habr.com/ru{values}'


def clean_photos(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


class AvitoParseItem(scrapy.Item):
    name = 'Harb_Posts'
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field()
    comments_count = scrapy.Field(output_processor=TakeFirst())
    author_name = scrapy.Field(output_processor=TakeFirst())
    author_url = scrapy.Field(input_processor=MapCompose(clean_author_url), output_processor=TakeFirst())
    post_url = scrapy.Field(output_processor=TakeFirst())
    pass


class AuthorParseItem(scrapy.Item):
    name = "Harb_Authors"
    _id = scrapy.Field()
    author_posts = scrapy.Field(output_processor=TakeFirst())
    # author_info = scrapy.Field()
    # nickname = scrapy.Field()
    # contacts = scrapy.Field()
    pass


class InstgramParsFeed(scrapy.Item):
    name = "Instgram_Parse"
    _id = scrapy.Field()
    user_name = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst())
    like_count = scrapy.Field(output_processor=TakeFirst())
    photo_url = scrapy.Field()
    photo_path = scrapy.Field()
    pass