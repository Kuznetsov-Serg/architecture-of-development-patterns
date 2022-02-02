from framework.templator import render
from framework.logger import Logger
from patterns.сreational_patterns import Engine


site = Engine()
logger = Logger('views', is_debug_console=True)


class Index:
    """ Home page controller """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('index.html')


class About:
    """ Controller 'about the project' """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('about.html')


class Contact:
    """ Controller of the 'contacts' page """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('contact.html', date=request.get('date', None))


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


class CategoryCreate:
    """ Controller - create a category """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('category-list.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('category-create.html',
                                    categories=categories)


class CategoryList:
    """ Controller - list of categories """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('category-list.html',
                                objects_list=site.categories)


class StudentList:
    """ Controller - list of Students """
    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return '200 OK', render('student-list.html',
                                objects_list=site.students)


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

