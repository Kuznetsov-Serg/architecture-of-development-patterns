from framework.templator import render
from framework.db_util import MapperRegistry
from framework.logger import Logger
from patterns.сreational_patterns import Engine
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import *



path_DB = 'database/my_database.db'
site = Engine(path_DB)
logger = Logger('views', is_debug_console=True)
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
mapper_registry = MapperRegistry(path_DB)



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
            objects_list = [site.find_course_by_id(id) for id in student.courses]
            return '200 OK', render('student-course-list.html',
                                    objects_list=objects_list,
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
            objects_list = [el for el in site.courses if el.id not in student.courses]
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


# @AppRoute('/category-list/')
class CategoryList(ListView):
    """ Controller - list of categories """

    queryset = site.categories
    template_name = 'category-list.html'
    category = None

    def get_context_data(self):
        context = super().get_context_data()
        if self.category:
            context['objects_list'] = self.category.categories
            context['category_name'] = self.category.name
            context['category_id'] = self.category.id
        else:
            context['objects_list'] = [el for el in site.categories if el.category == None]

        return context

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        if 'category_id' in request['request_params']:
            self.category = site.find_category_by_id(int(request['request_params']['category_id']))
        else:
            self.category = None

        return super().__call__(request)


@AppRoute('/category-create/')
class CategoryCreate(CreateView):
    """ Controller - create a SubCategory """

    template_name = 'category-create.html'
    redirect_to = CategoryList()
    category = None

    def get_context_data(self):
        context = super().get_context_data()
        if self.category:
            context['category_name'] = self.category.name
        return context

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_category = site.create_category(name, self.category)
        site.categories.append(new_category)

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        if request['method'] != 'POST':
            if ('request_params' in request) \
                    and ('category_id' in request['request_params']) \
                    and request['request_params']['category_id'] not in ('', 'None'):
                category_id = int(request['request_params']['category_id'])
                self.category = site.find_category_by_id(int(category_id))
            else:
                self.category = None

        return super().__call__(request)


@AppRoute('/student-list/')
class StudentList(ListView):
    """ Controller - list of Students """

    template_name = 'student-list.html'
    # queryset = site.students
    # model_name = 'Student'

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return super().__call__(request)

    def get_queryset(self):
        site.students = site.refresh('Student')
        self.queryset = site.students
        return super().get_queryset()


# @AppRoute('/student-create/')
class StudentCreate(CreateView):
    """ Controller - create a student """
    template_name = 'student-create.html'
    redirect_to = StudentList()

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        student = site.create_user('student', name)
        site.students.append(student)

    def __call__(self, request):
        logger.debug(f'Started {self.__doc__} with request={request}')
        return super().__call__(request)


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

            # student.courses.append(course)
            course.add_student(student)
            objects_list = [site.find_course_by_id(id) for id in student.courses]
            return '200 OK', render('student-course-list.html',
                                    objects_list=objects_list,
                                    name=student.name,
                                    id=student.id)

        except KeyError:
            msg = '200 OK', 'No courses have been added yet'
            logger.error(msg)
            return msg


@AppRoute('/api-courses/')
class CourseApi:
    @Debug()
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.courses).save()


@AppRoute('/api-students/')
class StudentApi:
    @Debug()
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.students).save()

