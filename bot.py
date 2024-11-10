import telebot
import psycopg2
import time
import datetime
import re
from datetime import datetime, timedelta, date
from telebot import types

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="testbot",
    user="postgres",
    password="11111111",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Инициализация бота
bot = telebot.TeleBot('7230290156:AAFdcfLaf3vKkZkUqThr-IH8Y1RegQ4ebXA')

month_names = {
    1: 'Января',
    2: 'Февраля',
    3: 'Марта',
    4: 'Апреля',
    5: 'Мая',
    6: 'Июня',
    7: 'Июля',
    8: 'Августа',
    9: 'Сентября',
    10: 'Октября',
    11: 'Ноября',
    12: 'Декабря'
}


# ГЛАВНОЕ МЕНЮ
def main_menu(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton("Записать на процедуру", callback_data='type_procedures')
    button2 = types.InlineKeyboardButton("Информация о процедурах", callback_data='info_procedures')
    button3 = types.InlineKeyboardButton("Управление записями", callback_data='manage_appointments')
    markup.add(button1, button2, button3)

    bot.send_photo(
        chat_id,
        open(r'C:\Users\troya\OneDrive\Рабочий стол\ПРОЕКТ КОСМЕТОЛОГИЯ\КАРТИНКА.jpg', 'rb'),
        caption="\U0001F3E0 Главное меню",
        parse_mode="Markdown",
        reply_markup=markup
    )


def main_menu_new(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton("Записать на процедуру", callback_data='type_procedures')
    button2 = types.InlineKeyboardButton("Информация о процедурах", callback_data='info_procedures')
    button3 = types.InlineKeyboardButton("Управление записями", callback_data='manage_appointments')
    markup.add(button1, button2, button3)
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="\U0001F3E0 Главное меню",
        parse_mode="Markdown",
        reply_markup=markup
    )


# ЗАПИСЬ
# ТИПЫ ПРОЦЕДУР
def type_procedures(call):
    cursor = conn.cursor()
    type_procedures = f"""
        SELECT id_group, name_group FROM public.groups_services 
        ORDER BY id_group ASC
    """
    cursor.execute(type_procedures)
    groups_services = cursor.fetchall()
    cursor.close()

    buttons = [types.InlineKeyboardButton(group[1], callback_data=f'group_{group[0]}') for group in groups_services]
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад", callback_data='back_home')
    markup = types.InlineKeyboardMarkup()
    for button in buttons:
        markup.add(button)
    markup.row(button1, button2)

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="*Запись*\nВыберете тип процедуры",
        parse_mode="Markdown",
        reply_markup=markup
    )

    # СПИСОК ПРОЦЕДУР
def list_procedures(call, group_id):
    cursor = conn.cursor()
    type_procedures = f"""
        SELECT id_service, name_service FROM public.services 
        WHERE group_id = {group_id}
        ORDER BY id_service ASC
    """
    cursor.execute(type_procedures)
    services = cursor.fetchall()
    cursor.close()

    buttons = [types.InlineKeyboardButton(service[1], callback_data=f'service_{service[0]}_group_{group_id}') for
               service in services]
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад", callback_data='back_type_procedures')
    markup = types.InlineKeyboardMarkup()
    for button in buttons:
        markup.add(button)
    markup.row(button1, button2)

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="*Запись*\nВыберете интересующую вас процедуру",
        parse_mode="Markdown",
        reply_markup=markup
    )


    # ВЫБОР ДАТЫ ПРОЦЕДУРЫ
