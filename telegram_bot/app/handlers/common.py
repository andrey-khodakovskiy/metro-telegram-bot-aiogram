from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext


async def cmd_exit(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    await message.answer(
        "Спасибо, что воспользовались ботом!", reply_markup=types.ReplyKeyboardRemove()
    )
    await message.answer("/start")


async def exit_station_get_callback(
    call: types.CallbackQuery, state: FSMContext
) -> None:
    await call.answer()
    await cmd_exit(message=call.message, state=state)


def register_handlers_common(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_exit, commands="exit", state="*")
    dp.register_callback_query_handler(
        exit_station_get_callback, text="exit", state="*"
    )
