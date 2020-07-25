from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
import requests

class GbBlogParse:
    __domain = 'https://geekbrains.ru'
    __url = 'https://geekbrains.ru/posts'
    __done_urls = set()

    def __init__(self):
        client= MongoClient('localhost:27017')
        data_base = client['parse_gb']
        self.collection = data_base['posts']
        self.posts_urls = set()
        self.pagination_urls = set()

    def get_page_soap(self, url):
        response = requests.get(url)
        soup = bs(response.text, 'lxml')
        return soup

    def run(self, url=None):
        url = url or self.__url
        soup = self.get_page_soap(url)
        self.pagination_urls.update(self.get_pagination(soup))
        self.posts_urls.update(self.get_posts_urls(soup))

        for url in tuple(self.pagination_urls):
            if url not in self.__done_urls:
                self.__done_urls.add(url)
                self.run(url)
        self.save_to_mongo()

    def get_pagination(self, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in ul.find_all('a') if a.get("href")]
        return a_list

    def get_posts_urls(self, soup):
        posts_wrap = soup.find('div', attrs={'class': 'post-items-wrapper'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in
                  posts_wrap.find_all('a', attrs={'class': 'post-item__title'})]
        return a_list

    def get_title(self, soup):
        post_title = soup.find('h1', class_="blogpost-title text-left text-dark m-t-sm").text
        return post_title

    def get_author_data(self, soup):
        author = soup.find('div', class_='row m-t')
        author_name = author.find('div', class_='text-lg text-dark').text
        author_url = author.find('a')['href']
        author_url = f'{self.__domain}{author_url}'
        return (author_name, author_url)

    def get_images(self, soup):
        urls = []
        images = soup.find('div', class_='blogpost-content content_text content js-mediator-article')
        image_urls = images.find_all('img')
        for link in image_urls:
            urls.append(link['src'])
        return urls

    def get_post_content(self, soup):
        content_source = soup.find('div', class_='blogpost-content content_text content js-mediator-article')
        text = content_source.text
        return(text)

    def save_to_mongo(self):
        counter = 0
        done_url = self.__done_urls
        for i in done_url:
            soup = self.get_page_soap(i)
            post_urls = self.get_posts_urls(soup)
            for j in post_urls:
                inner_soup = self.get_page_soap(j)
                spam = {'title': self.get_title(inner_soup),
                        'post_url': j,
                        'writer_name': self.get_author_data(inner_soup)[0],
                        'writer_url': self.get_author_data(inner_soup)[1],
                        'images': self.get_images(inner_soup),
                        'text': self.get_post_content(inner_soup)}
                counter += 1
                self.collection.insert_one(spam)


if __name__ == '__main__':
    parser = GbBlogParse()
    parser.run()
    print(1)