def reg_procedure(call, service_id, group_id, back):
    cursor = conn.cursor()
    services = f"""
        SELECT id_service, duration, name_service, price 
        FROM public.services 
        WHERE id_service = {service_id}
    """
    dates = f"""
        SELECT calendar_date FROM public.calendar
        where id_master >= 0 AND calendar_date >= CURRENT_DATE
        ORDER BY calendar_date ASC
        LIMIT 14;
    """
    cursor.execute(services)
    services = cursor.fetchall()
    cursor.execute(dates)
    dates = cursor.fetchall()
    cursor.close()
    service = services[0]
    buttons = [
        types.InlineKeyboardButton(
            f"{date[0].strftime('%d')} {month_names[date[0].month]}",  # День и название месяца
            callback_data=f'selected_date_{date[0]}_{group_id}_{service_id}'
        ) for date in dates
    ]
    #button0 = types.InlineKeyboardButton("Добавить процедуру", callback_data='add_procedure')
    button01 = types.InlineKeyboardButton("Информация о процедуре", callback_data=f'info1_procedure_{service_id}_{group_id}')
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    if back == "Запись":
        button2 = types.InlineKeyboardButton("\u21A9 Назад", callback_data=f'back_list_procedures_{group_id}')
    else:
        button2 = types.InlineKeyboardButton("\u21A9 Назад", callback_data=f'info2_procedure_{service[0]}_{group_id}')
    markup = types.InlineKeyboardMarkup()
    #markup.add(button0)
    markup.add(button01)
    for i in range(0, len(buttons), 2):
        row_buttons = buttons[i:i + 2]
        markup.row(*row_buttons)
    markup.row(button1, button2)

    total_minutes = service[1].total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"

    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n\n"
        f"Выберете удобную вам дату:"
    )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )


def info1_procedure(call, group_id, service_id):
    cursor = conn.cursor()

    services_query = f"""
        SELECT id_service, duration, name_service, price, info_services
        FROM public.services 
        WHERE id_service = {service_id}
    """
    cursor.execute(services_query)
    services = cursor.fetchall()
    service = services[0]
    button0 = types.InlineKeyboardButton("Продолжить запись",
                                         callback_data=f'back_reg_procedure_group_id_{group_id}_service_id_{service_id}')
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад",
                                         callback_data=f'back_reg_procedure_group_id_{group_id}_service_id_{service_id}')
    markup = types.InlineKeyboardMarkup()
    markup.add(button0)
    markup.row(button1, button2)

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"
    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n\n"
        f"{service[4]}"

    )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )
    # ВЫБОР ВРЕМЕНИ
def time_selection(call, selected_date, group_id, service_id):
    cursor = conn.cursor()

    services_query = f"""
        SELECT id_service, duration, name_service, price 
        FROM public.services 
        WHERE id_service = {service_id}
    """
    open_time_query = f"""
        SELECT open_time 
        FROM public.studios
        WHERE id_studio = 1
    """
    closing_time_query = f"""
        SELECT closing_time
        FROM public.studios
        WHERE id_studio = 1
    """
    appointment_query = f"""
        SELECT start_time, end_time
        FROM public.appointment
        WHERE appointment_date = '{selected_date}'
    """
    tg_id = str(call.from_user.id)
    check_tg_query = f"""
        SELECT id_client
        FROM clients
        WHERE tg_id = '{tg_id}'
    """

    # Выполнение запросов и получение данных
    cursor.execute(services_query)
    services = cursor.fetchall()
    cursor.execute(open_time_query)
    open_time = cursor.fetchall()[0][0]
    cursor.execute(closing_time_query)
    closing_time = cursor.fetchall()[0][0]
    cursor.execute(appointment_query)
    appointments = cursor.fetchall()
    cursor.execute(check_tg_query)
    check_tg = cursor.fetchall()
    cursor.close()

    service = services[0]
    service_duration = service[1]

    now = datetime.now()
    rounded_minutes = (now.minute // 15 + 1) * 15
    now_time = (now + timedelta(minutes=(rounded_minutes - now.minute))).time()
    now_time_plus_15 = (
            datetime.combine(date.today(), now_time) + timedelta(minutes=15)
    ).time()

    # Преобразование временных интервалов в удобный формат
    busy_times = [(start, end) for start, end in appointments]

    def is_time_in_busy_intervals(current_time, service_duration):
        end_time = (datetime.combine(date.today(), current_time) + service_duration).time()
        for start, end in busy_times:
            if start <= current_time < end or start < end_time <= end or (current_time <= start and end_time >= end):
                return True
        return False

    def generate_time_buttons(now_time, check_tg):
        buttons = []

        if selected_date == date.today().strftime('%Y-%m-%d'):
            current_time = datetime.combine(date.today(), now_time_plus_15)
        else:
            current_time = datetime.combine(date.today(), open_time)

        end_time = datetime.combine(date.today(), closing_time)

        while current_time.time() < end_time.time():
            if not is_time_in_busy_intervals(current_time.time(), service_duration):
                next_end_time = current_time + service_duration
                if next_end_time.time() <= end_time.time():

                    if check_tg:
                        user_id = check_tg
                        button = types.InlineKeyboardButton(
                            current_time.strftime('%H:%M'),
                            callback_data=f"tgtrue_{user_id[0][0]}_{current_time.strftime('%H:%M')}_{selected_date}_{group_id}_{service_id}"
                        )
                        buttons.append(button)
                    else:
                        button = types.InlineKeyboardButton(
                            current_time.strftime('%H:%M'),
                            callback_data=f"current_time_{current_time.strftime('%H:%M')}_{selected_date}_{group_id}_{service_id}"
                        )
                        buttons.append(button)
            current_time += timedelta(minutes=15)

        return buttons

    # Генерация кнопок времени
    buttons = generate_time_buttons(now_time_plus_15, check_tg)
    keyboard = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
    markup = types.InlineKeyboardMarkup(keyboard)

    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад",
                                         callback_data=f'back_reg_procedure_group_id_{group_id}_service_id_{service_id}')
    markup.row(button1, button2)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    total_minutes = service_duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"

    if buttons:
        caption = (
            f"*Запись*\n"
            f"Процедура: *{service[2]}*\n"
            f"Продолжительность: *{duration_str}*\n"
            f"Цена: *{service[3]}*р\n"
            f"Дата: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]}*\n\n"
            f"Выберете удобное вам время:"
        )
    else:
        caption = (
            f"*Запись*\n"
            f"Процедура: *{service[2]}*\n"
            f"Продолжительность: *{duration_str}*\n"
            f"Цена: *{service[3]}*р\n"
            f"Дата: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]}*\n\n"
            f"*На выбранную дату нет свободных окон*"
        )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )


