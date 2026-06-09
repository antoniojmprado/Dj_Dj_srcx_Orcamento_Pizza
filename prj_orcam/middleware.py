from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Se o usuário já está autenticado, segue o fluxo normal
        if request.user.is_authenticated:
            return self.get_response(request)

        # 2. Descobre o 'name' da rota que o usuário está tentando acessar
        try:
            current_url_name = resolve(request.path_info).url_name
        except:
            current_url_name = None

        # 3. Lista de exceções (rotas que NÃO precisam de login)
        # Usamos 'login' porque está definido como LOGIN_URL = 'login' no seu settings
        rotas_publicas = ['login']

        # 4. Se o usuário for anônimo e a rota não for pública, barra e manda pro login
        if current_url_name not in rotas_publicas and request.path != settings.LOGIN_URL:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)