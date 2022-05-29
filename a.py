import logging
import time

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests

second = int(time.time())
logging.basicConfig(level=logging.INFO)

bot = Bot(token="5135730638:AAHV9pi647R8BHCtCrh0etRUHbO8G1ulq9g")

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


diction1 = {"English": "en",
            "Русский": "ru",
            "Moscow": "msk",
            "Saint Petersburg": "spb",
            "Москва": "msk",
            "Санкт-Петербург": "spb",
            "0+": 0,
            "6+": "6+",
            "12+": "12+",
            "16+": "16+",
            "Show only free events": True,
            "Show all events": False,
            "Показать только бесплатные события": True,
            "Показать любые события": False}

available_languages = ["English", "Русский"]
available_cities_english = ["Moscow", "Saint Petersburg"]
available_cities_russian = ["Москва", "Санкт-Петербург"]
available_cities = available_cities_russian + available_cities_english
available_ages = ["0+", "6+", "12+", "16+"]
available_costs_english = ["Show only free events", "Show all events"]
available_costs_russian = ["Показать только бесплатные события", "Показать любые события"]
available_answers_russian = ["В избранное", "Дальше"]
available_answers_english = ["To favourites", "Next"]
available_back_keys = ["Back", "Назад"]


class Choices(StatesGroup):
    waiting_for_language = State()
    waiting_for_city = State()
    waiting_for_age = State()
    waiting_for_cost = State()
    waiting_for_likes = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for language in available_languages:
        keyboard.add(language)
    await message.answer("Выберите язык:", reply_markup=keyboard)
    await Choices.waiting_for_language.set()


