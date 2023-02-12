import json
from aiogram import executor

from core import dp
from loader import groups_data

async def on_startup(dispatcher):
    print('Бот запустился')


async def on_shutdown(dispatcher):
    data_to_save = json.dumps(groups_data)
    json_table = open("bot\\data\\groups.json", "w")
    json_table.write(data_to_save)
    json_table.close()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup, on_shutdown=on_shutdown)
