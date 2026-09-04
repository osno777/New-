from controllers.controller import Controller
from servisec.db import Db

class SiteController(Controller):

    def index(self, request,response):
       
        response.text = self.view.render_html('site/index.html',{'title' : 'MVC фрейворк', 'h1' : 'Главная страница'})

    def about(self, request, response):
        response.text = self.view.render_html('site/about.html',{'title' : 'MVC фрейворк - о нас', 'h1' : 'Страница о нас'})    

    def hello(self,request,response,user_name):
        response.text = self.view.render_html('site/hello.html',{'title' : 'MVC фрейворк - о нас', 'h1' : 'Страница о нас', 'user' : user_name})

                            