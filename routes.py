from controllers.sitecontroller import SiteController
from controllers.testcontroller import TestController
from controllers.articlescontroller import ArticlesController
from controllers.users_controller import UsersController
from controllers.article_api_controller import ArticlesApiController

routes = {
    r"^/home$": [SiteController, SiteController.index],
    r"^/article/add$": [ArticlesController, ArticlesController.add],
    r"^/article/(\d+)$": [ArticlesController, ArticlesController.view],
    r"^/article/(\d+)/edit$": [ArticlesController, ArticlesController.edit],
    r"^/article/(\d+)/delete$": [ArticlesController, ArticlesController.delete],
    r"^/articles$": [ArticlesController, ArticlesController.index],
    r"^/user/register$": [UsersController, UsersController.sign_up],
    r"^/user/login$": [UsersController, UsersController.sign_in],
    r"^/user/logout$": [UsersController, UsersController.logout],
    r"^/users$": [UsersController, UsersController.index],
    r"^/about$": [SiteController, SiteController.about],
    r"^test$": [TestController, TestController.test],
    r"^/articles/search$": [ArticlesController, ArticlesController.search],
    r"^/action/(.*)$": [TestController, TestController.action],
    r"^/hello/(.*)$": [SiteController, SiteController.hello],

    # --- API (JSON) ---
    r"^/api/articles$": [ArticlesApiController, ArticlesApiController.index],
    r"^/api/article/(\d+)$": [ArticlesApiController, ArticlesApiController.view],
    
    # --- API Docs (HTML с картинками) ---
    r"^/api-docs$": [SiteController, SiteController.api_docs],
}
