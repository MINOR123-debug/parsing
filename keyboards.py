from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)

# Клавіатура з кнопкою для пошуку
search_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пошук 🔍", switch_inline_query_current_chat="")],
])

bay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пошук 🔍", switch_inline_query_current_chat="")],
])


admin_panel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🌟Активність🌟'),
                                      KeyboardButton(text='🌟Зробити росилку🌟')],
                                      [KeyboardButton(text='⏰Тех-перерва⏰'),
                                       KeyboardButton(text='👥Користувачі👥')
                                    ]],
                        resize_keyboard=True,
                        input_field_placeholder='Виберете пункт в меню...')


vip = InlineKeyboardMarkup(inline_keyboard=[[
InlineKeyboardButton(text='Назад⚡️', callback_data='vip1')]])


admin_info = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Користувачі id'),
                                      KeyboardButton(text='Admin info')],
                                      [KeyboardButton(text='⚡️Назад⚡️')]])