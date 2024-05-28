import sqlite3

# Создаем подключение к базе данных
conn = sqlite3.connect("skylife_bot.db")
cursor = conn.cursor()

# Получаем данные об ответах пользователей
cursor.execute("SELECT * FROM user_answers")
user_answers = cursor.fetchall()

# Получаем данные об ответах тренеров
cursor.execute("SELECT * FROM trainer_responses")
trainer_responses = cursor.fetchall()

# Получаем данные об ответах тренеров
cursor.execute("SELECT * FROM questions")
trainer_responses = cursor.fetchall()

# Получаем данные об ответах тренеров
cursor.execute("SELECT * FROM answer_options")
trainer_responses = cursor.fetchall()

# Выводим полученные данные
print("Ответы пользователей:")
for row in user_answers:
    print(row)

print("\nОтветы тренеров:")
for row in trainer_responses:
    print(row)

# Выводим полученные данные
print("Вопросы:")
for row in questions:
    print(row)

# Выводим полученные данные
print("Варианты ответов:")
for row in answer_options:
    print(row)

# Закрываем соединение с базой данных
conn.close()
