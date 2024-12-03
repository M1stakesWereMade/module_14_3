from aiogram import Bot, Dispatcher, executor, types 
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button2 = KeyboardButton(text='Расчитать')
button = KeyboardButton(text='Информация')
button_buy = KeyboardButton(text='Купить')
kb.add(button2)
kb.add(button)
kb.add(button_buy)

inline_kb = InlineKeyboardMarkup(4)
button_product1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
button_product2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
button_product3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
button_product4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
inline_kb.add(button_product1, button_product2, button_product3, button_product4)

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Информация')
async def inform(message: types.Message):
    await message.answer('Информация о боте!')

@dp.message_handler(text='Расчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)

@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    products = [
        {'name': 'Продукт 1', 'description': 'Описание 1', 'price': 100, 'image': 'img/card_1.jpg'},
        {'name': 'Продукт 2', 'description': 'Описание 2', 'price': 200, 'image': 'img/card_2.jpg'},
        {'name': 'Продукт 3', 'description': 'Описание 3', 'price': 300, 'image': 'img/card_3.jpg'},
        {'name': 'Продукт 4', 'description': 'Описание 4', 'price': 400, 'image': 'img/card_4.jpg'}
    ]
    
    for product in products:
        await message.answer(
            f"Название: {product['name']} | Описание: {product['description']} | Цена: {product['price']} ₽"
        )
        await message.answer_photo(open(product['image'], 'rb'))
    
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_kb)

@dp.callback_query_handler(lambda c: c.data == 'product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    # Подтверждаем покупку
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer(
        "Формула для расчета нормы калорий (Миффлин-Сан Жеор):\n"
        "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
        "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161"
    )

@dp.callback_query_handler(lambda c: c.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Напишите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def calculate_bmr(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = float(data.get('age'))
    growth = float(data.get('growth'))
    weight = float(data.get('weight'))
    
    bmr = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f"Ваша норма калорий: {bmr:.2f} ккал")
    await state.finish()

@dp.message_handler(lambda message: True)
async def all_messages(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
