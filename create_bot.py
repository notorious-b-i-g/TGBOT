from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config

bot = Bot(token=config.API_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
