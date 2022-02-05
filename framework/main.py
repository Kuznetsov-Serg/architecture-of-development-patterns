import sys
from quopri import decodestring

sys.path.append('../')
from framework.logger import Logger
from framework.requests import GetRequests, PostRequests


logger = Logger('server', is_debug_console=True)


class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class Framework:
    """Main class Framework"""

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj


    def __call__(self, environ, start_response):
        # the address to which the transition was made
        path = environ['PATH_INFO']

        # adding a closing slash
        if not path.endswith('/'):
            path = f'{path}/'

        request = {}
        # get request method
        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'POST':
            data = PostRequests().get_request_params(environ)
            request['data'] = Framework.decode_dict(data)
            logger.debug(f'{path} POST-request: {Framework.decode_dict(data)}')
        if method == 'GET':
            request_params = GetRequests().get_request_params(environ)
            request['request_params'] = Framework.decode_dict(request_params)
            logger.debug(f'{path} GET-request: {Framework.decode_dict(request_params)}')

        # let's add a request through all Front_Controllers
        for front in self.fronts_lst:
            front(request)

        # chose controller for processing pattern of page
        view = self.routes_lst[path] if path in self.routes_lst else PageNotFound404()
        # starting the controller
        code, body = view(request)
        # code, body = view.__call__(view, request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_dict(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data


# Новый вид WSGI-application.
# Первый — логирующий (такой же, как основной,
# только для каждого запроса выводит информацию
# (тип запроса и параметры) в консоль.
class DebugApplication(Framework):

    # def __init__(self, routes_obj, fronts_obj):
    #     self.application = Framework(routes_obj, fronts_obj)
    #     super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return super().__call__(env, start_response)
        # return self.application(env, start_response)


# Новый вид WSGI-application.
# Второй — фейковый (на все запросы пользователя отвечает:
# 200 OK, Hello from Fake).
class FakeApplication(Framework):

    # def __init__(self, routes_obj, fronts_obj):
    #     self.application = Framework(routes_obj, fronts_obj)
    #     super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']
