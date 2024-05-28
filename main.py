import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# Импортируем обученную модель кластеризации
from clsf import TrainerClusterer

# Создаем подключение к базе данных
conn = sqlite3.connect("skylife_bot.db")
cursor = conn.cursor()

# Создаем объект бота
bot = Bot(token="5510823745:AAHz5NxuoIFumCwTEYZK9o6zFUmP-4FOtKM")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# Клавиатура для кнопки "начать"
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_button = KeyboardButton("Начать")
start_keyboard.add(start_button)

clusterer = TrainerClusterer("skylife_bot.db")
clusterer.train_model()


# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        'Привет! Я бот тестирования. Чтобы начать тест, нажмите кнопку "Начать".',
        reply_markup=start_keyboard,
    )


# Обработчик команды /reset
@dp.message_handler(commands=["reset"])
async def reset(message: types.Message):
    user_id = message.from_user.id
    reset_user_answers(user_id)
    await message.answer(
        "Ваши ответы были сброшены. Вы можете начать тест заново, нажав кнопку 'Начать'."
    )


def reset_user_answers(user_id):
    cursor.execute("DELETE FROM user_answers WHERE user_id=?", (user_id,))
    conn.commit()


# Класс состояний для управления процессом тестирования
class TestStates(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()
    Q6 = State()
    Q7 = State()
    Q8 = State()
    Q9 = State()
    Q10 = State()
    Q11 = State()
    Q12 = State()
    Q13 = State()
    Q14 = State()
    Q15 = State()


# Функция для получения вопроса и вариантов ответов из базы данных
def get_question_and_options(question_number):
    cursor.execute("SELECT question_text FROM questions WHERE id=?", (question_number,))
    question_text = cursor.fetchone()[0]
    cursor.execute(
        "SELECT option_text FROM answer_options WHERE question_id=?", (question_number,)
    )
    options = [option[0] for option in cursor.fetchall()]
    return question_text, options


# Обработчик кнопки "начать"
@dp.message_handler(lambda message: message.text == "Начать")
async def start_test(message: types.Message):
    await TestStates.Q1.set()
    await ask_question(message, 1)


# Функция для задания вопроса и вариантов ответов пользователю
async def ask_question(message, question_number):
    question_text, options = get_question_and_options(question_number)
    question_message = f"Вопрос {question_number}: {question_text}\n"
    for i, option in enumerate(options, 1):
        question_message += f"{i}. {option}\n"
    await message.answer(question_message)
    next_state = getattr(TestStates, f"Q{question_number}")
    await next_state.set()


# Обработчики ответов пользователя для каждого вопроса
for question_number in range(1, 16):

    async def answer_qn(message: types.Message, state: FSMContext, num=question_number):
        if message.text.strip().isdigit() and int(message.text.strip()) in range(1, 5):
            # Сохраняем ответ пользователя в базу данных
            cursor.execute(
                "INSERT INTO user_answers (user_id, question_id, answer) VALUES (?, ?, ?)",
                (message.from_user.id, num, int(message.text.strip())),
            )
            conn.commit()  # Обязательно коммитим изменения в базе данных
            await state.update_data({f"question_{num}": int(message.text.strip())})
            if num == 15:
                await save_user_answers(message, state)
                await state.finish()
            else:
                await ask_question(message, num + 1)
        else:
            await message.answer(
                "Пожалуйста, введите номер выбранного вами варианта ответа (от 1 до 4):"
            )

    dp.register_message_handler(
        answer_qn, state=getattr(TestStates, f"Q{question_number}")
    )


# Добавляем метод получения пути к фото тренера
def get_trainer_photo_path(trainer_name):
    photo_path = os.path.join(
        "C:/Users/nikif/Desktop/BOTIC/photo", f"{trainer_name}.jpg"
    )
    return photo_path


async def save_user_answers(message: types.Message, state: FSMContext):
    user_answers = await state.get_data()
    user_responses = [user_answers[f"question_{i}"] for i in range(1, 16)]

    # Предсказываем тренера для ответов пользователя
    trainer_id = clusterer.predict_trainer(user_responses)

    # Получаем имя тренера на основе его ID
    trainer_name = clusterer.get_trainer_name(trainer_id)

    if trainer_name:
        # Получаем путь к фото тренера
        trainer_photo_path = get_trainer_photo_path(trainer_name)

        # Проверяем наличие файла с фото тренера
        if os.path.exists(trainer_photo_path):
            # Загружаем и отправляем фото тренера
            with open(trainer_photo_path, "rb") as photo_file:
                await message.answer_photo(
                    photo_file,
                    caption=f"Вы вылитый - {trainer_name}. Тест завершен. Спасибо за участие!",
                )
        else:
            await message.answer(
                f"Вы схожи с тренером {trainer_name}, но у нас нет его фото."
            )

        # Создаем кнопку "Записаться" с ссылкой
        inline_keyboard = InlineKeyboardMarkup()
        inline_btn = InlineKeyboardButton(
            text="онлайн-запись",
            url="https://b102559.yclients.com/?gcid=2134880398.1683120651",
        )
        inline_keyboard.add(inline_btn)

        # Отправляем сообщение с кнопкой
        await message.answer("Хотите записаться?", reply_markup=inline_keyboard)
    else:
        await message.answer("Не удалось найти подходящего тренера.")


# Обработчик команды /stat
@dp.message_handler(commands=["stat"])
async def show_stat(message: types.Message):
    user_id = message.from_user.id
    user_responses = get_user_responses(user_id)
    if user_responses is None:
        await message.answer(
            "Пожалуйста, пройдите тестирование, чтобы посмотреть статистику."
        )
        return

    # Построение графика
    plot_path = create_plot(user_responses)
    with open(plot_path, "rb") as photo_file:
        await message.answer_photo(photo_file, caption="Ваши ответы и ответы тренеров")


def get_user_responses(user_id):
    cursor.execute(
        "SELECT answer FROM user_answers WHERE user_id=? ORDER BY question_id",
        (user_id,),
    )
    rows = cursor.fetchall()
    if not rows:
        return None
    return [row[0] for row in rows]


def create_plot(user_responses):
    trainer_responses = clusterer.trainer_responses
    trainer_ids = clusterer.trainer_ids

    # Сокращаем данные до первых двух вопросов для простоты визуализации
    user_responses_2d = user_responses[:2]
    trainer_responses_2d = [responses[:2] for responses in trainer_responses]

    # Построение графика
    plt.figure(figsize=(10, 6))
    for i, trainer in enumerate(trainer_responses_2d):
        plt.scatter(
            trainer[0], trainer[1], label=f"Trainer {trainer_ids[i]}", alpha=0.6
        )
    plt.scatter(
        user_responses_2d[0],
        user_responses_2d[1],
        label="User",
        color="red",
        marker="x",
    )
    plt.xlabel("Q1")
    plt.ylabel("Q2")
    plt.legend()
    plt.title("Ответы тренеров и пользователя")

    plot_path = "stat_plot.png"
    plt.savefig(plot_path)
    plt.close()

    return plot_path


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
