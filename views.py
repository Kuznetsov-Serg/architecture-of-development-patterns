from framework.templator import render
from framework.logger import Logger
from patterns.сreational_patterns import Engine
from patterns.structural_patterns import AppRoute, Debug


site = Engine()
logger = Logger('views', is_debug_console=True)


# @AppRoute(routes=routes, url='/')
# @AppRoute('/')
class Index:
    """ Home page controller """

    @Debug()
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('index.html')


@AppRoute('/about/')
class About:
    """ Controller 'about the project' """

    @Debug()
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('about.html')


# @AppRoute('/contact/')
class Contact:
    """ Controller of the 'contacts' page """

    @Debug()
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('contact.html', date=request.get('date', None))


# @AppRoute('/course-list/')
class CourseList:
    """ Controller - list of courses """

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('course-list.html',
                                    objects_list=category.courses,
                                    name=category.name, id=category.id)
        except KeyError:
            msg = '200 OK', 'No courses have been added yet'
            logger.error(msg)
            return msg


@AppRoute('/student-course-list/')
class StudentCourseList:
    """ controller - list of student courses """

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        try:
            student = site.find_students_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('student-course-list.html',
                                    objects_list=student.courses,
                                    name=student.name, id=student.id)
        except KeyError:
            msg = '200 OK', 'No courses have been added yet'
            logger.error(msg)
            return msg


@AppRoute('/course-select/')
class CourseListForSelect:
    """ Controller - a list of courses to add to the Student """

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        try:
            student = site.find_students_by_id(
                int(request['request_params']['id']))
            objects_list = [el for el in site.courses if el not in student.courses]
            return '200 OK', render('course-list-for-choice.html',
                                    objects_list=objects_list,
                                    name=student.name, id=student.id)
        except KeyError:
            msg = '200 OK', 'No courses have been added yet'
            logger.error(msg)
            return msg


@AppRoute('/course-create/')
class CourseCreate:
    """ Controller - creating a course """
    category_id = -1

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                course = site.create_course('record', name, category)
                site.courses.append(course)

            return '200 OK', render('course-list.html',
                                    objects_list=category.courses,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('course-create.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                msg = '200 OK', 'No courses have been added yet'
                logger.error(msg)
                return msg


# @AppRoute('/student-create/')
class StudentCreate:
    """ Controller - create a student """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            student_id = data.get('student_id')

            student = None
            if student_id:
                student = site.find_students_by_id(int(student_id))

            new_student = site.create_user('student', name)

            site.students.append(new_student)

            return '200 OK', render('student-list.html', objects_list=site.students)
        else:
            students = site.students
            return '200 OK', render('student-create.html',
                                    categories=students)


@AppRoute('/category-create/')
class CategoryCreate:
    """ Controller - create a SubCategory """

    category_id = -1

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None if self.category_id == -1 else site.find_category_by_id(self.category_id)
            new_category = site.create_category(name, category)
            site.categories.append(new_category)

            if category:
                request = {'request_params': {'category_id': category.id}}
            else:
                request = {'request_params': {}}
            return CategoryList.__call__(CategoryList, request)
            # return '200 OK', render('category-list.html', objects_list=site.categories)
        else:
            if ('category_id' in request['request_params']) and request['request_params']['category_id'] not in ('', 'None'):
                self.category_id = int(request['request_params']['category_id'])
                category = site.find_category_by_id(int(self.category_id))
                category_name = category.name
            else:
                category_name = ''
            categories = site.categories

            return '200 OK', render('category-create.html',
                                    categories=categories,
                                    category_name=category_name)


# @AppRoute('/category-list/')
class CategoryList:
    """ Controller - list of categories """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')

        if 'category_id' in request['request_params']:
            category = site.find_category_by_id(int(request['request_params']['category_id']))
            return '200 OK', render('category-list.html',
                                    objects_list=category.categories,
                                    category_name=category.name,
                                    category_id=category.id)
        else:
            # only first level
            objects_list = [el for el in site.categories if el.category == None]
            return '200 OK', render('category-list.html',
                                    objects_list=objects_list)


@AppRoute('/student-list/')
class StudentList:
    """ Controller - list of Students """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('student-list.html',
                                objects_list=site.students)


# @AppRoute('/course-copy/')
class CourseCopy:
    """ Controller - copy course """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        request_params = request['request_params']

        try:
            id = request_params['id']

            old_course = site.get_course_by_id(id)
            if old_course:
                new_course = old_course.clone()
                new_course = site.create_course('record', f'{new_course.name}_copy', old_course.category)
                site.courses.append(new_course)

            return '200 OK', render('course-list.html',
                                    objects_list=new_course.category.courses,
                                    name=new_course.category.name,
                                    id=new_course.category.id)
        except KeyError:
            msg = '200 OK', 'No courses have been added yet'
            logger.error(msg)
            return msg


# @AppRoute('/course-add-student/')
class CourseAddStudent:
    """ Controller - adding a Course to a Student """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        request_params = request['request_params']

        try:
            course_id = request_params['course_id']
            student_id = request_params['student_id']

            student = site.find_students_by_id(int(student_id))
            course = site.get_course_by_id(int(course_id))

            student.courses.append(course)

            return '200 OK', render('student-course-list.html',
                                    objects_list=student.courses,
                                    name=student.name,
                                    id=student.id)

        except KeyError:
            msg = '200 OK', 'No courses have been added yet'
            logger.error(msg)
            return msg
