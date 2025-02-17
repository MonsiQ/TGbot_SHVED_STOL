import telebot
from telebot import types
import psycopg2
import datetime
import xlwt

conn = psycopg2.connect(user="postgres",
                        password="0000",
                        host="127.0.0.1",
                        port="5432",
                        database="shved_stol")
cur = conn.cursor()
bot = telebot.TeleBot("6525136024:AAFpVOa0ClnokyDW5DKR8W9LgMYbMQ1gkaQ")
user_states = {}
admin_password = "123"
admin_requests = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    cur.execute("SELECT status FROM users WHERE user_id = %s", (str(user_id),))
    user_status = cur.fetchone()
    if user_status and user_status[0] == 'активный':
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu_user())
    elif user_status and user_status[0] == 'ожидание':
        bot.send_message(message.chat.id, "Ваша заявка на рассмотрении. Пожалуйста, подождите.")
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button = types.KeyboardButton("Авторизоваться")
        keyboard.add(button)
        msg = bot.reply_to(message, "Добро пожаловать! Нажмите кнопку 'Авторизоваться' для начала:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, fio)

def fio(message):
    if message.text == 'Авторизоваться':
        user_id = message.from_user.id
        user_states[user_id] = {}
        msg = bot.reply_to(message, "Введите ваше ФИО:")
        bot.register_next_step_handler(msg, vvod_departure_date)
    else:
        bot.reply_to(message, "Пожалуйста, воспользуйтесь кнопкой 'Авторизоваться'.")

def vvod_departure_date(message):
    full_name = message.text
    user_id = message.from_user.id
    user_states[user_id]['full_name'] = full_name
    msg = bot.reply_to(message, "Введите дату выезда в формате ДД.ММ.ГГГГ (например, 01.01.2024):")
    bot.register_next_step_handler(msg, finish_departure_date)

def finish_departure_date(message):
    date_text = message.text
    user_id = message.from_user.id
    full_name = user_states[user_id]['full_name']
    try:
        departure_date = datetime.datetime.strptime(date_text, '%d.%m.%Y').date()
        today = datetime.datetime.now().date()
        if departure_date < today:
            bot.send_message(message.chat.id,
                             "Вы выбрали прошедшую дату. Пожалуйста, начните сначала.")
            start(message)
            return
        user_id = save_user_info(full_name, departure_date, user_id)
        bot.send_message(message.chat.id, "Спасибо! Ваша заявка отправлена на рассмотрение.")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный формат даты. Пожалуйста, начните сначала.")
        start(message)

def save_user_info(full_name, departure_date, user_id):
    cur.execute("SELECT EXISTS (SELECT 1 FROM users WHERE user_id = %s)", (user_id,))
    user_exists = cur.fetchone()[0]

    if user_exists:
        sql = "UPDATE users SET full_name = %s, departure_date = %s, status = 'ожидание' WHERE user_id = %s"
        cur.execute(sql, (full_name, departure_date, user_id))
    else:
        sql = "INSERT INTO users (full_name, departure_date, status, user_id) VALUES (%s, %s, 'ожидание', %s) RETURNING user_id"
        cur.execute(sql, (full_name, departure_date, user_id))
        user_id = cur.fetchone()[0]
    conn.commit()
    return user_id

def main_menu_user():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Меню"))
    keyboard.add(types.KeyboardButton("Заказать"))
    keyboard.add(types.KeyboardButton("Отменить заказ"))
    return keyboard

@bot.message_handler(func=lambda message: message.text == 'Меню')
def menu_dishes(message):
    cur.execute("SELECT dish_id, dish_name, meal FROM dishes")
    dishes = cur.fetchall()
    if dishes:
        menu_by_meal = {}
        for dish in dishes:
            dish_id, dish_name, meal = dish
            if meal not in menu_by_meal:
                menu_by_meal[meal] = []
            menu_by_meal[meal].append((dish_id, dish_name))

        response = "Меню:\n\n"
        for meal, meal_dishes in menu_by_meal.items():
            response += f"{meal.capitalize()}:\n"
            for dish_id, dish_name in meal_dishes:
                response += f"{dish_id}. {dish_name}\n"
            response += "\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Меню пусто.")

