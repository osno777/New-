# @app.route("/home")
def home(request,response):
    response.text = "Hello in main page"

# @app.route("/about")
def about(request,response):
    response.text = "Hello in page about"

# @app.route("/articles")
def articles(request,response):
    response.text = "Страница со статьями"
