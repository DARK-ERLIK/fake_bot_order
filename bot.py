import buttons as bt
import database as db
import requests
from geopy.geocoders import Nominatim
import telebot

token = "7633981899:AAFV_kqgWoMa2N2ELUzZhEE5bZCodPzEwQ4"
bot = telebot.TeleBot(token)

geolocator = Nominatim(user_agent="geo_bot")

url = f'https://api.telegram.org/bot{token}/getUpdates'
response = requests.get(url)

if response.status_code == 200:
    updates = response.json()
    print(updates)
else:
    print(f"Error: {response.status_code}")

users = {}

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Добро пожаловать в бот доставки!")
    checker = db.check_user(user_id)
    if checker == True:
        bot.send_message(user_id, "Главное меню: ", reply_markup=bt.main_menu_kb())
    elif checker == False:
        bot.send_message(user_id, "Введите своё имя для регистрации")
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(user_id, "Теперь поделитесь своим номером", reply_markup=bt.phone_button())
    bot.register_next_step_handler(message, get_phone_number, name)

def get_phone_number(message, name):
    user_id = message.from_user.id
    if message.contact:
        phone_number = message.contact.phone_number
        bot.send_message(user_id, "Отправьте свою локацию", reply_markup=bt.location_button())
        bot.register_next_step_handler(message, get_location, name, phone_number)
    else:
        bot.send_message(user_id, "Отправьте свой номер через кнопку в меню")
        bot.register_next_step_handler(message, get_phone_number, name)

def get_location(message, name, phone_number):
    user_id = message.from_user.id
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        address = geolocator.reverse((latitude, longitude)).address
        db.add_user(name=name, phone_number=phone_number, user_id=user_id)
        bot.send_message(user_id, "Вы успешно зарегистрировались!")
        bot.send_message(user_id, "Главное меню: ", reply_markup=bt.main_menu_kb())
    else:
        bot.send_message(user_id, "Отправьте свою локацию через кнопку в меню")
        bot.register_next_step_handler(message, get_location, name, phone_number)

@bot.callback_query_handler(lambda call: call.data in ["cart", "back", "plus", "minus", "to_cart", "main_menu", "order", "clear_cart"])
def all_cals(call):
    user_id = call.message.chat.id
    if call.data == "cart":
        bot.delete_message(user_id, call.message.message_id)
        cart = db.get_user_cart(user_id)
        full_text = "Ваша корзина: \n"
        count = 0
        total_price = 0
        for product in cart:
            count += 1
            full_text += f"{count}. {product[0]} x {product[1]} = {product[2]}\n"
            total_price += product[2]
        bot.send_message(user_id, full_text + f"\n\nИтоговая сумма: {total_price} сум", reply_markup=bt.get_cart_kb())
    elif call.data == "back":
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "Главное меню: ", reply_markup=bt.main_menu_kb())
    elif call.data == "plus":
        current_amount = users[user_id]["pr_count"]
        users[user_id]["pr_count"] += 1
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=bt.plus_minus_in("plus", current_amount))
    elif call.data == "minus":
        current_amount = users[user_id]["pr_count"]
        if current_amount > 1:
            users[user_id]["pr_count"] -= 1
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=bt.plus_minus_in("minus", current_amount))
    elif call.data == "to_cart":
        db.add_to_cart(user_id, users[user_id]["pr_id"], users[user_id]["pr_name"], users[user_id]["pr_count"], users[user_id]["pr_price"])
        users.pop(user_id)
        bot.delete_message(user_id, call.message.message_id)
        all_products = db.get_pr_id_name()
        bot.send_message(user_id, "Продукт успешно добавлен в корзину.\nЖелаете выбрать что-то еще?", reply_markup=bt.products_in(all_products))
    elif call.data == "main_menu":
        all_products = db.get_pr_id_name()
        bot.send_message(user_id, "Выберите продукт", reply_markup=bt.products_in(all_products))
    elif call.data == "order":
        bot.delete_message(user_id, call.message.message_id)
        cart = db.get_user_cart(user_id)
        full_text = f"Новый заказ от пользователя с id {user_id}: \n"
        count = 0
        total_price = 0
        for product in cart:
            count += 1
            full_text += f"{count}. {product[0]} x {product[1]} = {product[2]}\n"
            total_price += product[2]
        bot.send_message(6648488312, full_text + f"\n\nИтоговая сумма: {total_price} сум")
        bot.send_message(user_id, "Ваш заказ принят и обрабатывается оператором", reply_markup=bt.main_menu_kb())
        db.delete_user_cart(user_id)
    elif call.data == "clear_cart":
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "Ваша корзина очищена", reply_markup=bt.main_menu_kb())
        db.delete_user_cart(user_id)

@bot.callback_query_handler(lambda call: "prod_" in call.data)
def get_prod_info(call):
    user_id = call.message.chat.id
    bot.delete_message(user_id, call.message.message_id)
    product_id = int(call.data.replace("prod_", ""))
    product_info = db.get_exact_product(product_id)
    users[user_id] = {"pr_id": product_id, "pr_name": product_info[0], "pr_count": 1, "pr_price": product_info[1]}
    bot.send_photo(user_id, photo=product_info[3], caption=f"{product_info[0]}\n\n{product_info[2]}\nЦена: {product_info[1]}", reply_markup=bt.plus_minus_in())

@bot.message_handler(content_types=["text"])
def main_menu(message):
    user_id = message.from_user.id
    if message.text == "🍴Меню":
        all_products = db.get_pr_id_name()
        bot.send_message(user_id, "Выберите продукт:", reply_markup=bt.products_in(all_products))
    elif message.text == "🛒Корзина":
        bot.send_message(user_id, "Ваша корзина: ")
    elif message.text == "✒️Отзыв":
        bot.send_message(user_id, "Напишите текст вашего отзыва: ")

bot.infinity_polling()