@dp.message_handler(state=Choices.waiting_for_language)
async def language_chosen(message: types.Message, state: FSMContext):
    if message.text not in available_languages:
        await message.answer("Пожалуйста, выберите язык, используя клавиатуру.")
        return
    await state.update_data(chosen_language=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == "Русский":
        for city in available_cities_russian:
            keyboard.add(city)
        keyboard.add("Назад")
        await message.answer("А теперь выберите город:", reply_markup=keyboard)
        await Choices.next()
    else:
        for city in available_cities_english:
            keyboard.add(city)
        keyboard.add("Back")
        await message.answer("Now select city:", reply_markup=keyboard)
        await Choices.next()


@dp.message_handler(state=Choices.waiting_for_city)
async def city_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['chosen_language'] == "English":
        if message.text == "Back":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for language in available_languages:
                keyboard.add(language)
            await message.answer("Выберите язык:", reply_markup=keyboard)
            await Choices.previous()
            return
        if message.text not in available_cities_english:
            await message.answer("Please, select city using keyboard.")
            return
        await state.update_data(chosen_city=message.text)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for age in available_ages:
            keyboard.add(age)
        keyboard.add("Back")
        await message.answer("Select age limit:", reply_markup=keyboard)
        await Choices.next()
    else:
        if message.text == "Назад":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for language in available_languages:
                keyboard.add(language)
            await message.answer("Выберите язык:", reply_markup=keyboard)
            await Choices.previous()
            return
        if message.text not in available_cities_russian:
            await message.answer("Пожалуйста, выберите город, используя клавиатуру.")
            return
        await state.update_data(chosen_city=message.text)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for age in available_ages:
            keyboard.add(age)
        keyboard.add("Назад")
        await Choices.next()
        await message.answer("Выберите возрастное ограничение:", reply_markup=keyboard)


@dp.message_handler(state=Choices.waiting_for_age)
async def age_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['chosen_language'] == "English":
        if message.text == "Back":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for city in available_cities_english:
                keyboard.add(city)
            keyboard.add("Back")
            await message.answer("Select city:", reply_markup=keyboard)
            await Choices.previous()
            return
        if message.text not in available_ages:
            await message.answer("Please, choose age limit using keyboard.")
            return
        await state.update_data(chosen_age=message.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for cost in available_costs_english:
            keyboard.add(cost)
        keyboard.add("Back")
        await Choices.next()
        await message.answer("Show only free events?", reply_markup=keyboard)
    else:
        if message.text == "Назад":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for city in available_cities_russian:
                keyboard.add(city)
            keyboard.add("Назад")
            await message.answer("Выберите город:", reply_markup=keyboard)
            await Choices.previous()
            return
        if message.text not in available_ages:
            await message.answer("Пожалуйста, выберите возрастное ограничение, используя клавиатуру.")
            return
        await state.update_data(chosen_age=message.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for cost in available_costs_russian:
            keyboard.add(cost)
        keyboard.add("Назад")
        await Choices.next()
        await message.answer("Показывать только бесплатные события?", reply_markup=keyboard)


@dp.message_handler(state=Choices.waiting_for_cost)
async def cost_chosen(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['chosen_language'] == "English":
        if message.text == "Back":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for age in available_ages:
                keyboard.add(age)
            keyboard.add("Back")
            await message.answer("Select age:", reply_markup=keyboard)
            await Choices.previous()
            return
        if message.text not in available_costs_english:
            await message.answer("Please, select using keyboard. Show only free events?")
            return
        await state.update_data(chosen_cost=message.text)
        user_data = await state.get_data()
        await message.answer("Start searching...", reply_markup=types.ReplyKeyboardRemove())
    else:
        if message.text == "Назад":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for age in available_ages:
                keyboard.add(age)
            keyboard.add("Назад")
            await message.answer("Выберите возрастное ограничение:", reply_markup=keyboard)
            await Choices.previous()
            return
        if message.text not in available_costs_russian:
            await message.answer("Пожалуйста, выберите, используя клавиатуру. Показывать только бесплатные события?")
            return
        await state.update_data(chosen_cost=message.text)
        user_data = await state.get_data()
        await message.answer("Запускаем поиск...", reply_markup=types.ReplyKeyboardRemove())
    arr = list()
    ans = requests.get(
        f'https://kudago.com/public-api/v1.4/events/?lang={diction1[user_data["chosen_language"]]}&page_size=100'
        f'&fields=site_url,age_restriction,is_free,description&expand=&order_by=&text_format=text&ids=&location='
        f'{diction1[user_data["chosen_city"]]}&actual_since={second}&actual_until='
        f'{second}&is_free=&categories=&lon=&lat=&radius=')
    while True:
        for j in ans.json()['results']:
            if j['age_restriction'] == diction1[user_data["chosen_age"]]:
                if diction1[user_data["chosen_cost"]]:
                    if j['is_free'] == 1:
                        arr.append([j['site_url'], j['description']])
                else:
                    arr.append([j['site_url'], j['description']])
        if ans.json()['next'] is None:
            break
        ans = requests.get(ans.json()['next'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_data['chosen_language'] == "English":
        await message.answer(f"City: {user_data['chosen_city']}; Age: {user_data['chosen_age']}")
        for answer in available_answers_english:
            keyboard.add(answer)
        keyboard.add("Back")
    else:
        await message.answer(f"Город: {user_data['chosen_city']}; Возраст: {user_data['chosen_age']}")
        for answer in available_answers_russian:
            keyboard.add(answer)
        keyboard.add("Назад")
    await state.update_data(urls=arr)
    await message.answer(f"{arr[0][1]}\nСсылка:\n{arr[0][0]}", reply_markup=keyboard)
    await state.update_data(it=1)
    await Choices.next()


@dp.message_handler(state=Choices.waiting_for_likes)
async def likes_dislikes(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data['chosen_language'] == "English":
        if message.text == "Next":
            await message.answer(f"{user_data['urls'][user_data['it']][1]}\nСсылка:\n{user_data['urls'][user_data['it']][0]}")
            await state.update_data(it=user_data['it'] + 1)
            if user_data['it'] == len(user_data['urls']) - 1:
                await message.answer("It's all(", reply_markup=types.ReplyKeyboardRemove())
                await state.finish()
            return
        elif message.text == "Back":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for cost in available_costs_english:
                keyboard.add(cost)
            keyboard.add("Back")
            await Choices.previous()
            await message.answer("Show only free events?", reply_markup=keyboard)
    else:
        if message.text == "Дальше":
            await message.answer(f"{user_data['urls'][user_data['it']][1]}\nСсылка:\n{user_data['urls'][user_data['it']][0]}")
            await state.update_data(it=user_data['it']+1)
            if user_data['it'] == len(user_data['urls']) - 1:
                await message.answer("На этом всё(", reply_markup=types.ReplyKeyboardRemove())
                await state.finish()
            return
        elif message.text == "Назад":
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for cost in available_costs_russian:
                keyboard.add(cost)
            keyboard.add("Назад")
            await Choices.previous()
            await message.answer("Показывать только бесплатные события?", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
