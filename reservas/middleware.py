class SubdominioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        partes = host.split('.')

        # localhost o dominio normal
        if len(partes) < 2:
            request.subdominio = None
        else:
            request.subdominio = partes[0]

        response = self.get_response(request)
        return response