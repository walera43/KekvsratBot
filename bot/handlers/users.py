import pathlib
from uuid import uuid4

import aiofiles
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func
from sqlalchemy import select
from PIL import Image, ImageDraw, ImageFont
from random2 import choice
from db import async_session

from bot.keyboards.simple_keyboard import make_row_keyboard
from bot.phrases.collection import BEGGER_MODE, MEMES
from bot.phrases.phrases import APPEAL, start_message
from bot.models.photos import Photo

available_action = ['Создать свой мем', 'Поддержать', 'Чат с разработчиком', 'Режим оценки',
                    'Зачем этот бот?']
available_action_rating = ['Получить мем', 'Рейтинг', 'Назад в меню']


class ChatInPrivate(StatesGroup):
    actions_action = State()


class MakeMemeState(StatesGroup):
    make_meme_send_photo_action = State()
    make_meme_send_text_action = State()


async def start_comand(message: types.Message):
    if message.from_id == message.chat.id:
        await message.answer(text=start_message, reply_markup=make_row_keyboard(available_action))
        await ChatInPrivate.actions_action.set()
    elif message.from_id != message.chat.id:
        await message.answer(text=start_message)


async def trash_talk(message: types.Message):
    if message.from_id == message.chat.id:
        await message.answer('Отправь фотографию!', reply_markup=make_row_keyboard(available_action))


async def actions(message: types.Message):
    '''Навигация по действиям. Раздает дальнейшие state'''
    if message.text.lower() == 'создать свой мем':
        await message.answer('Окей, отправь фотографию!')
        await MakeMemeState.make_meme_send_photo_action.set()
    elif message.text.lower() == 'поддержать':
        await message.answer(text=BEGGER_MODE, reply_markup=make_row_keyboard(available_action))
    elif message.text.lower() == 'чат с разработчиком':
        await message.answer('Вы можете поговорить со мной тут: @Kraigan')
    elif message.text.lower() == 'режим оценки':
        await message.answer('Что надо сделать?', reply_markup=make_row_keyboard(available_action_rating))
    elif message.text.lower() == 'зачем этот бот?':
        await message.answer('¯\_(ツ)_/¯')


async def actions_rating(message: types.Message):
    if message.text.lower() == 'получить мем':
        photo_to_send = await get_photo_from_db(message.from_id)
        await message.answer_photo(open(photo_to_send, mode='rb'))
    elif message.text.lower() == 'рейтинг':
        await message.answer('Ведется работа, зайди позже.')
    elif message.text.lower() == 'назад в меню':
        await message.answer('Отправь фотографию', reply_markup=make_row_keyboard(available_action))


async def make_meme_send_photo(message: types.Message, state: FSMContext):
    if message.photo:
        async with state.proxy() as data:
            data['photo'] = await message.photo[3].get_file()
        await message.answer('Отлично! Теперь напиши что-нибудь!')
        await MakeMemeState.next()
    else:
        await message.answer('Это не фотография, попробуй ещё раз')


async def make_meme_send_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer('Начинаю скрещивать твои запросы!')
    photo_to_send = await edit_this_photo(data['photo'], data['text'])
    await message.answer_photo(open(photo_to_send, 'rb'))
    await message.answer(f'Вот твой мем с надписью "{data["text"]}"',
                         reply_markup=make_row_keyboard(available_action))
    pathlib.Path(photo_to_send).unlink()
    await ChatInPrivate.actions_action.set()


async def get_photo(message: types.Message):
    '''Здесь принимается фотография от пользователя'''
    if message.from_id == message.chat.id:
        photo_from_user = await message.photo[3].get_file()
        photo_to_send = await edit_this_photo(photo_from_user)
        await message.answer('Процесс запущен! Боже, что же мы наделали?')
        await message.answer_photo(open(photo_to_send, mode='rb'))
        await save_photo_in_db(photo_to_send, message.from_id)


async def edit_this_photo(photo, text=None):
    '''Функция принимает на вход словарь с информацией о фото пользователя.
       Загружает локально на диск фотографию, обрабатывает, а затем удаляет.'''
    if text:
        text_to_add = text
    else:
        text_to_add = choice(MEMES)
    photo_name = f'bot/photos/{uuid4()}.jpg'
    photo_edit_name = f'bot/photos/after_make - {uuid4()}.jpg'
    await photo.download(photo_name)
    photo = Image.open(photo_name)
    photo_edit = ImageDraw.Draw(photo)
    font_size = (photo.width // len(text_to_add)) * 2 - 5  # подбираем наиболее подходящий размер текста
    font = ImageFont.truetype('bot/fonts/Lobster-Regular.ttf', font_size)
    x, y = photo.width // 2, photo.height - 30  # рассчитываем расположение текста.
    photo_edit.text(text=text_to_add, xy=(x, y), font=font, fill='black', anchor='ms')  # добавляем тень тексту.
    photo_edit.text(text=text_to_add, xy=(x, y + 2), font=font, fill='white', anchor='ms')
    photo.save(photo_edit_name)
    pathlib.Path(photo_name).unlink()
    return photo_edit_name


async def save_photo_in_db(photo_path: str, user_id: int):
    '''Сохраняет обработанную фотографию в базу данных.'''
    async with async_session() as session:
        new_photo = Photo(photo_path=photo_path, user_create_id=user_id)
        session.add(new_photo)
        await session.commit()
        await session.refresh(new_photo)


async def get_photo_from_db(user_id):
    '''При запросе от пользователя на получение мема
        кидает рандомную фотографию из базы данных.
    '''
    async with async_session() as session:
        query = select(Photo).order_by(func.random())
        result = await session.execute(query)
        file = result.scalar()
        file_path = file.photo_path
        return file_path



def talk_handlers_register(dp: Dispatcher):
    dp.register_message_handler(start_comand, commands='start')
    dp.register_message_handler(actions, Text(equals=available_action,
                                ignore_case=True),
                                state=ChatInPrivate.actions_action)
    dp.register_message_handler(actions_rating, Text(equals=available_action_rating,
                                ignore_case=True),
                                state=ChatInPrivate.actions_action)
    dp.register_message_handler(get_photo, content_types=['photo'], state=ChatInPrivate.actions_action)
    dp.register_message_handler(trash_talk, state=ChatInPrivate.actions_action)


def make_own_mem_handlers_register(dp: Dispatcher):
    dp.register_message_handler(make_meme_send_photo, state=MakeMemeState.make_meme_send_photo_action,
                                content_types=['any'])
    dp.register_message_handler(make_meme_send_text, state=MakeMemeState.make_meme_send_text_action)