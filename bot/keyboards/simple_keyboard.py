from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(row_width=3, resize_keyboard=True).add(*row)