# ВВОД ИМЕНИ
def name_user(call, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()
    services_query = f"""
        SELECT id_service, duration, name_service, price 
        FROM public.services 
        WHERE id_service = {service_id}
    """

    cursor.execute(services_query)
    services = cursor.fetchall()
    cursor.close()

    if not services:
        # Обработка случая, если нет данных по запросу
        return

    service = services[0]

    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад",
                                         callback_data=f'back_time_selection_{selected_date}_{group_id}_{service_id}')
    markup = types.InlineKeyboardMarkup()
    markup.row(button1, button2)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"
    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n"
        f"Дата и время: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time}*\n\n"
        f"Введите имя:"
    )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )
    back = False
    # Устанавливаем следующий шаг обработки - ввод имени пользователя
    bot.register_next_step_handler(call.message, process_name_step, call, back, selected_time, selected_date, group_id,
                                   service_id)


def process_name_step(message, call, back, selected_time, selected_date, group_id, service_id):
    # Оставляем только буквы и обрезаем до 20 символов
    user_name = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', message.text)[:20].capitalize()
    phone_number_f(call, back, user_name, selected_time, selected_date, group_id, service_id)


def phone_number_f(call, back, user_name, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()
    services = f"""
            SELECT id_service, duration, name_service, price 
            FROM public.services 
            WHERE id_service = {service_id}
        """

    cursor.execute(services)
    service = cursor.fetchone()
    cursor.close()

    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад",
                                         callback_data=f'back_name_user_{selected_time}_{selected_date}_{group_id}_{service_id}')
    markup = types.InlineKeyboardMarkup()
    markup.row(button1, button2)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"

    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n"
        f"Дата и время: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time}*\n"
        f"Ваше имя:  *{user_name}*\n"
        f"Введите номер телефона"
    )

    if not back:
        # Отправляем сообщение с фотографией и подписью
        photo_message = bot.send_photo(
            call.message.chat.id,
            open(r'C:\Users\troya\OneDrive\Рабочий стол\ПРОЕКТ КОСМЕТОЛОГИЯ\КАРТИНКА.jpg', 'rb'),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=markup
        )
        photo_message_id = photo_message.message_id
        # Удаляем старое сообщение с фотографией
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=markup
        )
        photo_message_id = call.message.message_id
        # Регистрируем следующий шаг обработки - ввод номера телефона
    bot.register_next_step_handler(call.message, process_phone_number_step, call, back, photo_message_id, user_name,
                                   selected_time, selected_date,
                                   group_id, service_id)


