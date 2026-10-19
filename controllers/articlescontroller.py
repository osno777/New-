import os
import secrets

from controllers.controller import Controller
from servisec.db import Db
from models.article import Article
from models.user import User
from exceptions import NotFoundExceptions
from exceptions import UnauthorizedExpention
from exceptions import ForbiddenException
from exceptions import InvalidArgumentException


class ArticlesController(Controller):

    def index(self, request, response):
        articles = Article.find_all()
        response.text = self.view.render_html('articles/index.html', {
            'title': 'MVC фреймворк - статьи',
            'h1': 'Статьи на сайте',
            'articles': articles,
        })

    def view(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundExceptions('статья не найдена')

        user = User.get_by_id(article.get_author_id())

        # может ли текущий юзер редактировать статью (только автор)
        can_edit = (
            self.user is not None
            and article.get_author_id() == self.user.get_id()
        )

        response.text = self.view.render_html('articles/view.html', {
            'title': f'MVC фреймворк - {article.get_name()}',
            'h1': f'Статья:{article.get_name()}',
            'text': f'текст:{article.get_name()}',
            'article': article,
            'can_edit': can_edit,
        })

    # вспомогательный метод: получить form из request
    def _get_form(self, request):
        return request.POST

    # вспомогательный метод: проверить CSRF
    def _check_csrf(self, request, form):
        token_from_form = form.get('csrf_token')
        token_from_sess = request.session.get('csrf_token')
        return token_from_sess and token_from_form == token_from_sess

    # вспомогательный метод: сгенерировать и сохранить токен
    def _issue_csrf(self, request):
        token = secrets.token_urlsafe(32)
        request.session['csrf_token'] = token
        request.session_dirty = True
        return token

    # проверка авторства: только автор статьи может её менять/удалять
    def _check_ownership(self, article):
        if self.user is None:
            raise UnauthorizedExpention('Необходимо авторизоваться')
        if article.get_author_id() != self.user.get_id():
            raise ForbiddenException('Вы не автор этой статьи, редактирование запрещено')

    def edit(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundExceptions('статья не найдена')

        # защита на авторство
        self._check_ownership(article)

        if request.method == "POST":
            form = self._get_form(request)

            if not self._check_csrf(request, form):
                response.status_code = 403
                response.text = 'Forbidden'
                return

            article.set_name(form.get('name'))
            article.set_text(form.get('text'))
            article.save()
            response.status_code = 302
            response.headers = [('Location', f'/article/{article.get_id()}')]
            return

        token = self._issue_csrf(request)
        response.text = self.view.render_html('articles/edit.html', {
            'title': f'Редактирование - {article.get_name()}',
            'article': article,
            'csrf_token': token,
        })

    def delete(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundExceptions('статья не найдена')

        # защита на авторство
        self._check_ownership(article)

        article.delete()
        response.status_code = 302
        response.headers = [('Location', '/articles')]

    def add(self, request, response):
        if self.user is None:
            raise UnauthorizedExpention('Необходимо авторизоваться')

        if request.method == 'POST':
            form = self._get_form(request)

            # CSRF
            if not self._check_csrf(request, form):
                response.status_code = 403
                response.text = 'Forbidden'
                return

            # безопасное чтение полей
            fields = {
                'name': form.get('name'),
                'text': form.get('text'),
            }

            img_file = form.get('img')
            if img_file is None or not getattr(img_file, 'filename', None):
                response.status_code = 400
                response.text = self.view.render_html('articles/add.html', {
                    'title': 'Добавление статьи',
                    'article_data': fields,
                    'error': 'Картинка обязательна',
                    'csrf_token': request.session.get('csrf_token', ''),
                })
                return

            try:
                article = Article.create(fields, img_file, self.user)
                if isinstance(article, Article):
                    response.status_code = 302
                    response.headers = [('Location', '/articles')]
                    return
            except InvalidArgumentException as e:
                response.text = self.view.render_html('articles/add.html', {
                    'title': 'Добавление статьи',
                    'article_data': fields,
                    'error': e,
                    'csrf_token': request.session.get('csrf_token', ''),
                })
                return

        # GET: генерируем токен
        token = self._issue_csrf(request)
        response.text = self.view.render_html('articles/add.html', {
            'title': 'Добавление статьи',
            'csrf_token': token,
        })

    def search(self, request, response):
        if 'q' not in request.GET:
            response.text = self.view.render_html('articles/search.html')
            return
        articles = Article.search_by_name(request.GET['q'])
        response.text = self.view.render_html('articles/search.html', {
            'q': request.GET['q'],
            'articles': articles,
        })
