from copy import deepcopy
from quopri import decodestring
from framework.db_util import *


# абстрактный пользователь
class User:
    pass


# преподаватель
class Teacher(User):
    pass


# студент
class Student(User):
    auto_id = 0

    def __init__(self, name, id=None):
        Student.auto_id += 1
        self.id = id if id else Student.auto_id
        self.name = name
        self.courses = []

    def course_count(self):
        result = len(self.courses)
        return result


class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, id=None):
        return cls.types[type_](name, id)


# порождающий паттерн Прототип
class CoursePrototype:
    # прототип курсов обучения

    def clone(self):
        return deepcopy(self)


class Course(CoursePrototype):
    auto_id = 0

    def __init__(self, name, category, id=None):
        Course.auto_id += 1
        self.id = id if id else Course.auto_id
        self.name = name
        self.category = category
        self.category.courses.append(self)


# интерактивный курс
class InteractiveCourse(Course):
    pass


# курс в записи
class RecordCourse(Course):
    pass


class CourseFactory:
    types = {
        'interactive': InteractiveCourse,
        'record': RecordCourse
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category, id=None):
        return cls.types[type_](name, category, id)


# категория
class Category:
    auto_id = 0

    def __init__(self, name, category, id=None):
        Category.auto_id += 1
        self.id = id if id else Category.auto_id
        self.name = name
        self.category = category
        self.categories = []
        self.courses = []
        if self.category:
            self.category.categories.append(self)

    @classmethod
    def sub_category_count(cls, category):
        result = len(category.categories)
        for el in category.categories:
            result += cls.sub_category_count(el)

        return result

    @classmethod
    def course_count(cls, category):
        result = len(category.courses)
        for el in category.categories:
            result += cls.course_count(el)

        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.courses = []
        self.categories = []

        connection = create_or_open_db('database/my_database.db')
        categories = get_records(connection, 'category')
        courses = get_records(connection, 'course')
        students = get_records(connection, 'student')
        # connection.close()
        for el in categories:
            category = self.create_category(el['name'], None, el['id'])
            self.categories.append(category)

        for el in courses:
            category = self.find_category_by_id(int(el['category_id']))
            course = self.create_course('record', el['name'], category, el['id'])
            self.courses.append(course)

        for el in students:
            student = self.create_user('student', el['name'], el['id'])
            self.students.append(student)


    @staticmethod
    def create_user(type_, name, id=None):
        return UserFactory.create(type_, name, id)

    @staticmethod
    def create_category(name, category=None, id=None):
        return Category(name, category, id)

    def find_category_by_id(self, id):
        for item in self.categories:
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    def find_students_by_id(self, id):
        for item in self.students:
            if item.id == id:
                return item
        raise Exception(f'Нет студента с id = {id}')

    @staticmethod
    def create_course(type_, name, category, id=None):
        return CourseFactory.create(type_, name, category, id)

    def get_course_by_id(self, id):
        for item in self.courses:
            if item.id == int(id):
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')