def process_phone_number_step(message, call, back, photo_message_id, user_name, selected_time, selected_date, group_id,
                              service_id):
    phone_number = message.text
    phone_number = re.sub(r'\D', '', phone_number)

    if len(phone_number) == 11:
        phone_number = '8' + phone_number[1:]  # заменяем первый символ на 8
        appointment(call, photo_message_id, phone_number, user_name, selected_time, selected_date, group_id, service_id)
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат номера телефона. Пример: 89991112233"
        )
        # Ожидаем следующее сообщение от пользователя для ввода корректного номера
        bot.register_next_step_handler(message,
                                       lambda msg: process_phone_number_step(msg, call, back, photo_message_id,
                                                                             user_name,
                                                                             selected_time, selected_date, group_id,
                                                                             service_id))


def appointment(call, photo_message_id, phone_number, user_name, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()

    # Получение данных об услуге
    services_query = """
        SELECT id_service, duration, name_service, price 
        FROM public.services 
        WHERE id_service = %s
    """
    cursor.execute(services_query, (service_id,))
    service = cursor.fetchone()

    # Извлечение tg_id из объекта call
    tg_id = str(call.from_user.id)  # Преобразуем id в строку, если он еще не строка

    # Вставка или обновление клиента
    user_in_query = """
        INSERT INTO clients (phone_number, name_client, tg_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone_number) 
        DO UPDATE SET tg_id = EXCLUDED.tg_id
        RETURNING id_client;
    """
    cursor.execute(user_in_query, (phone_number, user_name, tg_id))  # Используем tg_id как строку
    user_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()

    button0 = types.InlineKeyboardButton("ЗАПИСАТЬСЯ",
                                         callback_data=f'save_appointment_{user_id}_{selected_time}_{selected_date}_{group_id}_{service_id}')
    button1 = types.InlineKeyboardButton("Добавить комментарий",
                                         callback_data=f'comment1_{user_id}_{selected_time}_{selected_date}_{group_id}_{service_id}')
    button2 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    if photo_message_id == "NaN":
        button3 = types.InlineKeyboardButton("\u21A9 Назад",
                                             callback_data=f'back_time_selection_{selected_date}_{group_id}_{service_id}')
    else:
        button3 = types.InlineKeyboardButton("\u21A9 Назад",
                                             callback_data=f'back_phone_number_{user_name}_{selected_time}_{selected_date}_{group_id}_{service_id}')
    markup = types.InlineKeyboardMarkup()
    markup.add(button0)
    markup.add(button1)
    markup.row(button2, button3)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"
    phone_number = '+7' + phone_number[1:]
    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n"
        f"Дата и время: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time}*\n"
        f"Ваше имя:  *{user_name}*\n"
        f"Номер телефона:  *{phone_number}*\n" 
        f"""Комментарий:  _"отсутствует"_\n\n"""
        f"""\u26A0 *Не забудьте нажать кнопку "ЗАПИСАТЬСЯ"*"""
    )
    if photo_message_id == "NaN":
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        # Отправляем сообщение с фотографией и подписью
        bot.send_photo(
            call.message.chat.id,
            open(r'C:\Users\troya\OneDrive\Рабочий стол\ПРОЕКТ КОСМЕТОЛОГИЯ\КАРТИНКА.jpg', 'rb'),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=markup
        )

        # Удаляем старое сообщение с фотографией
        bot.delete_message(chat_id=call.message.chat.id, message_id=photo_message_id)


