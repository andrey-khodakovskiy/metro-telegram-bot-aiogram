from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import requests
import logging
from string import capwords
from typing import List, Set, Dict, Tuple, Union, Any
from decouple import config


APP_HOST = config("APP_HOST")
APP_PORT = config("APP_PORT")


logger = logging.getLogger("bot-conversation")
logger.setLevel(logging.INFO)
logfile = logging.FileHandler("logs/conversation.log")
logfile.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%d-%b-%Y %H:%M:%S"
)
logfile.setFormatter(formatter)
logger.addHandler(logfile)


def stations_choise_keyboard(stations: List[str]) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    reply_keyboard = [
        types.InlineKeyboardButton(text=capwords(item), callback_data=item)
        for item in stations
    ]
    markup.add(*reply_keyboard)

    return markup


async def update_message_text(
    message: types.Message, direction: str, state: FSMContext
) -> None:
    user_data = await state.get_data()
    text = f"ОТ: {capwords(user_data['start_station'])}"
    markup = types.InlineKeyboardMarkup()

    if direction == "ДО":
        text += f"\nДО: {capwords(user_data['finish_station'])}"
        markup.add(
            types.InlineKeyboardButton(
                text="Найти путь", callback_data="start calculation"
            )
        )

    await message.edit_text(text, reply_markup=markup)


class CalculatePath(StatesGroup):
    waiting_for_start_station = State()
    waiting_for_finish_station = State()
    waiting_for_path_calculation = State()


async def start_station(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    reply_keyboard = [["/restart", "/exit"]]
    markup = types.ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await message.answer("Введите название начальной станции:", reply_markup=markup)
    await CalculatePath.waiting_for_start_station.set()


async def restart_station_get_callback(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.answer()
    await start_station(message=call.message, state=state)


async def start_station_get_message(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    input_request = {"station": message.text.lower()}
    r = requests.get(f"http://{APP_HOST}:{APP_PORT}/input_check", params=input_request)
    stations = r.json()

    if not stations:
        await message.answer("Название станции введено неверно. Попробуйте еще раз.")

    elif len(stations) > 1:
        markup = stations_choise_keyboard(stations)
        await message.answer(
            "Название станции введено не полностью. Доступны следующие варианты:",
            reply_markup=markup,
        )

    else:
        await state.update_data(start_station=stations[0])
        user_data = await state.get_data()
        await message.answer(f'ОТ: {capwords(user_data["start_station"])}')

        await message.answer("Введите название конечной станции:")
        await CalculatePath.waiting_for_finish_station.set()


async def start_station_get_callback(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await state.update_data(start_station=call.data)
    user_data = await state.get_data()
    await update_message_text(call.message, direction="ОТ", state=state)

    await call.message.answer("Введите название конечной станции:")
    await CalculatePath.waiting_for_finish_station.set()
    await call.answer()


async def finish_station_get_message(message: types.Message, state: FSMContext) -> None:
    logger.info(
        f"'{message.text}' от {message.from_user.full_name} ({message.from_user.username} id: {message.from_user.id})"
    )
    input_request = {"station": message.text.lower()}
    r = requests.get(f"http://{APP_HOST}:{APP_PORT}/input_check", params=input_request)
    stations = r.json()

    if not stations:
        await message.answer("Название станции введено неверно. Попробуйте еще раз.")

    elif len(stations) > 1:
        markup = stations_choise_keyboard(stations)
        await message.answer(
            "Название станции введено не полностью. Доступны следующие варианты:",
            reply_markup=markup,
        )

    else:
        await state.update_data(finish_station=stations[0])
        user_data = await state.get_data()
        text = f"ОТ: {capwords(user_data['start_station'])}"
        text += f"\nДО: {capwords(user_data['finish_station'])}"

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                text="Найти путь", callback_data="start calculation"
            )
        )

        await message.answer(text, reply_markup=markup)
        await CalculatePath.waiting_for_path_calculation.set()


async def finish_station_get_callback(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await state.update_data(finish_station=call.data)
    user_data = await state.get_data()
    await update_message_text(call.message, direction="ДО", state=state)

    await call.answer()
    await CalculatePath.waiting_for_path_calculation.set()


async def path_calculation_get_callback(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    user_data = await state.get_data()
    path_request = {
        "start": user_data["start_station"],
        "finish": user_data["finish_station"],
    }
    r = requests.get(
        f"http://{APP_HOST}:{APP_PORT}/calculate_path", params=path_request
    )
    text = r.json()

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Restart", callback_data="restart"),
        types.InlineKeyboardButton(text="Exit", callback_data="exit"),
    ]
    markup.add(*buttons)
    await call.message.edit_text(text, reply_markup=markup)

    logger.info(
        f"От {user_data['start_station']} до {user_data['finish_station']} {call.from_user.full_name} ({call.from_user.username} id: {call.from_user.id})"
    )
    await call.answer()
    await state.finish()


def register_handlers_main(dp: Dispatcher) -> None:
    dp.register_message_handler(start_station, commands=["start", "restart"], state="*")
    dp.register_callback_query_handler(
        restart_station_get_callback, text="restart", state="*"
    )
    dp.register_message_handler(
        start_station_get_message, state=CalculatePath.waiting_for_start_station
    )
    dp.register_callback_query_handler(
        start_station_get_callback, state=CalculatePath.waiting_for_start_station
    )
    dp.register_message_handler(
        finish_station_get_message, state=CalculatePath.waiting_for_finish_station
    )
    dp.register_callback_query_handler(
        finish_station_get_callback, state=CalculatePath.waiting_for_finish_station
    )
    dp.register_callback_query_handler(
        path_calculation_get_callback,
        text="start calculation",
        state=CalculatePath.waiting_for_path_calculation,
    )
