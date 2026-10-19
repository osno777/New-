from controllers.controller import Controller

class TestController(Controller):

    def test(self, request,response):
        response.text = self.view.render_html('test/test.html',{'title' : 'MVC фрейворк', 'h1' : 'Главная страница'})

    def action(self, request, response):
        response.text = self.view.render_html('test/action.html',{'title' : 'Чота произошло', 'h1' : 'Информация о действии'})   