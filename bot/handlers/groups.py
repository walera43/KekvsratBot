import pathlib

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.phrases.phrases import APPEAL
from config import BOT_ID
from random2 import randint
from loader import groups_data

from .user import edit_this_photo


async def change_chance(message: types.Message):
    if message.chat.id != message.from_user.id:
        try:
            new_chance = int(message.text[15:])
        except ValueError:
            await message.answer('<b>Чтобы это не было, это не число!</b>\n'
                                 '<i>Попробуй еще раз.</i>')
            return
        if new_chance and 1 <= int(new_chance) <= 100:
            group_id = str(message.chat.id)
            if group_id not in groups_data:
                groups_data[group_id] = {'random_chance': new_chance}
                await message.answer('<b>Вы еще не отправляли сообщение,</b>'
                                     '<b>но да ладно!</b>\n'
                                     '<i>Шанс моего ответа = </i>'
                                     f'<b><i>{new_chance}%</b></i>')
            elif group_id in groups_data:
                groups_data[group_id]['random_chance'] = new_chance
                await message.answer('<b>Вероятность моего ответа изменилась!</b>\n'
                                     '<i>Шанс моего ответа = </i>'
                                     f'<i><b>{new_chance}%</b></i>')
        else:
            await message.answer('<b>Похоже, вы забыли число!\n</b>'
                                 '<i>После команды напиши число от 1 до 100</i>')


async def reply_to_photo(message: types.Message):
    if message.reply_to_message.photo:
        await message.answer('Отправляю фотографию на мемезацию!')
        photo_from_user = await message.reply_to_message.photo[3].get_file()
        photo_to_send = await edit_this_photo(photo_from_user)
        await message.answer_photo(open(photo_to_send, mode='rb'))
        pathlib.Path(photo_to_send).unlink()  # удаляем обработанную фотографию.


async def react_to_photo(message: types.Message):
    '''Функция, где бот отвечает на фотографии с определенным шансом'''
    if message.chat.id != message.from_user.id:
        group_id = str(message.chat.id)
        if group_id not in groups_data:
            groups_data[group_id] = {'random_chance': 20}
            await message.answer('Поздравляю это первая фотография со мной!\n'
                                 '<b>Шанс моего ответа = </b>'
                                 f'<b><i>{groups_data[group_id]["random_chance"]} %</i></b>')
        if group_id in groups_data:
            chance_to_react = int(groups_data[group_id]["random_chance"])
            chance = randint(1, 100)
            if chance_to_react >= chance:
                photo_from_user = await message.photo[3].get_file()
                photo_to_send = await edit_this_photo(photo_from_user)
                await message.answer_photo(open(photo_to_send, mode='rb'))
                pathlib.Path(photo_to_send).unlink()


def group_handlers_register(dp: Dispatcher):
    dp.register_message_handler(reply_to_photo, Text(APPEAL, ignore_case=True))
    dp.register_message_handler(react_to_photo, content_types=['photo'])
    dp.register_message_handler(change_chance, commands=['setrandomkeka'])
