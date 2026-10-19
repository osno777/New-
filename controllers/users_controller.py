import re
from controllers.controller import Controller
from models.user import User
from exceptions import InvalidArgumentException
from models.user_auth_service import UserAuthService


class UsersController(Controller):
    
    def index(self, request, response):
        # Получаем всех пользователей из БД
        users = User.find_all()
        response.text = self.view.render_html('users/index.html', {
            'title': 'MVC фреймворк - Пользователи',
            'h1': 'Все пользователи',
            'users': users,
        })

    def sign_up(self, request, response):
        if request.method == 'POST':
            try:
                user = User.sign_up(request.POST)
                if isinstance(user, User):
                    response.text = self.view.render_html('users/singupsuccess.html')
                    return
            except InvalidArgumentException as e:
                response.text = self.view.render_html('users/sign_up.html', {'title': 'MVC фреймворк - Регистрация', 'user_data': request.POST, 'error': e})
                return
        
        response.text = self.view.render_html('users/sign_up.html', {'title': 'MVC фреймворк - Регистрация'})

    def sign_in(self, request, response):
        if request.method == 'POST':
            try:
                user = User.sign_in(request.POST)
                if isinstance(user, User):
                    token = UserAuthService.create_token(user)
                    response.set_cookie('token', token, 500, '/', False, httponly=True)
                    response.status_code = 302
                    # ЖЕСТКО задаем порт 8082 для редиректа
                    response.location = 'http://ilovekasumics.ru:8082/articles'
                    return
            except InvalidArgumentException as e:
                response.text = self.view.render_html('users/sign_in.html', {'title': 'MVC фреймворк - Вход', 'user_data': request.POST, 'error': e})
                return
        response.text = self.view.render_html('users/sign_in.html', {'title': 'MVC фреймворк - вход'})

    def logout(self, request, response):
        response.set_cookie('token', '', -1, '/')
        response.status_code = 302
        response.location = request.referer
