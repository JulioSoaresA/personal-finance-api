import os

import jwt
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from jwt import InvalidTokenError


class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/" and not self._is_authenticated(request):
            return redirect(reverse("login"))

        response = self.get_response(request)
        return response

    def _is_authenticated(self, request):
        token = request.COOKIES.get("access_token")
        if token:
            try:
                jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                return True
            except InvalidTokenError:
                return False
        return request.user.is_authenticated


class IPAllowlistMiddleware:
    """
    Bloqueia requisições de IPs não autorizados com HTTP 403.
    Ignorado quando DEBUG=True (desenvolvimento local).
    Suporta IPs exatos e notação CIDR via variável ALLOWED_CLIENT_IPS (CSV).
    Exemplo: ALLOWED_CLIENT_IPS="187.19.252.14,2804:29b8:50c6:a595::/64"
    """

    def __init__(self, get_response):
        import ipaddress

        self.get_response = get_response
        self.allowed_networks = []
        for entry in os.getenv("ALLOWED_CLIENT_IPS", "").split(","):
            entry = entry.strip()
            if not entry:
                continue
            try:
                self.allowed_networks.append(
                    ipaddress.ip_network(entry, strict=False)
                )
            except ValueError:
                pass  # entrada inválida ignorada silenciosamente

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)

        if self.allowed_networks:
            ip = self._get_client_ip(request)
            if not self._is_allowed(ip):
                return HttpResponseForbidden(
                    f"403 Forbidden — IP {ip!r} não autorizado."
                )

        return self.get_response(request)

    def _is_allowed(self, ip_str: str) -> bool:
        import ipaddress

        try:
            addr = ipaddress.ip_address(ip_str)
            return any(addr in net for net in self.allowed_networks)
        except ValueError:
            return False

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
