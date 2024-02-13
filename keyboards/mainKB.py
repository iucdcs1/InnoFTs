from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Попутчик'), KeyboardButton(text='Водитель')],
    [KeyboardButton(text='Статистика')]
], resize_keyboard=True, input_field_placeholder='Выберите один из пунктов меню')

main_kb_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Попутчик'), KeyboardButton(text='Водитель')],
    [KeyboardButton(text='Статистика')],
    [KeyboardButton(text='Админ-панель')]
], resize_keyboard=True, input_field_placeholder='Выберите один из пунктов меню')

passenger_main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Найти попутку'), KeyboardButton(text='Мои подписки')],
    [KeyboardButton(text='Вернуться')]
])

driver_main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Запланировать поездку'), KeyboardButton(text='Мои поездки')],
    [KeyboardButton(text='Вернуться')]
])

statistics_main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='А'), KeyboardButton(text='Б')],
    [KeyboardButton(text='Вернуться')]
])

admin_main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='А'), KeyboardButton(text='Б')],
    [KeyboardButton(text='Вернуться')]
])
