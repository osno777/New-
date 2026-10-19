import re
import traceback

from webob import Request, Response
import routes

from whitenoise import WhiteNoise
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from exceptions import NotFoundExceptions
from exceptions import UnauthorizedExpention
from exceptions import ForbiddenException
from views.view import View


SECRET_KEY = "jsdf9jdsf0jsdojfdsojsojdfojsdofj0ue8utyu459y9hd9udf9gdf9yu945ut9u"


class API:
    def __init__(self, static_dir="assets"):
        self.routes = routes.routes
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.serializer = URLSafeTimedSerializer(SECRET_KEY)

    def __call__(self, environ, start_response):
        return self.whitenoise(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def get_session(self, request):
        raw = request.cookies.get('session')
        if not raw:
            return {}
        try:
            return self.serializer.loads(raw, max_age=3600)
        except (BadSignature, SignatureExpired):
            return {}

    def set_session(self, response, data):
        cookie = self.serializer.dumps(data)
        response.set_cookie(
            'session', cookie,
            httponly=True,
            samesite='Lax',
            max_age=3600,
            path='/',
        )

    def render_error(self, controller, template, error):
        """Рендерит страницу ошибки через view контроллера (чтобы был user в шапке)."""
        if controller is not None:
            return controller.view.render_html(template, {'error': error})
        return View("default").render_html(template, {'error': error})

    def handle_request(self, request):
        response = Response()
        controller = None

        request.session = self.get_session(request)
        request.session_dirty = False

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
            response.text = self.render_error(controller, 'errors/404.html', e)

        except UnauthorizedExpention as e:
            response.status_code = 401
            response.text = self.render_error(controller, 'errors/401.html', e)

        except ForbiddenException as e:
            response.status_code = 403
            response.text = self.render_error(controller, 'errors/403.html', e)

        except Exception as e:
            response.status_code = 500
            response.text = "Internal Server Error"
            traceback.print_exc()

        if getattr(request, 'session_dirty', False):
            self.set_session(response, request.session)

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

