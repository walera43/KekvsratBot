import json
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from bot.handlers.groups import group_handlers_register
from bot.handlers.users import (make_own_mem_handlers_register,
                               talk_handlers_register)

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


talk_handlers_register(dp)
make_own_mem_handlers_register(dp)
group_handlers_register(dp)
