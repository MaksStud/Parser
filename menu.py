import tkinter as tk
from tkinter import messagebox as mb
from services import Write_in_exel, Data_parsing
import threading


def parsing(url_text, ):
    parser = Data_parsing()

    if checkbox_var.get():
        url_subpages_list = parser.link_to_all_pages(url_text)
        links_to_products = parser.links_to_products_from_all_pages(url_subpages_list)
    else:
        links_to_products = parser.links_to_products(url_text)

    product_data = parser.read_product_data(links_to_products)
    Write_in_exel.write(product_data)

    mb.showinfo(title="Успіх", message="Процес завершено")


def start():
    url_text = url_from_user.get()
    if url_text != '':
        mb.showinfo(title="Початок", message="Процес почато")

        threading.Thread(target=parsing, args=(url_text,)).start()

    elif url_text == '':
        mb.showerror(title="Пропущено рядок", message="Поле url має бути заповнене")


root = tk.Tk()
root.title("Парсер")
root.geometry("380x170+550+200")
root.resizable(width=False, height=False)


tk.Label(text='Введіть url', font=('Arial', 20)).pack()
url_from_user = tk.Entry(font=('Arial', 20), width=20, )
url_from_user.pack()

checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Всі сторінки", variable=checkbox_var, font=('Arial', 15))
checkbox.pack(padx=10)

start = tk.Button(text="Розпочати", font=('Arial', 15), width=27, command=start)
start.pack()

root.mainloop()
