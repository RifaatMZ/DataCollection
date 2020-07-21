from bs4 import BeautifulSoup as bs
import requests
import json
import os


class GbBlogParse:
    __domain = 'https://geekbrains.ru'
    __url = 'https://geekbrains.ru/posts'
    __done_urls = set()

    def __init__(self):
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
        self.save_to_file()

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

    def save_to_file(self):
        counter = 0
        if not os.path.exists('json_files'):
            os.mkdir('json_files')
        done_url = self.__done_urls
        for i in done_url:
            soup = self.get_page_soap(i)
            post_urls = self.get_posts_urls(soup)
            for j in post_urls:
                inner_soup = self.get_page_soap(j)
                spam = {'title': '',
                        'post_url': '',
                        'writer_name': '',
                        'writer_url': ''
                        }
                spam['title'] = self.get_title(inner_soup)
                spam['post_url'] = j
                spam['writer_name'], spam['writer_url'] = self.get_author_data(inner_soup)

                counter += 1
                with open(F'json_files/Post #{counter}.json', 'w', encoding='UTF-8') as file:
                    json.dump(spam, file, ensure_ascii=False)\



if __name__ == '__main__':
    parser = GbBlogParse()
    parser.run()
    print(1)
