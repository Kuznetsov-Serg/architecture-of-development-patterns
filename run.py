from wsgiref.simple_server import make_server

from framework.logging import write_log
from framework.main import Framework
from urls import routes, fronts


application = Framework(routes, fronts)

with make_server('', 8000, application) as httpd:
    write_log("Starting the server on the port 8080...")
    httpd.serve_forever()
