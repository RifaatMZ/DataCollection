from scrapy.crawler import  CrawlerProcess
from scrapy.settings import Settings

from avito_parse import settings
from avito_parse.spiders.avito import AvitoSpider

from avito_parse.spiders.habr import HabrSpider

if __name__ == '__main__':
    crawl_settigns = Settings()
    crawl_settigns.setmodule(settings)
    crawol_proc = CrawlerProcess(settings=crawl_settigns)

    # crawol_proc.crawl(AvitoSpider)
    crawol_proc.crawl(HabrSpider)

    crawol_proc.start()



