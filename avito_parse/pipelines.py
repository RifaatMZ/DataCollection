# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class AvitoParsePipeline:

    def __init__(self):
        client = MongoClient()
        self.db = client['gb_parse_course']

    def process_item(self, item, spider):
        collection = self.db[item.name]
        collection.insert_one(item)
        return item


class ImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get('photo_url', []):
            try:
                yield Request(url)
            except ValueError as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photo_url'] = [itm[1] for itm in results][0]['url']   # from debugger/results
        item['photo_path'] = [itm[1] for itm in results][0]['path']
        return item