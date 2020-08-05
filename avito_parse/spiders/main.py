from scrapy.crawler import  CrawlerProcess
from scrapy.settings import Settings
from avito_parse import settings
from avito_parse.spiders.avito import AvitoSpider
from avito_parse.spiders.habr import HabrSpider
from avito_parse.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    crawl_settigns = Settings()
    crawl_settigns.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settigns)
    # crawl_proc.crawl(AvitoSpider)
    # crawl_proc.crawl(HabrSpider)
    crawl_proc.crawl(InstagramSpider,
                     'rmzr89',
                     '#PWD_INSTAGRAM_BROWSER:10:1596458885:AaFQAMRU2Zom4srocL5c79QiIYxcto8PeIV4Y2Eu1cvmgB5rusc28MoUDPPKa7GoSt1Rs8JfIoVa4hw/g3oxHCxsEBiq4nDD0Mma0erx2cCTzmUH6SwMJFSYkalXmUaUk1jVCwlBKPlQfZwXJ+ty4Rw=',
                     ['rifaat_st'])
    crawl_proc.start()



