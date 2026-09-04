import os
import re
from webob import Request, Response
import routes
import handlers
from whitenoise import WhiteNoise
from exceptions import NotFoundExceptions
from exceptions import UnauthorizedExpention
from views.view import View


class API:
    def __init__(self, static_dir="assets"):
        self.routes = routes.routes
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

    def __call__(self, environ, start_response):
        return self.whitenoise(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()
        
        try:
            result = self.find_handler_re(request_path=request.path)
            
            if result is None:
                raise NotFoundExceptions("Страница не найдена")
            handler, params = result
            controller = handler[0](request)
            action = handler[1]
            action(controller, request, response, *params)

                
        except NotFoundExceptions as e:
            response.status_code = 404
            response.text = View("default").render_html('errors/404.html', {'error': e})

        except UnauthorizedExpention as e:
            response.status_code = 401
            response.text = View("default").render_html('errors/401.html', {'error': e})
        
        return response

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            if path == request_path:
                return handler
        return None

    def find_handler_re(self, request_path):
        for path, handler in self.routes.items():
            match = re.search(path, request_path)
            if match is not None:
                return handler, match.groups()
        return None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found"

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper


app = API()