def save_save_appointment(call, user_id, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()
    # Запрос на получение продолжительности и имени услуги
    services_query = """
        SELECT duration, name_service
        FROM public.services 
        WHERE id_service = %s
    """

    # Запрос на получение имени клиента
    user_name_query = """
        SELECT name_client 
        FROM clients 
        WHERE id_client = %s
    """

    # Запрос на вставку данных в таблицу appointment
    insert_query = """
        INSERT INTO appointment (
            appointment_date,
            start_time,
            end_time,
            id_service,
            id_client,
            active,
            confirmation
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # Выполнение запроса на получение данных услуги
    cursor.execute(services_query, (service_id,))
    service = cursor.fetchone()

    # Преобразование времени начала и продолжительности
    start_time = datetime.strptime(selected_time, "%H:%M")
    duration = service[0]  # duration это timedelta

    # Рассчитываем время окончания
    end_time = start_time + duration
    end_time_str = end_time.strftime("%H:%M")

    # Данные для вставки
    data_to_insert = (
        selected_date,  # appointment_date
        selected_time,  # start_time
        end_time_str,  # end_time
        service_id,  # id_service
        user_id,  # id_client
        True,  # active
        False  # confirmation
    )

    # Выполнение вставки
    cursor.execute(insert_query, data_to_insert)
    conn.commit()

    # Выполнение запроса на получение имени клиента
    cursor.execute(user_name_query, (user_id,))
    user_name = cursor.fetchone()[0]

    cursor.close()

    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    markup = types.InlineKeyboardMarkup()
    markup.row(button1)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    caption = (
        f"{user_name}, ваша запись *сохранена*\n"
        f"Ждём вас {datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time} на процедуру {service[1]}\n"
    )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )


def comment(call, user_id, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()
    # Запрос на получение продолжительности и имени услуги
    services_query = f"""
        SELECT id_service, duration, name_service, price 
        FROM public.services 
        WHERE id_service = %s
    """

    # Запрос на получение имени клиента
    user_name_phone_number = """
           SELECT name_client, phone_number
           FROM clients 
           WHERE id_client = %s
       """
    # Выполнение запроса на получение данных услуги
    cursor.execute(services_query, (service_id,))
    service = cursor.fetchone()
    # Выполнение запроса на получение имени клиента
    cursor.execute(user_name_phone_number, (user_id,))
    user_name_phone_number = cursor.fetchone()
    cursor.close()

    user_name = user_name_phone_number[0]
    phone_number = user_name_phone_number[1]

    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад",
                                         callback_data=f'back_save_save_{user_id}_{selected_time}_{selected_date}_{group_id}_{service_id}')
    markup = types.InlineKeyboardMarkup()
    markup.row(button1, button2)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"
    phone_number = '+7' + phone_number[1:]
    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n"
        f"Дата и время: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time}*\n"
        f"Ваше имя:  *{user_name}*\n"
        f"Номер телефона:  *{phone_number}*\n\n" 
        f"""*Введите комментарий*"""
    )
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.register_next_step_handler(call.message, process_comment_step, call, user_id,
                                   selected_time, selected_date, group_id, service_id)


def process_comment_step(message, call, user_id,
                         selected_time, selected_date, group_id, service_id):
    comment = message.text[:300]
    comment_appointment(call, comment, user_id, selected_time, selected_date, group_id, service_id)

def comment_appointment(call, comment, user_id, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()
    # Получение данных об услуге
    services_query = """
            SELECT id_service, duration, name_service, price 
            FROM public.services 
            WHERE id_service = %s
        """
    # Запрос на получение имени клиента
    user_name_phone_number = """
               SELECT name_client, phone_number
               FROM clients 
               WHERE id_client = %s
           """
    # Выполнение запроса на получение данных услуги
    cursor.execute(services_query, (service_id,))
    service = cursor.fetchone()
    # Выполнение запроса на получение имени клиента
    cursor.execute(user_name_phone_number, (user_id,))
    user_name_phone_number = cursor.fetchone()

    comment_in = """
        INSERT INTO comments (comment) 
        VALUES (%s) RETURNING id_comment;
    """
    cursor.execute(comment_in, (comment,))
    comment_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    user_name = user_name_phone_number[0]
    phone_number = user_name_phone_number[1]

    button0 = types.InlineKeyboardButton("ЗАПИСАТЬСЯ",
                                         callback_data=f'savecom_appointment_{comment_id}_{user_id}_{selected_time}_{selected_date}_{group_id}_{service_id}')
    button2 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')

    button3 = types.InlineKeyboardButton("\u21A9 Назад",
                                             callback_data=f'back_comment_{user_id}_{selected_time}_{selected_date}_{group_id}_{service_id}')
    markup = types.InlineKeyboardMarkup()
    markup.add(button0)
    markup.row(button2, button3)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"
    phone_number = '+7' + phone_number[1:]
    caption = (
        f"*Запись*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n"
        f"Дата и время: *{datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time}*\n"
        f"Ваше имя:  *{user_name}*\n"
        f"Номер телефона:  *{phone_number}*\n"
        f"""Комментарий:  _"{comment}"_\n\n"""
        f"""\u26A0 *Не забудьте нажать кнопку "ЗАПИСАТЬСЯ"*"""
    )

    bot.send_photo(
        call.message.chat.id,
        open(r'C:\Users\troya\OneDrive\Рабочий стол\ПРОЕКТ КОСМЕТОЛОГИЯ\КАРТИНКА.jpg', 'rb'),
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )

    # Удаляем старое сообщение с фотографией
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


def save_comment_appointment(call, comment_id, user_id, selected_time, selected_date, group_id, service_id):
    cursor = conn.cursor()
    comment = """
        SELECT comment 
        FROM comments 
        WHERE id_comment = %s
    """
    # Запрос на получение продолжительности и имени услуги
    services_query = """
        SELECT duration, name_service
        FROM public.services 
        WHERE id_service = %s
    """

    # Запрос на получение имени клиента
    user_name_query = """
        SELECT name_client 
        FROM clients 
        WHERE id_client = %s
    """

    # Запрос на вставку данных в таблицу appointment
    insert_query = """
        INSERT INTO appointment (
            appointment_date,
            start_time,
            end_time,
            id_service,
            id_client,
            active,
            confirmation,
            comment_client
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(comment, (comment_id,))
    comment = cursor.fetchone()[0]

    # Выполнение запроса на получение данных услуги
    cursor.execute(services_query, (service_id,))
    service = cursor.fetchone()

    # Преобразование времени начала и продолжительности
    start_time = datetime.strptime(selected_time, "%H:%M")
    duration = service[0]  # duration это timedelta

    # Рассчитываем время окончания
    end_time = start_time + duration
    end_time_str = end_time.strftime("%H:%M")

    # Данные для вставки
    data_to_insert = (
        selected_date,  # appointment_date
        selected_time,  # start_time
        end_time_str,  # end_time
        service_id,  # id_service
        user_id,  # id_client
        True,  # active
        False,  # confirmation
        comment
    )

    # Выполнение вставки
    cursor.execute(insert_query, data_to_insert)
    conn.commit()

    # Выполнение запроса на получение имени клиента
    cursor.execute(user_name_query, (user_id,))
    user_name = cursor.fetchone()[0]

    cursor.close()

    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    markup = types.InlineKeyboardMarkup()
    markup.row(button1)

    datetime_obj = datetime.strptime(selected_date, '%Y-%m-%d')

    caption = (
        f"{user_name}, ваша запись *сохранена*\n"
        f"Ждём вас {datetime_obj.strftime('%d')} {month_names[datetime_obj.month]} к {selected_time} на процедуру {service[1]}\n"
    )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )


# ИНФОРМАЦИЯ
def info_type(call):
    cursor = conn.cursor()
    type_procedures = f"""
        SELECT id_group, name_group FROM public.groups_services 
        ORDER BY id_group ASC
    """
    cursor.execute(type_procedures)
    groups_services = cursor.fetchall()
    cursor.close()

    buttons = [types.InlineKeyboardButton(group[1], callback_data=f'gr_info_{group[0]}') for group in groups_services]
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад", callback_data='back_home')
    markup = types.InlineKeyboardMarkup()
    for button in buttons:
        markup.add(button)
    markup.row(button1, button2)

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="*Информация*\nВыберете тип процедуры",
        parse_mode="Markdown",
        reply_markup=markup
    )

    # СПИСОК ПРОЦЕДУР
