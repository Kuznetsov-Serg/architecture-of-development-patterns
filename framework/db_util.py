import sys
import sqlite3
from .logger import Logger

# sys.path.append('../')
# from patterns.сreational_patterns import Student




logger = Logger('db_util', is_debug_console=True)


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        logger.debug(f'Connection to SQLite DB successful (path={path})')
    except sqlite3.Error as e:
        logger.error(f"The error '{e}' occurred")

    return connection


def create_or_open_db(path):
    """ Opening or creating a database, if not created """

    logger.debug(f'Opening or creating a database')
    connection = create_connection(path)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS category (
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL,
                            category_id INTEGER,
                            FOREIGN KEY (category_id)
                                REFERENCES category (id)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS student_course (
                            student_id INTEGER,
                            course_id INTEGER,
                            FOREIGN KEY (course_id)
                                REFERENCES course (id)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE,
                            FOREIGN KEY (student_id)
                                REFERENCES student (id)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE
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
        category = [(1, 'Категория интерактивных курсов', 0), (2, 'WEB-категория', 0), (3, 'Категория Python-практика', 1)]
        cursor.executemany("INSERT INTO category VALUES (?, ?, ?)", category)

    if not is_have_records(connection, 'student'):
        student = [(1, 'Иванов Иван Иванович'), (2, 'Сидоров Петр Семенович')]
        cursor.executemany("INSERT INTO student VALUES (?, ?)", student)

    if not is_have_records(connection, 'course'):
        category_records = get_records(connection, 'category')
        course = [
                    (1, 'Перспектива программирования', category_records[0]['id']),
                    (2, 'Программируем на ...', category_records[0]['id']),
                    (3, 'Приложения для ...', category_records[0]['id']),
                    (4, 'WEB для всех', category_records[1]['id']),
                    (5, 'Python forever!!!', category_records[2]['id']),
        ]
        cursor.executemany("INSERT INTO course VALUES (?, ?, ?)", course)

    if not is_have_records(connection, 'student_course'):
        category_records = get_records(connection, 'student_course')
        student_course = [(1, 1), (1, 2), (2, 5)]
        cursor.executemany("INSERT INTO student_course VALUES (?, ?)", student_course)

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
    if records[0][0]:
        logger.debug(f'Table {table_name} has a records')
        return True
    else:
        logger.debug(f'Table {table_name} hasn`t a records')
        return False


class UniversalMapper:

    def __init__(self, connection, name):
        self.connection = connection
        self.cursor = connection.cursor()
        self.name = name
        self.tablename = self.name.lower()
        self.table_fields = self._get_table_fields()
        # rrr = self.all()
        # ttt = self.find_by_id(1)
        # kkk = self.insert({'name': 'Сидоров'})
        # ddd = self.update({'id': 1, 'name': 'Petrov333'})

    def all(self):
        sql = f'SELECT * from {self.tablename}'
        result = self.cursor.execute(sql)
        records = result.fetchall()
        # let's tie the names of the fields to their values
        result_list = [self._to_dict_with_fields(item) for item in records]
        return result_list

    def find_by_id(self, id):
        return self.find_by_field('id', id)

    def find_by_field(self, field_name, field_value):
        statement = f"SELECT * FROM {self.tablename} WHERE {field_name}=?"
        self.cursor.execute(statement, (field_value,))
        result = self.cursor.fetchone()
        if result:
            return self._to_dict_with_fields(result)
        else:
            raise RecordNotFoundException(f'record with {field_name}={field_value} not found')

    def filter_by_field(self, field_name, field_value):
        sql = f"SELECT * FROM {self.tablename} WHERE {field_name}=?"
        result = self.cursor.execute(sql, (field_value,))
        records = result.fetchall()
        # let's tie the names of the fields to their values
        result_list = [self._to_dict_with_fields(item) for item in records]
        return result_list

    def insert(self, obj):
        fields_lst = self._get_intersection_fields(obj)
        fields_lst.discard('id')
        values_lst = [obj.__dict__[el] for el in fields_lst] if hasattr(obj, '__dict__') else [obj[el] for el in fields_lst]
        statement = f"INSERT INTO {self.tablename} ({', '.join(fields_lst)}) VALUES ({'?, ' * (len(fields_lst)-1)}?)"
        self.cursor.execute(statement, values_lst)
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        fields_lst = self._get_intersection_fields(obj)
        fields_lst.discard('id')
        values_lst = [obj[el] for el in fields_lst]
        assign_str = '=? , '.join(fields_lst) + '=?'
        statement = f"UPDATE {self.tablename} SET {assign_str} WHERE id=?"
        id = obj.__dict__['id'] if hasattr(obj, '__dict__') else obj['id']
        self.cursor.execute(statement, (*values_lst, id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)

    def _get_table_fields(self):
        statement = f'pragma table_info({self.tablename})'
        self.cursor.execute(statement)
        result = [item[1] for item in self.cursor.fetchall()]
        return result

    def _to_dict_with_fields(self, record_DB):
        return {key: val for key, val in zip(self.table_fields, record_DB)}

    # Python program to get the intersection
    # of two lists using set() and intersection()
    def _get_intersection_fields(self, obj):
        obj_field_lst = obj.__dict__ if hasattr(obj, '__dict__') else dict(obj)
        return set(self.table_fields).intersection(obj_field_lst)



# архитектурный системный паттерн - Data Mapper
class MapperRegistry:

    _mappers = {}  # for pattern Singleton

    def __init__(self, path_DB=None):
        self.path_DB = path_DB if path_DB else 'database/my_database.db'
        self.connection = create_or_open_db(self.path_DB)
        self._mappers = {}

    def get_mapper_by_obj(self, obj):
        name = obj.__name__ if hasattr(obj, '__name__') else obj.__class__.__name__
        return self.get_mapper_by_name(name)

    def get_mapper_by_name(self, name):
        if name not in self._mappers:
            self._mappers[name] = UniversalMapper(self.connection, name)
        return self._mappers[name]


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')

