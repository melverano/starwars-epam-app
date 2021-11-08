import requests
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import Error
import prodenv

# Pull data from API site
people = json.loads(requests.get('https://swapi.dev/api/people').text)['results']
starships = json.loads(requests.get('https://swapi.dev/api/starships').text)['results']

# Заглушки для первоначального создания бд и выгрузки данных
def first_setup_app():
    try:
        create_db(prodenv.db_username, prodenv.db_password, prodenv.db_ip, prodenv.db_port, prodenv.db_name)
    except(Exception, Error) as error:
        pass

    try:
        create_table_starships()
    except(Exception, Error) as error:
        pass

    try:
        create_table_characters()
    except(Exception, Error) as error:
        pass

    try:
        update_starships_table()
    except(Exception, Error) as error:
        pass

    try:
        update_characters_table()
    except(Exception, Error) as error:
        pass


def create_db(user, password, host, port, db_name):
    connection = psycopg2.connect(user=prodenv.db_username,
                                  password=prodenv.db_password,
                                  host=prodenv.db_ip,
                                  port=prodenv.db_port)

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    sql_create_database = 'create database ' + prodenv.db_name
    cursor.execute(sql_create_database)
    cursor.close()
    connection.close()


def create_table_characters():
    connection = False
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        # Создайте курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # SQL-запрос для создания новой таблицы
        create_table_query = '''CREATE TABLE people
                             (ID SERIAL PRIMARY KEY,
                             NAME           TEXT    NOT NULL,
                             GENDER           TEXT    NOT NULL,
                             HOMEWORLD           TEXT    NOT NULL,
                             STARSHIPS           TEXT   ARRAY); '''
        # Выполнение команды: это создает новую таблицу
        cursor.execute(create_table_query)
        connection.commit()
        print("Таблица успешно создана в PostgreSQL - characters")
        cursor.execute('''CREATE UNIQUE INDEX name_idx ON people (NAME);''')
        connection.commit()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def create_table_starships():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        # Создайте курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # SQL-запрос для создания новой таблицы
        create_table_query = '''CREATE TABLE starships
                             (ID SERIAL PRIMARY KEY,
                             NAME           TEXT    NOT NULL,
                             MODEL           TEXT    NOT NULL,
                             MANUFACTURER           TEXT    NOT NULL,
                             CARGO_CAPACITY           REAL,
                             PILOTS           TEXT    ARRAY); '''
        # Выполнение команды: это создает новую таблицу
        cursor.execute(create_table_query)
        connection.commit()
        print("Таблица успешно создана в PostgreSQL - starships")
        cursor.execute('''CREATE UNIQUE INDEX name_s_idx ON starships (NAME);''')
        connection.commit()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def store_characters_to_db():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        # Выполнение SQL-запроса для вставки данных в таблицу
        for each_dict in people:
            cursor.execute(
                """ INSERT INTO people (NAME, GENDER, HOMEWORLD, STARSHIPS) VALUES ('{0}', '{1}', '{2}', ARRAY{3}); """.format(
                    each_dict['name'],
                    each_dict['gender'],
                    json.loads(requests.get(each_dict['homeworld']).text)['name'],
                    [json.loads(requests.get(each_dict['starships'][index]).text)['name'] for index in
                     range(len(each_dict['starships']))] if each_dict['starships'] != [] else ["none"]
                ))

            connection.commit()
            # Получить результат
        cursor.execute("SELECT * from people")
        record = cursor.fetchall()
        print("Результат", record)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def store_starships_to_db():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        # Выполнение SQL-запроса для вставки данных в таблицу
        for each_dict in starships:
            cursor.execute(
                """ INSERT INTO starships (NAME, MODEL, MANUFACTURER, CARGO_CAPACITY, PILOTS) VALUES ('{0}', '{1}', '{2}', '{3}', ARRAY{4}); """.format(
                    each_dict['name'],
                    each_dict['model'],
                    each_dict['manufacturer'],
                    int(each_dict['cargo_capacity']),
                    #                ", ".join([ json.loads(requests.get(each_dict['pilots'][index]).text)['name'] for index in range(len(each_dict['pilots'])) ])
                    [json.loads(requests.get(each_dict['pilots'][index]).text)['name'] for index in
                     range(len(each_dict['pilots']))] if each_dict['pilots'] != [] else ["none"]
                ))
            connection.commit()
            # Получить результат
        cursor.execute("SELECT * from starships")
        record = cursor.fetchall()
        print("Результат", record)

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def pull_data_from_characters():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * from people")
        data = cursor.fetchall()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
    return data


def pull_data_from_starships():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * from starships")
        data = cursor.fetchall()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
    return data


def pull_data_from_starships_ordered():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM starships WHERE PILOTS[1] != 'none' ORDER BY CARGO_CAPACITY DESC")
        data = cursor.fetchall()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
    return data


def update_characters_table():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        # Выполнение SQL-запроса для вставки данных в таблицу
        for each_dict in people:
            cursor.execute(
                """ INSERT INTO people (NAME,GENDER,HOMEWORLD,STARSHIPS) VALUES ('{0}', '{1}', '{2}', ARRAY{3}) ON CONFLICT(NAME) WHERE ((NAME)::text = '{0}'::text) DO UPDATE SET NAME='{0}', GENDER='{1}', HOMEWORLD='{2}', STARSHIPS=ARRAY{3} ; """.format(
                    each_dict['name'],
                    each_dict['gender'],
                    json.loads(requests.get(each_dict['homeworld']).text)['name'],
                    [json.loads(requests.get(each_dict['starships'][index]).text)['name'] for index in
                     range(len(each_dict['starships']))] if each_dict['starships'] != [] else ["none"]
                ))
            connection.commit()
        cursor.execute("SELECT * from people")
        record = cursor.fetchall()
        print("Результат", record)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")


def update_starships_table():
    try:
        # Подключиться к существующей базе данных
        connection = psycopg2.connect(user=prodenv.db_username,
                                      password=prodenv.db_password,
                                      host=prodenv.db_ip,
                                      port=prodenv.db_port,
                                      database=prodenv.db_name)
        cursor = connection.cursor()
        # Выполнение SQL-запроса для вставки данных в таблицу
        for each_dict in starships:
            cursor.execute(
                """ INSERT INTO starships (NAME,MODEL,MANUFACTURER,CARGO_CAPACITY,PILOTS) VALUES ('{0}', '{1}', '{2}', '{3}', ARRAY{4}) ON CONFLICT(NAME) WHERE ((NAME)::text = '{0}'::text) DO UPDATE SET NAME='{0}', MODEL='{1}', MANUFACTURER='{2}', CARGO_CAPACITY='{3}',  PILOTS=ARRAY{4} ; """.format(
                    each_dict['name'],
                    each_dict['model'],
                    each_dict['manufacturer'],
                    int(each_dict['cargo_capacity']),
                    [json.loads(requests.get(each_dict['pilots'][index]).text)['name'] for index in
                     range(len(each_dict['pilots']))] if each_dict['pilots'] != [] else ["none"]
                ))
            connection.commit()
        cursor.execute("SELECT * from starships")
        record = cursor.fetchall()
        print("Результат", record)
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")
