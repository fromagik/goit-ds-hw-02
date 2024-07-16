from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
from main import Base, User, Status, Task, TaskStatus  

# Ініціалізація Faker
fake = Faker()

# URL підключення
DATABASE_URL = 'postgresql://postgres:mysecretpassword@localhost:5432/postgres'

# Створення підключення и сессії
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Функція для наданння статусу до задач
def seed_statuses():
    # Перевірка існуючих статусів
    existing_statuses = {status.name.value for status in session.query(Status).all()}
    
    statuses = [TaskStatus.new, TaskStatus.in_progress, TaskStatus.completed]
    for status in statuses:
        if status not in existing_statuses:
            session.add(Status(name=status.value))
    session.commit()

def seed_users():
    # Створення користувача
    for _ in range(10):  # Створюємо 10 користувачів
        user = User(
            fullname=fake.name(),
            email=fake.email()
        ) #Заповнюємо випадковими данними
        session.add(user) # Додаємо користувача в таблицю
    session.commit() # Зберігаємо зміни

def seed_tasks():
    # Получення всіх статусів и користувачів
    statuses = session.query(Status).all()
    users = session.query(User).all()

    # Створення задач
    for _ in range(50):  # Створюємо 50 задач
        task = Task(
            title=fake.sentence(),
            description=fake.text(),
            status_id=random.choice(statuses).id, #Випадково надаємо статус
            user_id=random.choice(users).id # та користувача
        )
        session.add(task) # Додаємо задачу в таблицю
    session.commit()

def print_statuses():
    # Вивід всіх статусів
    statuses = session.query(Status).all()
    print("Statuses:\n")
    for status in statuses:
        print(f"ID: {status.id}, Name: {status.name.value}\n")

def print_users():
    # Вивід всіх користувачів
    users = session.query(User).all()
    print("\nUsers:")
    for user in users:
        print(f"ID: {user.id}, Full Name: {user.fullname}, Email: {user.email}\n")

def print_tasks():
    # Вивід всіх завдань
    tasks = session.query(Task).all()
    print("\nTasks:")
    for task in tasks:
        print(f"ID: {task.id}, Title: {task.title}, Description: {task.description}, Status ID: {task.status_id}, User ID: {task.user_id}")

# Функція для видалення та створення нової таблиці
# Не обов‘язково використовувати, я користувався лише для тесту запитів 
def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    recreate_database()
    # Заповнення таблиць даними
    seed_statuses()
    seed_users()
    seed_tasks()

    # Вивід даних
    print_statuses()
    print_users()
    print_tasks()

    # Закриття сесії
    session.close()


