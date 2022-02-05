from wsgiref.simple_server import make_server

from framework.logger import Logger
from framework.main import Framework, DebugApplication, FakeApplication
from urls import routes, fronts


logger = Logger('server', is_debug_console=True)
application = Framework(routes, fronts)
# application = DebugApplication(routes, fronts)
# application = FakeApplication(routes, fronts)


with make_server('', 8080, application) as httpd:
    logger.debug("Starting the server on the port 8080...")
    httpd.serve_forever()
