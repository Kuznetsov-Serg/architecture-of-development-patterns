from datetime import date
from views import *


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

routes = {
    '/': Index(),
    '/index/': Index(),
    '/about/': About(),
    '/course-list/': CourseList(),
    '/course-create/': CourseCreate(),
    '/course-copy/': CourseCopy(),
    '/course-select/': CourseListForSelect(),
    '/course-add-student/': CourseAddStudent(),
    '/category-create/': CategoryCreate(),
    '/category-list/': CategoryList(),
    '/student-list/': StudentList(),
    '/student-create/': StudentCreate(),
    '/student-course-list/': StudentCourseList(),
    '/contact/': Contact(),
}
