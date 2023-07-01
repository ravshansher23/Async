import sqlalchemy

print("Версия SQLAlchemy:", sqlalchemy.__version__)

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from variables import *
from datetime import datetime

ENGINE = create_engine(SERVER_DATABASE, echo=False)
# Класс - серверная база данных:
BASE = declarative_base()


class Users(BASE):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_login = Column(DateTime)

    def __init__(self, name):
        self.id = None
        self.name = name
        self.last_login = datetime.now()


class ActiveUsers(BASE):
    __tablename__ = "Active_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id), unique=True)
    user = relationship("Users")
    ip_address = Column(String)
    port = Column(Integer)
    login_time = Column(DateTime)

    def __init__(self, user_id, ip_address, port, login_time):
        self.id = None
        self.user_id = user_id
        self.ip_address = ip_address
        self.port = port
        self.login_time = login_time


class LoginHistory(BASE):
    __tablename__ = "Login_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id))
    user = relationship("Users")
    date_time = Column(DateTime)
    ip = Column(String)
    port = Column(Integer)

    def __init__(self, name, date, ip, port):
        self.id = None
        self.name = name
        self.date_time = date
        self.ip = ip
        self.port = port


class ServerStorage:
    def __init__(self):
        self.ENGINE = create_engine(SERVER_DATABASE, echo=False)
        # Класс - серверная база данных:
        self.BASE = declarative_base()
        BASE.metadata.create_all(ENGINE)

        self.Session = sessionmaker(bind=ENGINE)
        self.Sess_OBJ = self.Session()
        self.Sess_OBJ.query(ActiveUsers).delete()
        self.Sess_OBJ.commit()

    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.Sess_OBJ.query(Users).filter_by(name=username)
        # print(type(rez))
        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if rez.count():
            user = rez.first()
            user.last_login = datetime.now()
        # Если нет, то создаздаём нового пользователя
        else:
            # Создаем экземпляр класса self.AllUsers, через который передаем данные в таблицу
            user = Users(username)
            self.Sess_OBJ.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.Sess_OBJ.commit()

        new_active_user = ActiveUsers(user.id, ip_address, port, datetime.now())
        self.Sess_OBJ.add(new_active_user)

        # и сохранить в историю входов
        # Создаем экземпляр класса self.LoginHistory, через который передаем данные в таблицу
        history = LoginHistory(user.id, datetime.now(), ip_address, port)
        self.Sess_OBJ.add(history)

        # Сохраняем изменения
        self.Sess_OBJ.commit()

    def user_logout(self, username):
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы AllUsers
        user = self.Sess_OBJ.query(Users).filter_by(name=username).first()

        # Удаляем его из таблицы активных пользователей.
        # Удаляем запись из таблицы ActiveUsers
        self.Sess_OBJ.query(ActiveUsers).filter_by(user_id=user.id).delete()

        # Применяем изменения
        self.Sess_OBJ.commit()


    # Функция возвращает список известных пользователей со временем последнего входа.
    def users_list(self):
        query = self.Sess_OBJ.query(
            Users.name,
            Users.last_login,
        )
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращает список активных пользователей
    def active_users_list(self):
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.Sess_OBJ.query(
            Users.name,
            ActiveUsers.ip_address,
            ActiveUsers.port,
            ActiveUsers.login_time
        ).join(Users)
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращающая историю входов по пользователю или всем пользователям
    def login_history(self, username=None):
        # Запрашиваем историю входа
        query = self.Sess_OBJ.query(Users.name,
                                    LoginHistory.date_time,
                                    LoginHistory.ip,
                                    LoginHistory.port
                                    ).join(Users)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(Users.name == username)
        return query.all()

# Отладка
if __name__ == '__main__':
    test_db = ServerStorage()
    # выполняем 'подключение' пользователя
    test_db.user_login('client_1', '192.168.1.4', 8888)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя
    test_db.user_logout('client_1')
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # запрашиваем историю входов по пользователю
    test_db.login_history('client_1')
    # выводим список известных пользователей
    print(test_db.users_list())