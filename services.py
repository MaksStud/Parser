import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import data


class Data_parsing:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    @staticmethod
    def what_language_url(url):
        if 'https://1-m.com.ua/ua/' in url:
            return 'ukr'
        else:
            return 'russ'

    @staticmethod
    def reading_the_number_of_pages(content: str) -> int:
        """
        :param content: The text that returned the request
        :return: number of all pages
        """
        soup = BeautifulSoup(content, 'html.parser')

        pagination = soup.find('ul', class_="pagination")
        if pagination:
            page_links = pagination.find_all('a')
            page_numbers = []

            for link in page_links:
                href = link.get('href')
                if href and 'page=' in href:
                    page_num = href.split('page=')[-1]
                    if page_num.isdigit():
                        page_numbers.append(int(page_num))

            if page_numbers:
                return max(page_numbers)

    def link_to_all_pages(self, url: str) -> list:
        """
        Reads the largest page number and generates links to all pages and returns a list of them
        :param url: Link to the page
        :return: List of links to all pages
        """
        request = requests.get(url, headers=self.headers)
        link_list = []
        max_page = 0

        if request.status_code == 200:
            content = request.text

            max_page = self.reading_the_number_of_pages(content)

        for i in range(max_page):
            link_list.append(url + f"&page={i + 1}")
        return link_list

    @staticmethod
    def search_for_a_product_page(content: str):
        """
        :param content: The text that returned the request
        :return: link to the product page
        """
        soup = BeautifulSoup(content, 'html.parser')
        link_list = []

        items = soup.find_all('div', class_='image')
        for item in items:
            link_tag = item.find('a')
            if link_tag and 'href' in link_tag.attrs:
                link_list.append(link_tag['href'])
        return link_list

    def links_to_products(self, url: str) -> list:
        """
        :param url: Link to the page
        :return: List of links to products that are on this page
        """
        request = requests.get(url, headers=self.headers)
        link_list = []

        if request.status_code == 200:
            content = request.text
            soup = BeautifulSoup(content, 'html.parser')

            items = soup.find_all('div', class_='image')
            for item in items:
                link_tag = item.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    link_list.append(link_tag['href'])
            return link_list

    def links_to_products_from_all_pages(self, urls: list):
        """
        :param urls: List of links to pages
        :return: Links to all products that are on the page from the list
        """
        link_list = []
        for i in urls:
            request = requests.get(i, headers=self.headers)

            if request.status_code == 200:
                content = request.text
                link_list.extend(self.search_for_a_product_page(content))

        return link_list

    @staticmethod
    def get_product_name(content: str) -> str:
        """
        :param content: The text that returned the request
        :return: string with the product name
        """
        soup = BeautifulSoup(content, 'html.parser')
        names = soup.find_all('div', class_="prod_header")
        for j in names:
            name = j.find('h1').get_text()
            return name

    @staticmethod
    def get_product_price(content: str) -> float:
        """
        :param content: The text that returned the request
        :return: string with the product price
        """
        soup = BeautifulSoup(content, 'html.parser')
        prices = soup.find_all('div', class_='normal')
        for price in prices:
            price_new = price.find('span', class_='price-new')
            if price_new:
                price_value = price_new.get_text(strip=True).replace('₴', '').replace(' ', '')
                return float(price_value)

    @staticmethod
    def get_product_photos(content: str) -> str:
        """
        :param content: The HTML content as a string
        :return: a list of strings with links to product photos
        """
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for a in soup.find_all('a', class_='fancy-prod el zoom data-fancybox-images'):
            href = a.get('href')
            if href:
                links.append(href)
        return ' '.join(links)

    @staticmethod
    def get_product_description(content: str) -> str:
        """
        :param content: The text that returned the request
        :return: a string from the product description
        """
        soup = BeautifulSoup(content, 'html.parser')
        descriptions = soup.find_all('div', class_="prod-description-wrap clip")
        for desc in descriptions:
            list_items = desc.find_all('li')
            descriptions_text = '; '.join([li.get_text(strip=True) for li in list_items])
            return descriptions_text

    @staticmethod
    def get_product_article(content: str) -> int:
        '''
        :param content: The text that returned the request
        :return: number from the product article
        '''
        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find_all('div', class_="model")
        for art in articles:
            return int(art.get_text().replace('Артикул:', ''))

    @staticmethod
    def get_product_in_stock(content: str) -> str:
        '''
        :param content: The text that returned the request
        :return:
        + if in stock, - if not in stock or +
        '''
        soup = BeautifulSoup(content, 'html.parser')
        stocks = soup.find_all('div', class_='spec-wrapper')
        for stock in stocks:
            stock_status = stock.find('div', class_='stock')
            if stock_status:
                in_stock = stock_status.get_text(strip=True)
                if in_stock in data.in_stock_list:
                    return '+'
        return '-'

    @staticmethod
    def get_product_group_id(name: str) -> int:
        return data.groups_id.get(name)

    @staticmethod
    def get_product_group(content: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        groups_name = soup.find_all('ul', class_="breadcrumb")
        for group in groups_name:
            return group.text.split('\n')[-2]

    @staticmethod
    def get_search_queries(content: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        groups_list = soup.find_all('ul', class_="breadcrumb")
        for i in groups_list:
            return i.text.replace('\n', ', ')[4::]

    @staticmethod
    def get_product_characteristics(content: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        characteristics = soup.find_all('div', class_="prod-description-wrap")

        for i in characteristics:
            str_list = i.get_text(strip=True, separator='#').split('#')[1:-1]
            return '\n'.join(str_list)

    def read_product_data(self, links_list: list):
        """
        :param links_list: List of links to products
        :return: Double array of product information
        """
        list_of_products_data = []
        for i in links_list:
            list_of_product_data = []
            convert_url = Convert_url()
            links = convert_url.double_link(i)

            request_russ = requests.get(links['russ'], headers=self.headers)
            request_ua = requests.get(links['ua'], headers=self.headers)

            if request_russ.status_code == 200 and request_ua.status_code == 200:
                content_russ = request_russ.text
                content_ua = request_ua.text

                # getting a product russ name
                list_of_product_data.append(self.get_product_name(content_russ))

                # getting a product ua name
                list_of_product_data.append(self.get_product_name(content_ua))

                # getting a product search queries russ
                list_of_product_data.append(self.get_search_queries(content_russ))

                # getting a product search queries ua
                list_of_product_data.append(self.get_search_queries(content_ua))

                # getting the price of the product
                list_of_product_data.append(self.get_product_price(content_russ))

                # getting a link to a product photo
                list_of_product_data.append(self.get_product_photos(content_russ))

                # getting a product russ description
                list_of_product_data.append(self.get_product_description(content_russ))

                # getting a product ua description
                list_of_product_data.append(self.get_product_description(content_ua))

                # getting a product article
                list_of_product_data.append(self.get_product_article(content_russ))

                # getting a product stock status
                list_of_product_data.append(self.get_product_in_stock(content_russ))

                # getting a product group
                group_name = self.get_product_group(content_russ)
                list_of_product_data.append(group_name)

                # getting a product id group
                list_of_product_data.append(self.get_product_group_id(group_name))

                # getting a product characteristic
                list_of_product_data.append(self.get_product_characteristics(content_russ))

                list_of_products_data.append(list_of_product_data)

        return list_of_products_data


class Write_in_exel:
    @staticmethod
    def write(data_matrix) -> None:
        """
        :param data_matrix: Double array of product data
        :return: None
        """
        sheet_name = 'Export Products Sheet'

        data_matrix = np.array(data_matrix)
        data_matrix = np.transpose(data_matrix)
        data = {
            "Назва_позиції": data_matrix[0],
            "Назва_позиції_укр": data_matrix[1],
            "Пошукові_запити": data_matrix[2],
            "Пошукові_запити_укр": data_matrix[3],
            "Опис": data_matrix[6],
            "Опис_укр": data_matrix[7],
            "Тип_товару": ['r' for _ in range(len(data_matrix[0]))],
            "Ціна": data_matrix[4],
            "Валюта": ['UAH' for _ in range(len(data_matrix[0]))],
            "Одиниця_виміру": ['шт.' for _ in range(len(data_matrix[0]))],
            "Посилання_зображення": data_matrix[5],
            "Наявність": data_matrix[9],
            "Номер_групи": data_matrix[11],
            "Назва_групи": data_matrix[10],
            "Ідентифікатор_товару": data_matrix[8],
            "Назва_Характеристики": data_matrix[12]
        }
        df = pd.DataFrame(data)

        with pd.ExcelWriter("Export_Products.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)


class Convert_url:

    @staticmethod
    def double_link(url) -> dict:
        if '/ua/' in url:
            russ_url = url.replace("https://1-m.com.ua/ua/", "https://1-m.com.ua/", 1)
            return {'russ': russ_url, 'ua': url}
        else:
            ua_url = url.replace("https://1-m.com.ua/", "https://1-m.com.ua/ua/", 1)
            return {'russ': url, 'ua': ua_url}