@bot.message_handler(func=lambda message: message.text == 'Заказать')
def select_time(message):
    user_id = message.from_user.id
    current_date = datetime.datetime.now().date()

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Завтрак"), types.KeyboardButton("Обед"), types.KeyboardButton("Ужин"),
                 types.KeyboardButton("Назад"))
    msg = bot.reply_to(message, "Выберите время приема пищи:", reply_markup=keyboard)
    user_states[message.from_user.id] = {'meal': None}
    bot.register_next_step_handler(msg, menu_time_dish)

def menu_time_dish(message):
    meal = message.text.lower()
    if meal == 'назад':
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu_user())
        return

    user_id = message.from_user.id
    user_states[user_id]['meal'] = meal
    cur.execute("SELECT dish_id, dish_name, dish_description FROM dishes WHERE meal = %s", (meal,))
    dishes = cur.fetchall()
    if dishes:
        response = f"Меню на {meal}:\n"
        for dish in dishes:
            dish_id, dish_name, dish_description = dish
            response += f"{dish_id}. {dish_name}\n{dish_description}\n\n"
        bot.send_message(message.chat.id, response)
        msg = bot.reply_to(message, "Введите номер блюда:")
        bot.register_next_step_handler(msg, confirm_order)
    else:
        bot.send_message(message.chat.id, f"Меню на {meal} пусто.")

def confirm_order(message):
    try:
        user_id = message.from_user.id
        current_date = datetime.datetime.now().date()

        dish_ids = [int(dish_id.strip()) for dish_id in message.text.split(',')]
        dish_id = dish_ids[0]  # Берем первый введенный ID блюда

        meal = user_states[user_id]['meal']

        cur.execute("SELECT meal FROM dishes WHERE dish_id = %s", (dish_id,))
        dish_meal = cur.fetchone()

        if not dish_meal:
            bot.send_message(message.chat.id, f"Блюда с номером {dish_id} не существует.")
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu_user())
            return

        dish_meal = dish_meal[0]

        if dish_meal != meal:
            bot.send_message(message.chat.id,
                             f"Блюдо с номером {dish_id} не соответствует выбранному времени приема пищи.")
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu_user())
            return

        delivery_date = current_date + datetime.timedelta(days=2)

        cur.execute(
            "INSERT INTO orders (user_id, delivery_date, time, status) VALUES (%s, %s, %s, %s) RETURNING order_id",
            (user_id, delivery_date, meal, 'ожидание'))
        order_id = cur.fetchone()[0]
        cur.execute("INSERT INTO order_dishes (order_id, dish_id) VALUES (%s, %s)", (order_id, dish_id))
        conn.commit()

        bot.send_message(message.chat.id, "Ваш заказ отправлен на рассмотрение, ожидайте!",
                         reply_markup=main_menu_user())
    except Exception as e:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu_user())

