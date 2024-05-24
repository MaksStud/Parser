import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def number_of_all_subpages(url: str) -> list:
    """
    :param url: Link to the page
    :return: List of links to subpages
    """
    request = requests.get(url, headers=headers)
    link_list = []
    max_page = 0

    if request.status_code == 200:
        content = request.text
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
                max_page = max(page_numbers)

    for i in range(max_page):
        link_list.append(url + f"&page={i + 1}")
    return link_list


def links_to_products(url: str) -> list:
    """
    :param url: Link to the page
    :return: List of links to products that are on this page
    """
    request = requests.get(url, headers=headers)
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


def links_to_products_from_all_pages(urls: list):
    """
    :param urls: List of links to pages
    :return: Links to all products that are on the page from the list
    """
    link_list = []
    for i in urls:
        request = requests.get(i, headers=headers)

        if request.status_code == 200:
            content = request.text
            soup = BeautifulSoup(content, 'html.parser')

            items = soup.find_all('div', class_='image')
            for item in items:
                link_tag = item.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    link_list.append(link_tag['href'])
    return link_list


def read_product_data(links_list: list):
    """
    :param links_list: List of links to products
    :return: Double array of product information
    """
    data = []
    for i in links_list:
        new_list = []
        request = requests.get(i, headers=headers)
        if request.status_code == 200:
            content = request.text
            soup = BeautifulSoup(content, 'html.parser')

            # getting a product name
            names = soup.find_all('div', class_="prod_header")
            for j in names:
                name = j.find('h1').get_text()
                new_list.append(name)

            # getting the price of the product
            prices = soup.find_all('div', class_='normal')
            for price in prices:
                price_new = price.find('span', class_='price-new')
                if price_new:
                    price_value = price_new.get_text(strip=True).replace('₴', '').replace(' ', '')
                    new_list.append(price_value)

            # getting a link to a product photo
            imgs = soup.find_all('img', class_="img-responsive", id="ProductPhotoImg")
            for img in imgs:
                img_url = img['src']
                new_list.append(img_url)

            # getting a product description
            descriptions = soup.find_all('div', class_="prod-description-wrap clip")
            for desc in descriptions:
                list_items = desc.find_all('li')
                descriptions_text = '; '.join([li.get_text(strip=True) for li in list_items])
                new_list.append(descriptions_text)

            data.append(new_list)
    return data


def write_in_exel(file_path: str, sheet_name: str, data_matrix) -> None:
    """
    :param file_path: The path to the file in which to write
    :param sheet_name: Name of the page in the file to which you want to write
    :param data_matrix: Double array of product data
    :return: None
    """
    data_matrix = np.array(data_matrix)
    data_matrix = np.transpose(data_matrix)
    data = {
        'Название_позиции': data_matrix[0],
        'Описание': data_matrix[3],
        'Цена': data_matrix[1],
        'Ссылка_изображения': data_matrix[2]
    }

    df_new = pd.DataFrame(data)

    df_existing = pd.read_excel(file_path, sheet_name=sheet_name)

    for column in df_existing.columns:
        if column not in df_new.columns:
            df_new[column] = pd.NA

    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df_combined.to_excel(writer, sheet_name=sheet_name, index=False)
