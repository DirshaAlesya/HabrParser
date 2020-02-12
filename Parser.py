from bs4 import BeautifulSoup
import requests


class HabrParser:
    def __init__(self):
        self.url = 'https://habr.com/ru/hub/python/'

    def parser(self):
        result = []
        r = requests.get(self.url)
        html_page = r.content

        soup = BeautifulSoup(html_page, 'html.parser')

        value = soup.find_all('h2', {'class': "post__title"})
        for title in value:
            h = title.find('a', {'class': "post__title_link"}, href=True)
            result.append(h['href'])
        return result

# ps = HabrParser()
# r = ps.parser()