def list_info_procedures(call, group_id):
    cursor = conn.cursor()
    type_procedures = f"""
        SELECT id_service, name_service FROM public.services 
        WHERE group_id = {group_id}
        ORDER BY id_service ASC
    """
    cursor.execute(type_procedures)
    services = cursor.fetchall()
    cursor.close()
    buttons = [types.InlineKeyboardButton(service[1], callback_data=f'info2_procedure_{service[0]}_{group_id}') for
               service in services]
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад", callback_data='back_type_info_procedures')
    markup = types.InlineKeyboardMarkup()
    for button in buttons:
        markup.add(button)
    markup.row(button1, button2)

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="*Информация*\nВыберете интересующую вас процедуру",
        parse_mode="Markdown",
        reply_markup=markup
    )

def info2_procedure(call, group_id, service_id):
    cursor = conn.cursor()

    services_query = f"""
        SELECT id_service, duration, name_service, price, info_services
        FROM public.services 
        WHERE id_service = {service_id}
    """
    cursor.execute(services_query)
    services = cursor.fetchall()
    service = services[0]
    button0 = types.InlineKeyboardButton("Записаться",
                                         callback_data=f'reg_info_procedure_{group_id}_{service[0]}')
    button1 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')
    button2 = types.InlineKeyboardButton("\u21A9 Назад",
                                         callback_data=f'back_list_info_{group_id}')
    markup = types.InlineKeyboardMarkup()
    markup.add(button0)
    markup.row(button1, button2)

    # Предполагается, что duration это timedelta
    duration = service[1]
    total_minutes = duration.total_seconds() // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        duration_str = f"{int(hours)}ч {int(minutes)}мин"
    elif hours > 0:
        duration_str = f"{int(hours)}ч"
    elif minutes > 0:
        duration_str = f"{int(minutes)}мин"
    caption = (
        f"*Информация*\n"
        f"Процедура: *{service[2]}*\n"
        f"Продолжительность: *{duration_str}*\n"
        f"Цена: *{service[3]}*р\n\n"
        f"{service[4]}"

    )
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )

