import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from services import Write_in_exel, Data_parsing


def choose_file():
    global file_path
    file_path = filedialog.askopenfilename()


def start():
    url_text = url_from_user.get()
    parser = Data_parsing()
    if url_text != '':
        if checkbox_var.get():
            mb.showinfo(title="Початок", message="Процес почато")
            url_subpages_list = parser.link_to_all_pages(url_text)
            links_to_products = parser.links_to_products_from_all_pages(url_subpages_list)
            product_data = parser.read_product_data(links_to_products)
            Write_in_exel.write(file_path, 'Export Products Sheet', product_data)
            mb.showinfo(title="Успіх", message="Процес завершино")
            root.destroy()
        else:
            mb.showinfo(title="Початок", message="Процес почато")
            links_to_products = parser.links_to_products(url_text)
            product_data = parser.read_product_data(links_to_products)
            Write_in_exel.write(file_path, 'Export Products Sheet', product_data)
            mb.showinfo(title="Успіх", message="Процес завершино")
            root.destroy()
    elif url_text == '':
        mb.showerror(title="Пропущено рядок", message="Поле url має бути заповнене")


root = tk.Tk()
root.title("Парсер")
root.geometry("380x250+450+200")
root.resizable(width=False, height=False)


tk.Label(text='Введіть url', font=('Arial', 20)).pack()
url_from_user = tk.Entry(font=('Arial', 20), width=20, )
url_from_user.pack()

file = tk.Button(text="Вибрати файл", font=('Arial', 15), height=3, command=choose_file)
file.pack()

checkbox_var = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Всі сторінки", variable=checkbox_var, font=('Arial', 15))
checkbox.pack(padx=10)

start = tk.Button(text="Розпочати", font=('Arial', 15), width=27, command=start)
start.pack()

root.mainloop()