@bot.message_handler(func=lambda message: message.text == 'Отменить заказ')
def cancel_order(message):
    user_id = message.from_user.id
    cur.execute("SELECT orders.order_id, orders.delivery_date, orders.time, orders.status, dishes.dish_name, orders.created_at FROM orders JOIN order_dishes ON orders.order_id = order_dishes.order_id JOIN dishes ON order_dishes.dish_id = dishes.dish_id WHERE orders.user_id = %s AND (orders.status = 'активный' OR orders.status = 'ожидание')", (user_id,))
    user_orders = cur.fetchall()
    if user_orders:
        for order in user_orders:
            order_id, delivery_date, time, status, dish_name, created_at = order
            response = f"ID заказа: {order_id}, Блюдо: {dish_name}, Время подачи: {delivery_date}, Время: {time}, Статус: {status}, Создан: {created_at}\n"
            keyboard = types.InlineKeyboardMarkup()
            cancel_button = types.InlineKeyboardButton("Отменить", callback_data=f"cancel_order__{order_id}")
            keyboard.add(cancel_button)
            bot.send_message(message.chat.id, response, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "У вас нет активных или ожидающих заказов.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_order__'))
def cancel_order_callback(call):
    order_id = int(call.data.split('__')[-1])
    cur.execute("SELECT created_at FROM orders WHERE order_id = %s", (order_id,))
    created_at = cur.fetchone()[0]
    time_difference = datetime.datetime.now() - created_at
    if time_difference.total_seconds() <= 3600:
        cur.execute("UPDATE orders SET status = 'отменен' WHERE order_id = %s", (order_id,))
        conn.commit()
        bot.send_message(call.message.chat.id, f"Заказ с номером {order_id} был успешно отменен.")
    else:
        bot.send_message(call.message.chat.id, f"Извините, нельзя отменить заказ, прошло более часа с момента его создания.")

def delete_users_dep_date():
        cur.execute("SELECT user_id, table_number FROM users WHERE departure_date < CURRENT_DATE")
        expired_users = cur.fetchall()
        for user_id, table_number in expired_users:
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            cur.execute("SELECT seats_count, occupied_seats_count FROM tables WHERE table_number = %s", (table_number,))
            seats_count, occupied_seats_count = cur.fetchone()
            occupied_seats_count -= 1
            cur.execute("UPDATE tables SET occupied_seats_count = %s WHERE table_number = %s", (occupied_seats_count, table_number))
        conn.commit()

@bot.message_handler(commands=['admin'])
def password_admin_panel(message):
    msg = bot.reply_to(message, "Введите пароль для доступа к админ панели:")
    bot.register_next_step_handler(msg, admin_buttons)

def admin_buttons(message):
    if message.text == admin_password:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button1 = types.KeyboardButton("Просмотр заявок")
        button2 = types.KeyboardButton("Просмотр заказов")
        button3 = types.KeyboardButton("Пользователи")
        button4 = types.KeyboardButton("Отчет")
        keyboard.add(button1, button2, button3, button4)
        msg = bot.reply_to(message, "Вы успешно авторизованы. Выберите действие:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, main_menu_admin)
    else:
        bot.reply_to(message, "Неверный пароль.")

def main_menu_admin(message):
    if message.text == "Просмотр заявок":
        requests_list(message)
    elif message.text == "Просмотр заказов":
        orders_menu_buttons(message)
    elif message.text == "Пользователи":
        users_list(message)
    elif message.text == "Отчет":
        report(message)

@bot.message_handler(func=lambda message: message.text == 'Отчет')
def report(message):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Отчет')

    for col_num in range(6):
        ws.col(col_num).width = 9000

    style_header = xlwt.easyxf('font: bold on; borders: bottom thin, left thin, right thin, top thin; align: horiz center')
    style_data = xlwt.easyxf('borders: bottom thin, left thin, right thin, top thin; align: horiz left')

    cur.execute("SELECT COUNT(*) FROM users")
    total_users_count = cur.fetchone()[0]
    ws.write(0, 0, 'Общее количество пользователей:', style_header)
    ws.write(0, 1, total_users_count, style_data)

    cur.execute("SELECT COUNT(*) FROM dishes")
    total_dishes_count = cur.fetchone()[0]
    ws.write(1, 0, 'Общее количество блюд в меню:', style_header)
    ws.write(1, 1, total_dishes_count, style_data)

    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders_count = cur.fetchone()[0]
    ws.write(2, 0, 'Общее количество заказов:', style_header)
    ws.write(2, 1, total_orders_count, style_data)

    cur.execute("SELECT d.dish_name, COUNT(*) AS quantity " +
                "FROM orders o " +
                "JOIN order_dishes od ON o.order_id = od.order_id " +
                "JOIN dishes d ON od.dish_id = d.dish_id " +
                "GROUP BY d.dish_name")
    ordered_dishes_data = cur.fetchall()
    ws.write(3, 0, 'Заказанные блюда:', style_header)
    for idx, (dish_name, quantity) in enumerate(ordered_dishes_data, start=4):
        ws.write(idx, 0, dish_name, style_data)
        ws.write(idx, 1, quantity, style_data)

    ws.write(6, 0, 'Информация о заказах пользователя', style_header)
    ws.write(7, 0, 'Имя пользователя', style_header)
    ws.write(7, 1, 'Название блюда', style_header)
    ws.write(7, 2, 'Дата подачи', style_header)
    ws.write(7, 3, 'Время', style_header)
    ws.write(7, 4, 'Номер стола', style_header)
    ws.write(7, 5, 'Место за столом', style_header)

    cur.execute("SELECT u.full_name, d.dish_name, o.delivery_date, o.time, u.table_number, u.seat_number " +
                "FROM orders o " +
                "JOIN order_dishes od ON o.order_id = od.order_id " +
                "JOIN dishes d ON od.dish_id = d.dish_id " +
                "JOIN users u ON o.user_id = u.user_id")

    user_orders_data = cur.fetchall()
    for i, row in enumerate(user_orders_data, start=8):
        for j, value in enumerate(row):
            if j == 2:
                value = value.strftime("%Y-%m-%d") if value else ''
            ws.write(i, j, value, style_data)

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"report_{current_datetime}.xls"

    wb.save(filename)

    with open(filename, 'rb') as file:
        bot.send_document(message.chat.id, file)
        admin_main_menu_buttons(message)

def users_list(message):
    cur.execute("SELECT user_id, full_name, departure_date FROM users WHERE status = 'активный'")
    users = cur.fetchall()
    if users:
        for user in users:
            user_id, full_name, departure_date = user
            msg = f"User ID: {user_id}\nФИО: {full_name}\nДата выезда: {departure_date}\n"
            keyboard = types.InlineKeyboardMarkup()
            delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"delete_user_{user_id}")
            keyboard.add(delete_button)
            bot.send_message(message.chat.id, msg, reply_markup=keyboard)
        users_list_menu(message)
    else:
        bot.send_message(message.chat.id, "Активных пользователей нет.")
        admin_main_menu_buttons(message)

def users_list_menu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Назад"))
    msg = bot.reply_to(message, "Выберите действие:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, back_button)

def back_button(message):
    if message.text == "Назад":
        admin_main_menu_buttons(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_user_'))
def delete_user_callback(call):
    user_id = int(call.data.split('_')[-1])
    confirmation_keyboard = admin_user_choice(user_id)
    bot.send_message(call.message.chat.id, "Вы уверены, что хотите удалить этого пользователя?", reply_markup=confirmation_keyboard)

def admin_user_choice(user_id):
    keyboard = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton("Да", callback_data=f"confirm_delete_{user_id}")
    cancel_button = types.InlineKeyboardButton("Отмена", callback_data=f"cancel_delete_{user_id}")
    keyboard.add(confirm_button, cancel_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_user_callback(call):
    user_id = int(call.data.split('_')[-1])
    cur.execute("SELECT table_number FROM users WHERE user_id = %s", (user_id,))
    table_number = cur.fetchone()[0]
    cur.execute("UPDATE tables SET occupied_seats_count = occupied_seats_count - 1 WHERE table_number = %s", (table_number,))
    cur.execute("DELETE FROM order_dishes WHERE order_id IN (SELECT order_id FROM orders WHERE user_id = %s)", (user_id,))
    cur.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    bot.send_message(call.message.chat.id,
                     f"Пользователь с ID {user_id} был успешно удален из базы данных вместе со всеми его заказами.")
    remove_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(user_id, "Вы были удалены из базы данных. Вы можете авторизоваться, введите /start.",
                     reply_markup=remove_keyboard)
    admin_main_menu_buttons(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_delete_'))
def cancel_delete_user_callback(call):
    user_id = int(call.data.split('_')[-1])
    bot.send_message(call.message.chat.id, f"Удаление пользователя с ID {user_id} отменено.")
    admin_main_menu_buttons(call.message)

def orders_menu_buttons(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Активные заказы"), types.KeyboardButton("Заказы в ожидании"),
                 types.KeyboardButton("Отмененные заказы"), types.KeyboardButton("Назад"))
    msg = bot.reply_to(message, "Выберите тип заказов для просмотра:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, orders_menu)

def orders_menu(message):
    if message.text == "Заказы в ожидании":
        waiting_orders(message)
    elif message.text == "Отмененные заказы":
        cancelled_orders(message)
    elif message.text == "Назад":
        admin_main_menu_buttons(message)
    elif message.text == "Активные заказы":
        active_orders(message)

def active_orders(message):
    cur.execute("SELECT orders.order_id, orders.user_id, string_agg(order_dishes.dish_id::text, ', '), orders.delivery_date, orders.time FROM orders JOIN order_dishes ON orders.order_id = order_dishes.order_id WHERE orders.status = 'активный' GROUP BY orders.order_id")
    orders = cur.fetchall()
    if orders:
        for order in orders:
            order_id, user_id, dish_ids, delivery_date, time = order
            msg = f"ID Заявки: {order_id}\nID клиента: {user_id}\nБлюдо: {dish_ids}\nДата подачи: {delivery_date}\nВремя: {time}\n"
            keyboard = types.InlineKeyboardMarkup()
            cancel_button = types.InlineKeyboardButton("Снять", callback_data=f"cancel_order_{order_id}")
            keyboard.add(cancel_button)
            bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Активных заказов нет.")
        admin_main_menu_buttons(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_order_'))
def end_order(call):
    order_id = int(call.data.split('_')[-1])

    cur.execute("SELECT o.user_id, o.delivery_date, o.time, u.table_number, u.seat_number FROM orders o JOIN users u ON o.user_id = u.user_id WHERE o.order_id = %s", (order_id,))
    order_details = cur.fetchone()
    user_id, delivery_date, order_time, table_number, seat_number = order_details

    cur.execute("SELECT dish_name FROM order_dishes JOIN dishes ON order_dishes.dish_id = dishes.dish_id WHERE order_id = %s", (order_id,))
    dish_names = [row[0] for row in cur.fetchall()]

    message = f"Ваш заказ готов!\n\n" \
              f"Блюда: {', '.join(dish_names)}\n" \
              f"Время: {order_time}\n" \
              f"Дата: {delivery_date}\n" \
              f"Стол: {table_number}\n" \
              f"Место: {seat_number}\n" \
              f"Приходите к столу, чтобы забрать свой заказ."

    bot.send_message(user_id, message)

    cur.execute("DELETE FROM order_dishes WHERE order_id = %s", (order_id,))
    cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    conn.commit()

    admin_main_menu_buttons(call.message)

def cancelled_orders(message):
    cur.execute("SELECT order_id, user_id, delivery_date, time FROM orders WHERE status = 'отменен'")
    orders = cur.fetchall()
    if orders:
        for order in orders:
            order_id, user_id, delivery_date, time = order
            cur.execute("SELECT dish_id FROM order_dishes WHERE order_id = %s", (order_id,))
            dish_ids = cur.fetchall()
            dish_id_str = ', '.join(str(dish[0]) for dish in dish_ids)
            msg = f"ID заявки: {order_id}\nID клиента: {user_id}\nДата подачи: {delivery_date}\nВремя: {time}\nБлюдо: {dish_id_str}\n"
            keyboard = types.InlineKeyboardMarkup()
            delete_button = types.InlineKeyboardButton("Удалить", callback_data=f"delete_order__{order_id}")
            keyboard.add(delete_button)
            bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Отмененных заказов нет.")
        admin_main_menu_buttons(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_order__'))
def cancel_order_delete(call):
    order_id = int(call.data.split('_')[-1])
    cur.execute("SELECT user_id FROM orders WHERE order_id = %s", (order_id,))
    user_id = cur.fetchone()[0]
    cur.execute("DELETE FROM order_dishes WHERE order_id = %s", (order_id,))
    cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    conn.commit()
    bot.send_message(user_id, f"Ваш заказ с номером {order_id} был отменен.")
    bot.send_message(call.message.chat.id, f"Заказ с номером {order_id} был успешно отменен.")
    admin_main_menu_buttons(call.message)

def waiting_orders(message):
    cur.execute("SELECT orders.order_id, orders.user_id, string_agg(order_dishes.dish_id::text, ', '), orders.delivery_date, orders.time FROM orders JOIN order_dishes ON orders.order_id = order_dishes.order_id WHERE orders.status = 'ожидание' GROUP BY orders.order_id")
    orders = cur.fetchall()
    if orders:
        for order in orders:
            order_id, user_id, dish_ids, delivery_date, time = order
            msg = f"ID Заявки: {order_id}\nID клиента: {user_id}\nБлюдо: {dish_ids}\nДата подачи: {delivery_date}\nВремя: {time}\n"
            keyboard = types.InlineKeyboardMarkup()
            approve_button = types.InlineKeyboardButton("Одобрить", callback_data=f"approve_order__{order_id}")
            reject_button = types.InlineKeyboardButton("Отклонить", callback_data=f"reject_order__{order_id}")
            keyboard.add(approve_button, reject_button)
            bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Заказов в ожидании нет.")
        admin_main_menu_buttons(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_order__'))
def approve_order_callback(call):
    order_id = int(call.data.split('__')[-1])
    cur.execute("UPDATE orders SET status = 'активный' WHERE order_id = %s", (order_id,))
    conn.commit()
    cur.execute("SELECT user_id FROM orders WHERE order_id = %s", (order_id,))
    user_id = cur.fetchone()[0]
    bot.send_message(user_id, f"Ваш заказ с номером {order_id} был одобрен.")
    bot.send_message(call.message.chat.id, f"Заказ с номером {order_id} успешно одобрен.")
    admin_main_menu_buttons(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_order__'))
def reject_order_callback(call):
    order_id = int(call.data.split('__')[-1])
    cur.execute("SELECT user_id FROM orders WHERE order_id = %s", (order_id,))
    user_id = cur.fetchone()[0]
    bot.send_message(user_id, f"Ваш заказ с номером {order_id} был отклонен.")
    cur.execute("DELETE FROM order_dishes WHERE order_id = %s", (order_id,))
    cur.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    conn.commit()
    bot.send_message(call.message.chat.id, f"Заказ с номером {order_id} был отклонен.")
    admin_main_menu_buttons(call.message)

@bot.message_handler(func=lambda message: message.text == 'Назад')
def back_but(message):
    admin_main_menu_buttons(message)

def requests_list(message):
    if message.text == 'Просмотр заявок':
        cur.execute("SELECT user_id, full_name, departure_date, status FROM users WHERE status != 'активный'")
        requests = cur.fetchall()
        if requests:
            for req in requests:
                user_id, full_name, departure_date, status = req
                msg = f"ID клиента: {user_id}\nФИО: {full_name}\nДата выезда: {departure_date}\nСтатус: {status}\n"
                keyboard = types.InlineKeyboardMarkup()
                approve_button = types.InlineKeyboardButton(text="Одобрить", callback_data=f"approve_{user_id}")
                reject_button = types.InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{user_id}")
                keyboard.row(approve_button, reject_button)
                bot.send_message(message.chat.id, msg, reply_markup=keyboard)

            back_button = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            back_button.add(types.KeyboardButton("Назад"))
            bot.send_message(message.chat.id, "Для возврата к административной панели нажмите кнопку 'Назад'.",
                             reply_markup=back_button)
        else:
            bot.send_message(message.chat.id, "Заявок на рассмотрении нет.")
            admin_main_menu_buttons(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, воспользуйтесь кнопкой 'Просмотр заявок'.")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('approve_', 'reject_')))
def approve_and_reject(call):
    action, user_id = call.data.split('_')
    user_id = int(user_id)
    if action == "approve":
        approve_request(call.message, user_id)
    elif action == "reject":
        reject_request(call.message, user_id)

def approve_request(message, user_id):
    table_users_fn(message, user_id)

def reject_request(message, user_id):
    cancel_request(message, user_id)

def table_users_fn(message, user_id):
    cur.execute("SELECT table_number, seats_count, occupied_seats_count FROM tables WHERE occupied_seats_count < seats_count")
    tables = cur.fetchall()
    if tables:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for table in tables:
            table_number, seats_count, occupied_seats_count = table
            button_text = f"Стол {table_number} (свободно {seats_count - occupied_seats_count} мест)"
            keyboard.add(types.KeyboardButton(button_text))
        msg = bot.reply_to(message, "Выберите стол:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, seat_users_fn, user_id)
    else:
        bot.send_message(message.chat.id, "Извините, свободных столов нет.")
        admin_main_menu_buttons(message)

def seat_users_fn(message, user_id):
    table_text = message.text
    table_number = int(table_text.split()[1])
    cur.execute("SELECT occupied_seats_count FROM tables WHERE table_number = %s", (table_number,))
    occupied_seats_count = cur.fetchone()[0]
    cur.execute("UPDATE tables SET occupied_seats_count = %s WHERE table_number = %s", (occupied_seats_count + 1, table_number))
    cur.execute("UPDATE users SET table_number = %s, seat_number = %s, status = 'активный' WHERE user_id = %s",
                (table_number, occupied_seats_count + 1, user_id))
    conn.commit()
    bot.send_message(user_id, f"Ваша заявка на бронирование стола {table_number} и места {occupied_seats_count + 1} была одобрена.",
                     reply_markup=main_menu_user())
    bot.send_message(message.chat.id, f"Заявка пользователя с номером {user_id} была успешно одобрена. Стол {table_number}, место {occupied_seats_count + 1}.")
    admin_main_menu_buttons(message)

def cancel_request(message, user_id):
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    bot.send_message(message.chat.id, f"Заявка пользователя с номером {user_id} была успешно удалена.")
    admin_main_menu_buttons(message)

def admin_main_menu_buttons(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Просмотр заявок"), types.KeyboardButton("Просмотр заказов"), types.KeyboardButton("Пользователи"), types.KeyboardButton("Отчет"))
    msg = bot.reply_to(message, "Выберите действие:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, main_menu_admin)

bot.polling()