# МОИ ЗАПИСИ
def handle_manage_appointments(call):
    button1 = types.InlineKeyboardButton("\u2734 Активные", callback_data='back_home')
    button2 = types.InlineKeyboardButton("\U0001F4DC История", callback_data='home')
    button3 = types.InlineKeyboardButton("\u21A9 Назад", callback_data='back_home')
    button4 = types.InlineKeyboardButton("\U0001F3E0 Главная", callback_data='home')

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button1, button2)
    keyboard.add(button3, button4)

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="Активные или история?",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# Обработчик для inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Кнопки на главной
    if call.data == 'type_procedures':
        type_procedures(call)
    elif call.data == 'info_procedures':
        info_type(call)
    elif call.data == 'manage_appointments':
        handle_manage_appointments(call)
    # Кнопка возвращения на главную
    elif call.data == 'home':
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        main_menu_new(call)

    # Кнопки 1-го уровня записи
    elif call.data == 'back_home':
        main_menu_new(call)
    elif call.data.startswith('group_'):
        group_id = call.data.split('_')[1]
        list_procedures(call, group_id)
    elif call.data.startswith('gr_info'):
        group_id = call.data.split('_')[2]
        list_info_procedures(call, group_id)
    # Кнопки 2-го уровня записи
    elif call.data == 'back_type_procedures':
        type_procedures(call)
    elif call.data == 'back_type_info_procedures':
        info_type(call)
    elif call.data.startswith('service_'):
        data = call.data.split('_')
        service_id = data[1]
        group_id = data[3]
        back = "Запись"
        reg_procedure(call, service_id, group_id, back)

    # Кнопки 3-го уровня записи
    elif 'back_list_procedures' in call.data:
        data = call.data.split('_')
        group_id = data[3]
        list_procedures(call, group_id)
    elif 'info1_procedure' in call.data:
        data = call.data.split('_')
        group_id = data[3]
        service_id = data[2]
        info1_procedure(call, group_id, service_id)
    elif 'info2_procedure' in call.data:
        data = call.data.split('_')
        group_id = data[3]
        service_id = data[2]
        info2_procedure(call, group_id, service_id)
    elif 'selected_date' in call.data:
        data = call.data.split('_')
        selected_date = data[2]
        group_id = data[3]
        service_id = data[4]
        time_selection(call, selected_date, group_id, service_id)

    elif 'reg_info_procedure' in call.data:
        data = call.data.split('_')
        group_id = data[3]
        service_id = data[4]
        back = "Информация"
        reg_procedure(call, service_id, group_id, back)
    elif 'back_list_info' in call.data:
        data = call.data.split('_')
        group_id = data[3]
        list_info_procedures(call, group_id)

    # Кнопки 4-го уровня записи
    elif 'back_reg_procedure' in call.data:
        data = call.data.split('_')
        service_id = data[8]
        group_id = data[5]
        back = "Запись"
        reg_procedure(call, service_id, group_id, back)
    elif 'current_time' in call.data:
        data = call.data.split('_')
        service_id = data[5]
        group_id = data[4]
        selected_time = data[2]
        selected_date = data[3]
        name_user(call, selected_time, selected_date, group_id, service_id)
    elif 'tgtrue' in call.data:
        data = call.data.split('_')
        cursor = conn.cursor()
        name_number = f"""
            SELECT phone_number, name_client 
            FROM clients 
            WHERE id_client = {data[1]}
        """
        cursor.execute(name_number)
        name_number = cursor.fetchone()
        cursor.close()
        service_id = data[5]
        group_id = data[4]
        selected_time = data[2]
        selected_date = data[3]
        user_name = name_number[1]
        phone_number = name_number[0]
        photo_message_id = "NaN"
        appointment(call, photo_message_id, phone_number, user_name, selected_time, selected_date,
                    group_id, service_id)

    # Кнопки 5-го уровня записи
    elif 'back_time_selection' in call.data:
        data = call.data.split('_')
        service_id = data[5]
        group_id = data[4]
        selected_date = data[3]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        time_selection(call, selected_date, group_id, service_id)

    # Кнопки 6-го уровня записи
    elif 'back_name_user' in call.data:
        data = call.data.split('_')
        service_id = data[6]
        group_id = data[5]
        selected_time = data[3]
        selected_date = data[4]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        name_user(call, selected_time, selected_date, group_id, service_id)

    # Кнопки 7-го уровня записи
    elif 'back_phone_number' in call.data:
        data = call.data.split('_')
        service_id = data[7]
        group_id = data[6]
        selected_date = data[5]
        selected_time = data[4]
        user_name = data[3]
        back = data[0]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        phone_number_f(call, back, user_name, selected_time, selected_date, group_id, service_id)

    elif 'save_appointment' in call.data:
        data = call.data.split('_')
        service_id = data[6]
        group_id = data[5]
        selected_date = data[4]
        selected_time = data[3]
        user_id = data[2]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        save_save_appointment(call, user_id, selected_time, selected_date, group_id, service_id)

    elif 'comment1' in call.data:
        data = call.data.split('_')
        service_id = data[5]
        group_id = data[4]
        selected_date = data[3]
        selected_time = data[2]
        user_id = data[1]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        comment(call, user_id, selected_time, selected_date, group_id, service_id)

    # Кнопки 8-го уровня записи
    elif 'back_save_save' in call.data:
        data = call.data.split('_')
        cursor = conn.cursor()
        name_number = f"""
                   SELECT phone_number, name_client 
                   FROM clients 
                   WHERE id_client = {data[3]}
               """
        cursor.execute(name_number)
        name_number = cursor.fetchone()
        cursor.close()
        service_id = data[7]
        group_id = data[6]
        selected_date = data[5]
        selected_time = data[4]
        user_name = name_number[1]
        phone_number = name_number[0]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        photo_message_id = "NaN"
        appointment(call, photo_message_id, phone_number, user_name, selected_time, selected_date, group_id, service_id)

    # Кнопки 9-го уровня записи
    elif 'back_comment' in call.data:
        data = call.data.split('_')
        service_id = data[6]
        group_id = data[5]
        selected_date = data[4]
        selected_time = data[3]
        user_id = data[2]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        comment(call, user_id, selected_time, selected_date, group_id, service_id)
    elif 'savecom_appointment' in call.data:
        data = call.data.split('_')
        service_id = data[7]
        group_id = data[6]
        selected_date = data[5]
        selected_time = data[4]
        user_id = data[3]
        comment_id = data[2]
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        save_comment_appointment(call, comment_id, user_id, selected_time, selected_date, group_id, service_id)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.from_user.id,
        "Привет, я бот-помощник студии *AriTBeauty*, вот с чем я могу помочь:\n\n\u270E Записать на "
        "процедуру\n\n\u2139 Рассказать про процедуру\n\n\U0001F4DD Помогу с управлением записями ",
        parse_mode="Markdown")
    time.sleep(0.1)
    main_menu(message)


# Запуск бота
bot.polling(none_stop=True)
