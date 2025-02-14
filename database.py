import sqlite3
from datetime import datetime

connection = sqlite3.connect("fake_kfc.db")
sql = connection.cursor()

sql.execute("CREATE TABLE IF NOT EXISTS users "
            "(user_id INTEGER, name TEXT, "
            "phone_number TEXT, reg_date DATETIME);")
sql.execute("CREATE TABLE IF NOT EXISTS products "
            "(pr_id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "pr_name TEXT, pr_quantity INTEGER, pr_price REAL,"
            "pr_desc TEXT, pr_photo TEXT, reg_date DATETIME);")
sql.execute("CREATE TABLE IF NOT EXISTS cart (user_id INTEGER,"
            "pr_id INTEGER, pr_count INTEGER, pr_name TEXT, "
            "total_price REAL);")
connection.commit()

def add_user(name, phone_number, user_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute(f"INSERT INTO users (user_id, name, phone_number, reg_date) "
                "VALUES (?, ?, ?, ?);", (user_id, name, phone_number, datetime.now()))
    connection.commit()

def check_user(user_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    checker = sql.execute("SELECT * FROM users WHERE user_id=?", (user_id, )).fetchone()
    if checker:
        return True
    elif not checker:
        return False
def get_all_users():
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    all_users = sql.execute("SELECT * FROM users;").fetchall()
    return all_users
# продукты
def add_product(pr_name, pr_price, pr_desc, pr_quantity, pr_photo):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute("INSERT INTO products (pr_name, pr_price, pr_desc, pr_quantity, "
                "pr_photo, reg_date) VALUES (?, ?, ?, ?, ?, ?);",
                (pr_name, pr_price, pr_desc, pr_quantity, pr_photo, datetime.now()))
    connection.commit()
def get_all_products():
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    all_products = sql.execute("SELECT * FROM products;").fetchall()
    return all_products
def delete_product(pr_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute("DELETE FROM products WHERE pr_id=?;", (pr_id, ))
    connection.commit()

def get_exact_product(pr_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    exact_product = sql.execute("SELECT pr_name, pr_price, pr_desc, pr_photo "
                                "FROM products WHERE pr_id=?;", (pr_id, )).fetchone()
    return exact_product
def get_pr_id_name():
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    # вытаскиваем всю инфу перед фильтрацией
    all_products = sql.execute("SELECT pr_id, pr_name, pr_quantity "
                               "FROM products;").fetchall()
    # фильтрация продуктов которых больше 0
    actual_products = [[product[0], product[1]] for product in all_products if product[2] > 0]
    return actual_products

def delete_all_products():
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute("DELETE FROM products;")
    connection.commit()

def change_quantity(pr_id, pr_quantity):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute("UPDATE products SET pr_quantity=? WHERE pr_id=?;", (pr_quantity, pr_id))
    connection.commit()

# корзина
def add_to_cart(user_id, pr_id, pr_name, pr_count, pr_price):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    total_price = pr_price * pr_count
    sql.execute("INSERT INTO cart (user_id, pr_id, pr_name, "
                "pr_count, total_price) VALUES (?, ?, ?, ?, ?);",
                (user_id, pr_id, pr_name, pr_count, total_price))
    connection.commit()
# информация о корзине для кнопок удаления
def get_card_id_name(user_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    product = sql.execute("SELECT pr_id, pr_name FROM cart WHERE user_id=?;",
                          (user_id, )).fetchall()
    return product
# удаление продукта через кнопки в корзине
def delete_exact_product_from_cart(user_id, pr_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute("DELETE FROM cart WHERE user_id=? and pr_id=?;",
                (user_id, pr_id))
    connection.commit()
# очищение корзины юзера
def delete_user_cart(user_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    sql.execute("DELETE FROM cart WHERE user_id=?;", (user_id, ))
    connection.commit()
# получение информации для меню корзины в формате
# (Название продукта ; количество ; цена)
def get_user_cart(user_id):
    connection = sqlite3.connect("fake_kfc.db")
    sql = connection.cursor()
    user_cart = sql.execute("SELECT pr_name, pr_count, total_price FROM cart "
                            "WHERE user_id=?;", (user_id,)).fetchall()
    return user_cart
