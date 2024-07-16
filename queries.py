import psycopg2

# Параметри підключення до бази данних
def get_connection():
    return psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="mysecretpassword",
    host="localhost",  # Або IP адрес вашого Docker контейнера, якщо необхідно
    port="5432"
)

#Функція для повернення правильного статусу
# Клас Enum викликає помилку при створенні роздільної строки як для 'in progress'
# можна використовувати для передачі параметра як стро'in progress', отримаємо коректний статус 'in_progress'
def get_valable_status(status):
    return status.replace(' ', '_')

# Функція для повернення всіх користувачів 
def all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users;
    """)

    results = cursor.fetchall()
    for row in results:
        print(row)

    cursor.close()
    conn.close()

# Функція що повертає задачі для користувача по його id
def select_task_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM tasks WHERE user_id = %s
''', (user_id,))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Функція повертає задачі по статусу 
def select_tasks_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()

#Ось приклад використання раніше описаної функції
#Якщо status передати як 'in progress' то без цієї функції повернеться виключення тому що такий статус буде не знайено
# Це не обов‘язкова функція, але добавив її для зручності
    status = get_valable_status(status)

    cursor.execute('''
    SELECT title FROM tasks 
    JOIN status ON tasks.status_id = status.id
    WHERE status.name = %s
    ''', (status, ))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Функція для змінення статусу для задачі
# Передеється назва задачі для якої потрібно змінити статус та статус на який потрібно змінити задачу
def update_status_by_task(title_task, status):
    conn = get_connection()
    cursor = conn.cursor()

    status = get_valable_status(status)
# status_id буде дорівнювати id статусу відповідно до назви статусу
    cursor.execute('''
    UPDATE tasks
    SET status_id = (SELECT id FROM status WHERE name = %s) 
    WHERE title = %s
''', (status, title_task))
    print(f'{title_task} is updated in status {status}')
    conn.commit()
    cursor.close()
    conn.close()

# Функція для повернення всіх задач та їх статусів для первного користувача по його id
def get_all_status_for_task(user):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT tasks.title, status.name
        FROM tasks
        JOIN status ON tasks.status_id = status.id
        WHERE tasks.user_id = %s;
        ''', (user,))
    results = cursor.fetchall()

    # Прінт результатів
    for row in results:
        print(f"Task: {row[0]}, Status: {row[1]}")

    cursor.close()
    conn.close()

# Функція для пошуку користувачів без задач
def get_user_without_tasks():
    conn = get_connection()
    cursor = conn.cursor()
# Запит виводить користувача якщо його id не знаходиться в таблиці задач по user_id 
    cursor.execute('''
        SELECT * FROM users 
        WHERE users.id NOT IN(SELECT tasks.user_id FROM tasks)''')
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

# Функція для добавлення нової задачі для користувача по його id
def new_task_for_user(title, description, user, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tasks (title, description, user_id, status_id) VALUES (%s, %s, %s, %s)
''', (title, description, user, status))

    conn.commit()
    cursor.close()
    conn.close()

# Функція робить те ж саме, але без опису задачі
# Ніяк не міг вирішити чи потрібна вона адже в попередню можна на місце опису передати None, але вирішив залишити  
def new_task_for_user_without_description(title, user, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO tasks (title, user_id, status_id) VALUES (%s, %s, %s)
''', (title, user, status))

    conn.commit()
    cursor.close()
    conn.close()

#Функція повертає всі незавершені задачі, тобто задачі в яких індекс не дорівнює 3(саме під таким індексом зберігаються всі завершені задачі)
def get_dont_completed_tasks_for_user(user):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM tasks WHERE status_id != 3 AND user_id = %s
''', (user, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

# Видалення задачі по її індексу
def delete_task_for_user(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))

    conn.commit()
    cursor.close()
    conn.close()

#Пошук користувачів по електроній пошті 
def select_users_by_email(exampl_email):
    conn = get_connection()
    cursor = conn.cursor()

    pattern = f'%@{exampl_email}.%' # Приклад електронної пошти в яку передається строка 
    cursor.execute('SELECT * FROM users WHERE email LIKE %s', (pattern, )) # В запиті вже використовується готова строка електронної пошти після LIKE
    result = cursor.fetchall()

    cursor.close()
    conn.close()    
    return result

# Функція для зміни повного імені користувача
def update_fullname_user(user_id, fullname):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users
        SET fullname = %s
        WHERE id = %s
''', (fullname, user_id))
    
    conn.commit()
    cursor.close()
    conn.close()

# Функція для підрахунку всіх задач по статусу 
def group_by_status():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''SELECT status.name, COUNT(*) FROM tasks
                   JOIN status ON tasks.status_id = status.id
                   GROUP BY status.name''')

    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

# Функція повертає всі задачі для користувачів з певною електронною поштою
def get_tast_for_user_order_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    pattern = f'%@{email}'
    cursor.execute('''
        SELECT * FROM tasks
        JOIN users ON tasks.user_id = users.id
        WHERE users.email LIKE %s
''', (pattern,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

# Функція для повернення задач без опису 
def get_task_whitout_description():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tasks WHERE description IS NULL')

    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

#Функція для повернення користувача, задачі та статусу 
def get_users_and_tasks_order_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()

    status = get_valable_status(status)

    cursor.execute("""
        SELECT users.fullname, tasks.title, status.name FROM tasks
        INNER JOIN users ON tasks.user_id = users.id
        INNER JOIN status ON tasks.status_id = status.id
        WHERE status.name = %s
""", (status, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

# Функція для підрахунку кількості задач для кожного користувача
def get_users_group_by_count_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT fullname, COUNT(*) AS count_task FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
        GROUP BY fullname
        ''')
    
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result
