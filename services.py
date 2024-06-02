import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


class Data_parsing:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

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
    def get_product_photo(content: str) -> str:
        """
        :param content: The text that returned the request
        :return: a string with a link to a product photo
        """
        soup = BeautifulSoup(content, 'html.parser')
        imgs = soup.find_all('img', class_="img-responsive", id="ProductPhotoImg")
        for img in imgs:
            img_url = img['src']
            return img_url

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
        + if in stock, - if not in stock
        '''
        soup = BeautifulSoup(content, 'html.parser')
        stocks = soup.find_all('div', class_="spec-wrapper")
        for stock in stocks:
            stock_status = stock.find('div', class_='stock hidden-xs hidden-sm nospesh')
            if stock_status:
                in_stock = stock_status.get_text(strip=True)
                if in_stock == 'В наявності':
                    return '+'
                else:
                    return '-'

    def read_product_data(self, links_list: list):
        """
        :param links_list: List of links to products
        :return: Double array of product information
        """
        list_of_products_data = []
        for i in links_list:
            list_of_product_data = []
            request = requests.get(i, headers=self.headers)
            if request.status_code == 200:
                content = request.text

                # getting a product name
                list_of_product_data.append(self.get_product_name(content))

                # getting the price of the product
                list_of_product_data.append(self.get_product_price(content))

                # getting a link to a product photo
                list_of_product_data.append(self.get_product_photo(content))

                # getting a product description
                list_of_product_data.append(self.get_product_description(content))

                # getting a product article
                list_of_product_data.append(self.get_product_article(content))

                # getting a product stock status
                list_of_product_data.append((self.get_product_in_stock(content)))

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
            "Опис": data_matrix[3],
            "Тип_товару": ['r' for _ in range(len(data_matrix[0]))],
            "Ціна": data_matrix[1],
            "Валюта": ['UAH' for _ in range(len(data_matrix[0]))],
            "Одиниця_виміру": ['шт.' for _ in range(len(data_matrix[0]))],
            "Посилання_зображення": data_matrix[2],
            "Наявність": data_matrix[5],
            "Ідентифікатор_товару": data_matrix[4],
        }

        df = pd.DataFrame(data)

        with pd.ExcelWriter("Export_Products.xlsx", engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
