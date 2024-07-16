from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

class TaskStatus(enum.Enum): # Клас для назв статусів 
    new = 'new'
    in_progress = 'in_progress'
    completed = 'completed'

# URL підключения
DATABASE_URL = 'postgresql://postgres:mysecretpassword@localhost:5432/postgres'
# Створення підключення и бази данних
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Створення моделей
class User(Base):
    __tablename__ = 'users' #Назва таблиці 
    # Стовпці таблиці 
    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    #З‘єднання табліці з таблицею задач для каскадного видалення 
    tasks = relationship('Task', back_populates='owner', cascade='all, delete-orphan')

class Status(Base): # Таблиця статусів
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(TaskStatus), nullable=False, unique=True)

class Task(Base): # Таблиця задач
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False) #З‘єднання з таблицею статусів задач
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False) #З‘єднання з таблицею користувачів з можливістью коскадного видалення 

    owner = relationship('User', back_populates='tasks')
    status = relationship('Status')

# Створення таблиць
Base.metadata.create_all(engine) 

# Створення сесії
Session = sessionmaker(bind=engine)
session = Session()

# Закриття сесії
session.close()


