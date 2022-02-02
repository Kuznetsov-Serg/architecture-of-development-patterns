import sqlite3
from sqlite3 import Error
from .logger import Logger



logger = Logger('db_util', is_debug_console=True)


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logger.debug(f'Connection to SQLite DB successful (path={path})')
    except Error as e:
        logger.error(f"The error '{e}' occurred")

    return connection


def create_or_open_db(path):
    """ Opening or creating a database, if not created """

    logger.debug(f'Opening or creating a database')
    connection = create_connection(path)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS category (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL
                            );'''
                   )
    cursor.execute('''CREATE TABLE IF NOT EXISTS course (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL,
                            category_id INTEGER NOT NULL,
                            FOREIGN KEY (category_id)
                                REFERENCES category (id)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE
                            );'''
                   )
    cursor.execute('''CREATE TABLE IF NOT EXISTS student (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL
                            );'''
                   )
    connection.commit()
    fill_db(connection)

    return connection


def fill_db(connection):
    """ Filling the database with data, if not already filled in """

    logger.debug('Filling the database with data, if not already filled in')
    cursor = connection.cursor()

    if not is_have_records(connection, 'category'):
        category = [(1, 'Категория интерактивных курсов'), (2, 'WEB-категория')]
        cursor.executemany("INSERT INTO category VALUES (?, ?)", category)

    if not is_have_records(connection, 'student'):
        student = [(1, 'Иванов Иван Иванович'), (2, 'Сидоров Петр Семенович')]
        cursor.executemany("INSERT INTO student VALUES (?, ?)", student)

    if not is_have_records(connection, 'course'):
        category_records = get_records(connection, 'category')
        course = [
                    (1, 'Перспектива программирования', category_records[0][0]),
                    (2, 'Программируем на ...', category_records[0][0]),
                    (3, 'Приложения для ...', category_records[0][0]),
                    (4, 'WEB для всех', category_records[1][0]),
        ]
        cursor.executemany("INSERT INTO course VALUES (?, ?, ?)", course)

    connection.commit()


def get_records(connection, table_name):
    """ Getting records from the database by table name """

    logger.debug(f'Getting records from table {table_name}')
    cursor = connection.cursor()
    sql = f'SELECT * FROM {table_name}'
    result = cursor.execute(sql)
    records = result.fetchall()
    # let's tie the names of the fields to their values
    result_list = [{key: val for key, val in zip([el[0] for el in result.description], obj)} for obj in records]
    return result_list


def is_have_records(connection, table_name):
    """ The table has entries """

    cursor = connection.cursor()
    sql = f'SELECT COUNT(*) FROM {table_name}'
    result = cursor.execute(sql)
    records = result.fetchall()
    if len(records):
        logger.debug(f'Table {table_name} has a records')
        return True
    else:
        logger.debug(f'Table {table_name} hasn`t a records')
        return False

