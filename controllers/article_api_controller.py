import json
from controllers.controller import Controller
from models.article import Article
from exceptions import NotFoundExceptions


class ArticlesApiController(Controller):
    def index(self, request, response):
        articles = Article.find_all()
        articles_dict = [article.to_dict() for article in articles]

        response.content_type = 'application/json; charset=utf-8'
        response.text = json.dumps({'articles': articles_dict}, ensure_ascii=False, indent=4)

    def view(self, request, response, id):
        article = Article.get_by_id(id)
        if article is None:
            raise NotFoundExceptions('статья не найдена')

        response.content_type = 'application/json; charset=utf-8'
        response.text = json.dumps({'article': article.to_dict()}, ensure_ascii=False, indent=4)
